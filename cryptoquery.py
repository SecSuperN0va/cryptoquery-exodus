import requests
from time import sleep
import argparse
import sys
import json
import logging

_logger = logging.getLogger()


class TradeDirection:
    DIR_FRM = 1
    DIR_TO = 2
    DIR_BOTH = 3


class ExodusRoutes(object):
    __PRICING__ = "https://pricing.a.exodus.io"
    __EXCHANGE__ = "https://exchange.exodus.io"

    def _generate_route(self, host, endpoint):
        return '{}/{}'.format(host, endpoint)

    @property
    def endpoint_ticker(self):
        return self._generate_route(self.__PRICING__, "ticker")

    @property
    def endpoint_current_price(self):
        return self._generate_route(self.__PRICING__, "current-price")

    @property
    def endpoint_exchange_pairs(self):
        return self._generate_route(self.__EXCHANGE__, "v2/pairs")


class ExodusQuery(object):
    ALL_SYMBOLS = ["ZRX", "AAVE", "ADT", "ARN", "AION", "AST", "ALGO", "AMB", "APPC", "ANT", "ANTv1", "ARK", "REP",
                   "REPv1", "BAL", "BNT", "BAT", "BNB", "BTC", "BCH", "BTG", "BSV", "BTT", "BFT", "BRD", "SNGLS", "ADA",
                   "LINK", "CND", "CVC", "COMP", "CDAI", "ATOM", "CRO", "CRV", "DAI", "DASH", "MANA", "DCR", "DENT",
                   "DCN", "DGB", "DGD", "DNT", "DOGE", "DRGN", "EDG", "EOS", "ETH", "ETC", "1ST", "FUN", "GUSD", "GVT",
                   "GNO", "GLM", "GNT", "HBAR", "ICX", "RLC", "KIN", "KNC", "LSK", "LTC", "LOOM", "LUN", "MKR", "GUP",
                   "MCO", "MDS", "MLN", "MTL", "MITH", "XMR", "NANO", "XEM", "NEO", "GAS", "NMR", "OMG", "ONT", "ONG",
                   "PAXG", "PAX", "PLR", "POE", "DOT", "POLY", "PPT", "POWR", "QASH", "QTUM", "QSP", "RDN", "RVN",
                   "REN", "REQ", "REV", "RCN", "RVT", "SAI", "SALT", "SAN", "SRM", "SOL", "SX", "SNT", "XLM", "STORJ",
                   "STORM", "STMX", "SUSHI", "SNX", "TAAS", "PAY", "USDT", "XTZ", "TNB", "TRX", "TUSD", "UMA", "UNI",
                   "LEO", "USDC", "VET", "VERI", "VTC", "VTHO", "VIB", "VGX", "WTC", "WAVES", "WAX", "TRST", "WINGS",
                   "WBTC", "XRP", "YFI", "ZEC", "ZIL"]

    def __init__(self, currency="GBP"):
        self.currency = currency
        self.router = ExodusRoutes()
        self.session = None
        self.trade_pairs = []
        self._symbol_price_data = {}

    def __enter__(self):
        _logger.debug("Initialising new Exodus query context")
        self.session = requests.session()
        self.refresh()
        _logger.debug("Initialisation complete")
        return self

    def refresh(self):
        self.trade_pairs = self._get_trade_pairs()
        self._symbol_price_data = self._get_current_symbol_price_data(self.ALL_SYMBOLS)
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.debug("Finalising Exodus query context")
        return

    def _get_trade_pairs(self):
        """
        Query the exchange endpoint to acquire the available trades between symbols.
        :return: list of TradePair objects
        """
        pairs = []
        response = self.session.get(self.router.endpoint_exchange_pairs)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('status', None) == "success":
                for x in response_json.get('data', []):
                    trade_pair = TradePair.pair_from_data(x)
                    pairs.append(trade_pair)
        return pairs

    def _get_current_symbol_price_data(self, symbols_from):
        """
        Query the pricing endpoint to retrieve the current prices of the symbols specified in `symbols_from`.
        :param symbols_from: list(str) specifying the symbols to get price information for.
        :return: dict() containing price information for each symbol.
        """
        assert type(symbols_from) is list
        response = self.session.post(
            self.router.endpoint_current_price,
            json={
                "assets": {
                    "from": symbols_from,
                    "to": [self.currency]
                }
            }
        )
        if not response.status_code == 200:
            return {}
        return response.json()

    @property
    def symbol_price_list(self):
        return [(x, v.get(self.currency)) for (x, v) in self._symbol_price_data.items()]

    def price_from_symbol(self, symbol):
        for s, price in self.symbol_price_list:
            if s == symbol:
                return price
        raise Exception("Could not query price for {} in {}".format(symbol, self.currency))

    def exchange_get_trade_pairs_for_symbol(self, symbol):
        relevant_pairs = []
        for trade_pair in self.trade_pairs:
            if symbol not in [trade_pair.left.symbol, trade_pair.right.symbol]:
                continue
            relevant_pairs.append(trade_pair)
        return relevant_pairs

    def get_available_trades_for_holdings(self, holdings, direction=TradeDirection.DIR_BOTH):
        holdings_available_trades = {}
        for holding_sym, holding_quantity in holdings:
            pairs = self.exchange_get_trade_pairs_for_symbol(holding_sym)

            available_trades = []
            for exchange_pair in pairs:
                if direction != TradeDirection.DIR_BOTH:
                    if direction & TradeDirection.DIR_FRM and exchange_pair.left.symbol != holding_sym:
                        continue
                    if direction & TradeDirection.DIR_TO and exchange_pair.right.symbol != holding_sym:
                        continue
                # otherwise we care about both
                exchange_pair.left.price = self._symbol_price_data.get(exchange_pair.left.symbol, {}).get(self.currency)
                exchange_pair.right.price = self._symbol_price_data.get(exchange_pair.right.symbol, {}).get(self.currency)

                if exchange_pair.conversion_rate == 0 or\
                        exchange_pair.left.price is None or \
                        exchange_pair.right.price is None:
                    continue

                available_trades.append(ActiveTrade(exchange_pair, holding_quantity))

            available_trades.sort(key=lambda x: x.ratio, reverse=True)

            holdings_available_trades[holding_sym] = available_trades

        return holdings_available_trades


