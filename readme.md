# Cryptocurrency Trade Assistant - Exodus

This script helps perform some simple queries on cryptocurrency pricing and exchange rates, 
based on the data provided by the Exodus platform.

# Configuring your holdings
The interface doesn't have a mechanism for querying your crypto balances automatically, so in 
order to perform calculations based on your balance, add each coin and associated balance into
a `holdings.json` file, as follows:

```json
{
  "BTC": 0.0123,
  "ETH": 1.555
}
```

# Usage Information

```
>python cryptoquery.py --help
usage: cryptoquery.py [-h] [--currency CURRENCY] [--holdings HOLDINGS] {generic,holding} ...

optional arguments:
  -h, --help           show this help message and exit
  --currency CURRENCY  Specify the currency to operate in (default:GBP)
  --holdings HOLDINGS  Specify the path to your holdings.json file (default:holdings.json)

context:
  {generic,holding}

```

## Usage Information - generic

```
>python cryptoquery.py generic --help
usage: cryptoquery.py generic [-h] {available-trades,prices} ...

optional arguments:
  -h, --help            show this help message and exit

action:
  {available-trades,prices}
```  
  
```
>python cryptoquery.py generic available-trades --help
usage: cryptoquery.py generic available-trades [-h] [-c COUNT] [-s SYMBOL] [-t] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        specify maximum number of rows to show per currency (default:0 (all))
  -s SYMBOL, --symbol SYMBOL
                        specify a symbol to show trades for
  -t, --top-only        only show the most profitable trade for each symbol
  -p, --profitable      only show profitable trades
```

```
>python cryptoquery.py generic prices --help
usage: cryptoquery.py generic prices [-h] [-c COUNT] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        specify maximum number of rows to show per currency (default:0 (all))
  -r, --reverse         reverse the sorting of the price list (high_to_low)

```

## Usage Information - holding

```
>python cryptoquery.py holding --help
usage: cryptoquery.py holding [-h] {value,top-trades,available-trades,profitable-trades} ...

optional arguments:
  -h, --help            show this help message and exit

action:
  {value,top-trades,available-trades,profitable-trades}

```

```
>python cryptoquery.py holding value --help
usage: cryptoquery.py holding value [-h]

optional arguments:
  -h, --help  show this help message and exit

```

```
>python cryptoquery.py holding top-trades --help
usage: cryptoquery.py holding top-trades [-h] [--watch]

optional arguments:
  -h, --help  show this help message and exit
  --watch     Continuously retrieve the best outgoing trades for all held currencies.
```

```
>python cryptoquery.py holding available-trades --help
usage: cryptoquery.py holding available-trades [-h] [-c COUNT] [--trades-from] [--trades-to]

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        specify maximum number of rows to show per currency (default:0 (all))
  --trades-from         show trades from held currencies
  --trades-to           show trades to held currencies
```

```
>python cryptoquery.py holding profitable-trades --help
usage: cryptoquery.py holding profitable-trades [-h] [-c COUNT] [--trades-from] [--trades-to] [--allow-trade-chains]

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        specify maximum number of rows to show (default:0 (all))
  --trades-from         show trades from held currencies
  --trades-to           show trades to held currencies
  --allow-trade-chains  include chain-trading results
```
# Example - Checking value of holdings

```
>python cryptoquery.py --currency USD holding value
BTG:    4130.71 USD
DOGE:   739.01 USD
--------------------
TOTAL:  4869.71 USD
--------------------
```

# Example - Identifying profitable trades

The following shows all trades into BTG (the held currency) where the ratio between the input and output value is greater than 1.0