class TradeElement(object):

    def __init__(self, symbol, price=0):
        self.symbol = symbol
        self.price = price

    def __repr__(self):
        return "{}({})".format(self.symbol, self.price)


class TradePair(object):

    @classmethod
    def pair_from_data(cls, data):
        pair_left, pair_right = data.get('pair').split("_")
        element_left = TradeElement(pair_left)
        element_right = TradeElement(pair_right)
        conversion_rate = data.get('rate')
        pair = TradePair(element_left, element_right, conversion_rate)
        return pair

    def __init__(self, left_element, right_element, conversion_rate):
        self.left = left_element
        self.right = right_element
        self.conversion_rate = conversion_rate

    @property
    def symbols(self):
        return [self.left.symbol, self.right.symbol]

    def __repr__(self):
        return "{}:{} ({})".format(self.left, self.right, self.conversion_rate)


class ActiveTrade(object):

    def __init__(self, trade_pair, starting_quantity):
        self.trade_pair = trade_pair
        self.starting_quantity = starting_quantity

    @property
    def starting_value(self):
        return self.trade_pair.left.price * self.starting_quantity

    @property
    def final_value (self):
        return self.trade_pair.right.price * (self.starting_quantity * self.trade_pair.conversion_rate)

    @property
    def final_quantity(self):
        return self.starting_quantity * self.trade_pair.conversion_rate

    @property
    def ratio(self):
        return self.final_value / self.starting_value

    @property
    def is_profitable_trade(self):
        return self.ratio > 1.0

    @property
    def is_acceptable_trade(self):
        return 1.0 > self.ratio > 0.9

    @property
    def is_bad_trade(self):
        return not self.is_profitable_trade and not self.is_acceptable_trade

    def __repr__(self):
        return "{} -> {} ({})".format(self.trade_pair.left, self.trade_pair.right, self.ratio)


class TradeChainNode(object):

    def __init__(self, trade_pair=None):
        self.current = trade_pair
        self.parent = None
        self.next = []

    @property
    def length(self):
        return 1 if self.parent is None else 1 + self.parent.length

    @property
    def chain_ratio(self):
        return self.current.ratio * (1 if self.parent is None else self.parent.chain_ratio)

    def get_chain_representation(self, indent=0):
        return "{indent}{current}\n" \
               "{children}".format(indent="\t"*indent, current=self,
                                   children='\n'.join(["{indent}\t\t|---- {child} (chained_ratio:{chained_ratio})".format(
                                       indent="\t"*indent, child=x, chained_ratio=x.chain_ratio) for x in self.next]))

    def get_trade_chains(self):
        chains = []
        if self.next:
            for child in self.next:
                child_chain = [self]
                child_chain.extend(child.get_trade_chains())
                chains.append(child_chain)
        else:
            if self.parent is not None:
                chains.append(self)
            else:
                chains.append([self])
        return chains

    def __repr__(self):
        return repr(self.current)


def display_trade_table(available_trades_for_holdings, max_lines=5, no_header=False):
    for holding_sym, available_trades in available_trades_for_holdings.items():
        if not len(available_trades):
            continue
        if not no_header:
            title_string = "{:5s} | {:8s} | {:32s} | {:8s} | {:32s} | {:20s} | {:34s} | {:34s} ".format(
                "no", "l_sym", "l_price", "r_sym", "r_price", "conv_rate", "value_pre", "value_post")
            _logger.info(title_string)
            _logger.info('-' * len(title_string))
        for i, trade in enumerate(available_trades):
            if max_lines and i == max_lines:
                break

            _logger.info('{:5d} | {:8s} | {:32.25f} | {:8s} | {:32.25f} | {:20.15f} | {:34.25f} | {:34.25f} | {:.10f}'.format(
                i,
                trade.trade_pair.left.symbol,
                trade.trade_pair.left.price,
                trade.trade_pair.right.symbol,
                trade.trade_pair.right.price,
                trade.trade_pair.conversion_rate,
                trade.starting_value,
                trade.final_value,
                trade.ratio
            ))
    return


def expand_chain_tree_branch(query, node, depth=5):
    """
    Take a node and find all profitable next trades
    :param query:
    :param node:
    :param depth:
    :return:
    """
    symbol = node.current.trade_pair.right.symbol
    available_trades = query.get_available_trades_for_holdings([(symbol, 1)], direction=TradeDirection.DIR_FRM)
    trades = available_trades.get(symbol, [])
    for trade in trades:
        if not trade.is_profitable_trade:
            continue
        new_trade_node = TradeChainNode(trade)
        new_trade_node.parent = node
        expand_chain_tree_branch(query, new_trade_node, depth=depth-1)
        node.next.append(new_trade_node)
    return


def produce_chain_tree(query, depth=5):
    trade_chains = []
    if depth:
        for symbol in query.ALL_SYMBOLS:
            available_trades = query.get_available_trades_for_holdings([(symbol, 1)], direction=TradeDirection.DIR_FRM)
            trades = available_trades.get(symbol, [])

            for trade in trades:
                # if trade is approved, then continue the tree
                if not trade.is_profitable_trade:
                    continue

                trade_node = TradeChainNode(trade)
                expand_chain_tree_branch(query, trade_node, depth=depth-1)

                # Only add to the results if the chain has additional entries
                trade_chains.append(trade_node)
    return trade_chains


def handle_generic_query(query):
    return


def handle_holding_query(query, holdings):
    return


class QueryHandlerGeneric:

    @staticmethod
    def handle_query_generic_available_trades(query, holdings, args):
        """
        Display a table of all trades currently available on the Exodus exchange.
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        query_symbols = [args.symbol.upper()] if args.symbol else query.ALL_SYMBOLS
        dummy_holdings = [(x, 1) for x in query_symbols]
        available_trades_for_holdings = query.get_available_trades_for_holdings(dummy_holdings,
                                                                                direction=TradeDirection.DIR_FRM)
        top_trades = []
        for sym, trades in available_trades_for_holdings.items():

            if len(trades):
                if args.top_only:
                    top_trade = top_trades[0]
                    if not args.profitable or top_trade.is_profitable_trade:
                        top_trades.append(top_trade)
                else:
                    for trade in trades:
                        if args.profitable and not trade.is_profitable_trade:
                            continue
                        top_trades.append(trade)
        top_trades.sort(key=lambda x: x.ratio, reverse=True)
        display_trade_table({"": top_trades}, max_lines=args.count)
        return

    @staticmethod
    def handle_query_generic_show_currencies(query, holdings, args):
        """
        Display a full list of currencies, with their associated prices.
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        price_list = query.symbol_price_list
        price_list.sort(key=lambda x: x[1], reverse=args.reverse)
        for i, (symbol, price) in enumerate(price_list):
            if args.count and i >= args.count:
                break
            _logger.info("{}: {}".format(symbol, price))
        return