```
>python cryptoquery.py holding profitable-trades
searching for profitable trades (SINGLE)
no    | l_sym    | l_price                          | r_sym    | r_price                          | conv_rate            | value_pre                          | value_post
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    0 | BSV      |    247.1422206421336227322171908 | BTG      |     83.4785958993446683962247334 |    3.158666217300000 |      247.1422206421336227322171908 |      263.6810207348983112751739100 | 1.0669201727
    1 | LTC      |    199.4107441776806695088453125 | BTG      |     83.4785958993446683962247334 |    2.541344710900000 |      199.4107441776806695088453125 |      212.1478881621579830607515760 | 1.0638739103
    2 | EOS      |      5.5983291137636825851586764 | BTG      |     83.4785958993446683962247334 |    0.071308636500000 |        5.5983291137636825851586764 |        5.9527448505167592784914632 | 1.0633074136
    3 | ZEC      |    178.0694826536784773907129420 | BTG      |     83.4785958993446683962247334 |    2.266427984200000 |      178.0694826536784773907129420 |      189.1982258279981294890603749 | 1.0624966334
    4 | NEO      |     50.7020693486374867120503040 | BTG      |     83.4785958993446683962247334 |    0.644895369100000 |       50.7020693486374867120503040 |       53.8349599144576274056817056 | 1.0617901913
    5 | BTC      |  45388.3174339999968651682138443 | BTG      |     83.4785958993446683962247334 |  577.059428328799982 |    45388.3174339999968651682138443 |    48172.1108273667414323426783085 | 1.0613328176
    6 | XEM      |      0.3112362050128469337373360 | BTG      |     83.4785958993446683962247334 |    0.003955433300000 |        0.3112362050128469337373360 |        0.3301940180575113625849326 | 1.0609113360
    7 | DASH     |    232.8221982734698372041748371 | BTG      |     83.4785958993446683962247334 |    2.957864824200000 |      232.8221982734698372041748371 |      246.9184023842779538426839281 | 1.0605449318
    8 | BCH      |    601.4627177855201125566964038 | BTG      |     83.4785958993446683962247334 |    7.638189927100000 |      601.4627177855201125566964038 |      637.6253703268257595482282341 | 1.0601245122
    9 | XTZ      |      4.9111646026220459049227429 | BTG      |     83.4785958993446683962247334 |    0.062355529800000 |        4.9111646026220459049227429 |        5.2053520742637440221756151 | 1.0599017739
   10 | DOT      |     31.4372504484725929785327025 | BTG      |     83.4785958993446683962247334 |    0.398844932500000 |       31.4372504484725929785327025 |       33.2950149466688998245444964 | 1.0590943696
   11 | QTUM     |     11.5824333958280671907914439 | BTG      |     83.4785958993446683962247334 |    0.146926550900000 |       11.5824333958280671907914439 |       12.2652221694655967354492532 | 1.0589503734
   12 | XLM      |      0.4558582026218563898467551 | BTG      |     83.4785958993446683962247334 |    0.005782282200000 |        0.4558582026218563898467551 |        0.4826967991497736476524949 | 1.0588748790
   13 | DCR      |    148.1760539330173571670457022 | BTG      |     83.4785958993446683962247334 |    1.878541328800000 |      148.1760539330173571670457022 |      156.8179924671131573177262908 | 1.0583220993
   14 | VET      |      0.1331871815678266901539217 | BTG      |     83.4785958993446683962247334 |    0.001688472800000 |        0.1331871815678266901539217 |        0.1409513385582349953573100 | 1.0582950769
   15 | SOL      |     19.9926483166040860339762730 | BTG      |     83.4785958993446683962247334 |    0.253344195600000 |       19.9926483166040860339762730 |       21.1488177279369331529323972 | 1.0578297279
   16 | XRP      |      1.2540471258036485213693823 | BTG      |     83.4785958993446683962247334 |    0.015889331800000 |        1.2540471258036485213693823 |        1.3264191084428067490819103 | 1.0577107360
   17 | NANO     |      4.0855325159821092029233114 | BTG      |     83.4785958993446683962247334 |    0.051718175500000 |        4.0855325159821092029233114 |        4.3173606732158873455773573 | 1.0567436818
   18 | ADA      |      1.0700583696791903243195065 | BTG      |     83.4785958993446683962247334 |    0.013498517000000 |        1.0700583696791903243195065 |        1.1268372458834343685651902 | 1.0530614757
   19 | DGB      |      0.0724722440132818668256931 | BTG      |     83.4785958993446683962247334 |    0.000912608500000 |        0.0724722440132818668256931 |        0.0761832761858070861560321 | 1.0512062545
   20 | XMR      |    245.3865741952807013603887754 | BTG      |     83.4785958993446683962247334 |    3.088159166500000 |      245.3865741952807013603887754 |      257.7951911331105634417326655 | 1.0505676277
   21 | BNB      |    399.6185401859061698814912234 | BTG      |     83.4785958993446683962247334 |    5.025791673700000 |      399.6185401859061698814912234 |      419.5460322030933753012504894 | 1.0498662850
   22 | TRX      |      0.1170199576781508349343497 | BTG      |     83.4785958993446683962247334 |    0.001470288600000 |        0.1170199576781508349343497 |        0.1227376278948132115598213 | 1.0488606416
   23 | ATOM     |     19.7474609321866765299091639 | BTG      |     83.4785958993446683962247334 |    0.247838124300000 |       19.7474609321866765299091639 |       20.6891786268912518664819800 | 1.0476880394
   24 | GAS      |      9.8090974546970546299462512 | BTG      |     83.4785958993446683962247334 |    0.123044616600000 |        9.8090974546970546299462512 |       10.2715918267411971953606553 | 1.0471495338
   25 | WAVES    |     11.6712312685369585807393378 | BTG      |     83.4785958993446683962247334 |    0.146179392600000 |       11.6712312685369585807393378 |       12.2028504436670548471965958 | 1.0455495365
   26 | ICX      |      1.8598918983512293667814674 | BTG      |     83.4785958993446683962247334 |    0.023256491900000 |        1.8598918983512293667814674 |        1.9414192893564823361174376 | 1.0438344783
   27 | HBAR     |      0.2731487143083807800358898 | BTG      |     83.4785958993446683962247334 |    0.003412775500000 |        0.2731487143083807800358898 |        0.2848937068596839594647463 | 1.0429985277
   28 | ZIL      |      0.1490165549419843749046066 | BTG      |     83.4785958993446683962247334 |    0.001857148000000 |        0.1490165549419843749046066 |        0.1550321074172761603993109 | 1.0403683502
   29 | LSK      |      4.6652130796802397938449758 | BTG      |     83.4785958993446683962247334 |    0.057996093400000 |        4.6652130796802397938449758 |        4.8414324446792500467040554 | 1.0377730582
   30 | RVN      |      0.1568524015342426802810394 | BTG      |     83.4785958993446683962247334 |    0.001944832500000 |        0.1568524015342426802810394 |        0.1623518863594122507709727 | 1.0350615277
   31 | BTT      |      0.0062563769766650987463885 | BTG      |     83.4785958993446683962247334 |    0.000077157400000 |        0.0062563769766650987463885 |        0.0064409914152440961299106 | 1.0295082025
   32 | ONT      |      1.4168811687171862789824672 | BTG      |     83.4785958993446683962247334 |    0.017321433600000 |        1.4168811687171862789824672 |        1.4459689558917310225893971 | 1.0205294472
   33 | ARK      |      1.8582054039588975502539370 | BTG      |     83.4785958993446683962247334 |    0.022690280000000 |        1.8582054039588975502539370 |        1.8941527149629824311460879 | 1.0193451762
   34 | ALGO     |      1.1285097572244193742108109 | BTG      |     83.4785958993446683962247334 |    0.013774379700000 |        1.1285097572244193742108109 |        1.1498658767404363878483764 | 1.0189241780
   35 | DOGE     |      0.0958277377946250424889385 | BTG      |     83.4785958993446683962247334 |    0.001159022400000 |        0.0958277377946250424889385 |        0.0967535625678886124223510 | 1.0096613444
```