class QueryHandlerHolding:

    @staticmethod
    def handle_query_holding_value(query, holdings, args):
        """
        Display the sum total of specified holdings at current value according to the Exodus pricing API.
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        total = 0
        for symbol, quantity in holdings:
            price = query.price_from_symbol(symbol)
            value = price * quantity
            total += value
            _logger.info("{}:\t{:.2f} {}".format(symbol, value, query.currency))
        _logger.info("--------------------")
        _logger.info("TOTAL:\t{:.2f} {}".format(total, query.currency))
        _logger.info("--------------------")
        return

    @staticmethod
    def handle_query_holding_top_trades(query, holdings, args):
        """
        Display information on the least-expensive (most-profitable) trades available on the Exodus exchange
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        while True:
            query.refresh()
            available_trades = query.get_available_trades_for_holdings(holdings, direction=TradeDirection.DIR_FRM)
            display_trade_table(available_trades, max_lines=1, no_header=True)
            _logger.info("")
            if not args.watch:
                break
            sleep(2)
        return

    @staticmethod
    def handle_query_holding_available_trades(query, holdings, args):
        """
        Display information on available trades linked to the specified holdings.
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        direction = (TradeDirection.DIR_FRM if args.trades_from else 0) | (TradeDirection.DIR_TO if args.trades_to else 0)
        available_trades_for_holdings = query.get_available_trades_for_holdings(holdings, direction=direction)
        display_trade_table(available_trades_for_holdings, max_lines=args.count)
        return

    @staticmethod
    def handle_query_holding_profitable_trades(query, holdings, args):
        """
        Display information on trades where the resulting value of the destination currency outweighs the value
        of the held currency.
        :param query:
        :param holdings:
        :param args:
        :return:
        """
        direction = (TradeDirection.DIR_FRM if args.trades_from else 0) | (TradeDirection.DIR_TO if args.trades_to else 0)
        held_symbols = [x[0] for x in holdings]

        _logger.info("searching for profitable trades ({})".format("COMPOUND" if args.allow_trade_chains else "SINGLE"))
        tree = produce_chain_tree(query)
        if len(tree):
            if not args.allow_trade_chains:
                # If not showing compounding chains, collate all rows and present together
                collated_chains = []
                for branch in tree:
                    for chain in branch.get_trade_chains():
                        if len(chain) > 1:
                            _logger.debug("skipping compounding chain due to argument selection: {}".format(chain))
                            continue
                        if direction & TradeDirection.DIR_FRM and chain[0].current.trade_pair.left.symbol not in held_symbols:
                            _logger.debug("skipping due to not held origin".format(chain))
                            continue
                        if direction & TradeDirection.DIR_TO and chain[-1].current.trade_pair.right.symbol not in held_symbols:
                            _logger.debug("skipping due to not held destination: {}".format(chain))
                            continue
                        collated_chains.append(chain[0].current)
                collated_chains.sort(key=lambda x: x.ratio, reverse=True)
                display_trade_table({"": collated_chains}, max_lines=args.count)
            else:
                # otherwise, present the chains a separate tables
                collated_compound_chains = []
                for branch in tree:
                    for chain in branch.get_trade_chains():
                        if len(chain) <= 1:
                            continue
                        if direction & TradeDirection.DIR_FRM and chain[0].current.trade_pair.left.symbol not in held_symbols:
                            _logger.debug("skipping due to not held origin".format(chain))
                            continue
                        if direction & TradeDirection.DIR_TO and chain[-1].current.trade_pair.right.symbol not in held_symbols:
                            _logger.debug("skipping due to not held destination: {}".format(chain))
                            continue
                        collated_compound_chains.append(chain)
                collated_compound_chains.sort(key=lambda x: x[-1].chain_ratio, reverse=True)
                for compound_chain in collated_compound_chains:
                    _logger.info("Chain ROI: {}".format(compound_chain[-1].chain_ratio))
                    display_trade_table({"": [x.current for x in compound_chain]}, max_lines=args.count, no_header=True)
        else:
            _logger.info("no profitable trades available at this time.")
        return


def main(argv):
    args = parse_arguments(argv)
    if not hasattr(args, "handler"):
        _logger.warning("no action defined. See --help")
        return

    holdings = list()
    try:
        with open(args.holdings, 'rt') as f_holdings:
            for symbol, quantity in json.load(f_holdings).items():
                holdings.append((symbol, quantity))
    except Exception as e:
        _logger.error("Failed to load holdings from file")
        return

    with ExodusQuery(args.currency.upper()) as query:
        args.handler(query=query, holdings=holdings, args=args)
    return


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("--currency", default="GBP", help="Specify the currency to operate in (default:GBP)")
    parser.add_argument("--holdings", default="holdings.json", help="Specify the path to your holdings.json file (default:holdings.json)")

    context_parser_group = parser.add_subparsers(title="context")
    generic_parser = context_parser_group.add_parser("generic")
    generic_parser.set_defaults(handler=handle_generic_query)
    generic_parser_group = generic_parser.add_subparsers(title="action")

    generic_available_trades_parer = generic_parser_group.add_parser("available-trades")
    generic_available_trades_parer.set_defaults(handler=QueryHandlerGeneric.handle_query_generic_available_trades)
    generic_available_trades_parer.add_argument("-c", "--count", type=int, default=0,
                                                help="specify maximum number of rows to show per currency (default:0 (all))")
    generic_available_trades_parer.add_argument("-s", "--symbol",
                                                help="specify a symbol to show trades for")
    generic_available_trades_parer.add_argument("-t", "--top-only", action="store_true",
                                                help="only show the most profitable trade for each symbol")
    generic_available_trades_parer.add_argument("-p", "--profitable", action="store_true",
                                                help="only show profitable trades")

    generic_prices_parser = generic_parser_group.add_parser("prices")
    generic_prices_parser.set_defaults(handler=QueryHandlerGeneric.handle_query_generic_show_currencies)
    generic_prices_parser.add_argument("-c", "--count", type=int, default=0,
                                                help="specify maximum number of rows to show per currency (default:0 (all))")
    generic_prices_parser.add_argument("-r", "--reverse", action="store_true",
                                                help="reverse the sorting of the price list (high_to_low)")

    holding_parser = context_parser_group.add_parser("holding")
    holding_parser.set_defaults(handler=handle_holding_query)
    holding_parser_group = holding_parser.add_subparsers(title="action")

    holding_value_parser = holding_parser_group.add_parser("value")
    holding_value_parser.set_defaults(handler=QueryHandlerHolding.handle_query_holding_value)

    holding_value_parser = holding_parser_group.add_parser("top-trades")
    holding_value_parser.set_defaults(handler=QueryHandlerHolding.handle_query_holding_top_trades)
    holding_value_parser.add_argument("--watch", action="store_true",
                                      help="Continuously retrieve the best outgoing trades for all held currencies.")

    holding_available_trades_parser = holding_parser_group.add_parser('available-trades')
    holding_available_trades_parser.set_defaults(handler=QueryHandlerHolding.handle_query_holding_available_trades)
    holding_available_trades_parser.add_argument("-c", "--count", type=int, default=0,
                                                 help="specify maximum number of rows to show per currency (default:0 (all))")
    holding_available_trades_parser.add_argument("--trades-from", action="store_true",
                                                 help="show trades from held currencies")
    holding_available_trades_parser.add_argument("--trades-to", action="store_true",
                                                 help="show trades to held currencies")

    holding_profitable_trades_parser = holding_parser_group.add_parser('profitable-trades')
    holding_profitable_trades_parser.set_defaults(handler=QueryHandlerHolding.handle_query_holding_profitable_trades)
    holding_profitable_trades_parser.add_argument("-c", "--count", type=int, default=0,
                                                 help="specify maximum number of rows to show (default:0 (all))")
    holding_profitable_trades_parser.add_argument("--trades-from", action="store_true",
                                                  help="show trades from held currencies")
    holding_profitable_trades_parser.add_argument("--trades-to", action="store_true",
                                                  help="show trades to held currencies")
    holding_profitable_trades_parser.add_argument("--allow-trade-chains", action="store_true",
                                                  help="include chain-trading results")

    return parser.parse_args(argv)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main(sys.argv[1:])