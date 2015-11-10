---
title: MC2-Project-2 - Technical Indicators
author: Magahet Mendiola
date: November, 2015
---

## Overview

We will consider the use of technical indicators to signal trade orders. The underlaying assumption is that asset price history can be used to predict future pricing trends.

## Bollinger Bands

As specified in the assignment, the Bollinger Strategy was coded to trigger a buy order when the price moves from below to above the lower band, and a sell order when the price moves from above to below the upper band. Long and short positions are exited when the price crosses the SMA line after entering a buy or sell position.


#### Bollinger Band entry/exit graph

Figure 1 illustrates the Bolliner Strategy, including the 20 day SMA, Bollinger bands, and entry and exit points for buy and sell orders.

![Bollinger Band Strategy](output/bbs.png)

#### Bollinger Band code

The following snippet from the bollinger_strategy.py shows the core logic behind the trading recommendations:

```python
    if is_long_entry() and can_buy():
        return buy()
    elif is_short_entry() and can_sell():
        return sell()
    elif moved_above_sma() and can_exit_long():
        return sell()
    elif moved_below_sma() and can_exit_short():
        return buy()
```

Each boolean function performs the calculations as defined in the strategy specification.

```python
    def is_long_entry():
        return (
            last_price <= self.last_sma - 2 * self.last_std and
            current_price > self.sma - 2 * self.std
        )

    def can_buy():
        return self.current_position < self.long_limit

    def moved_above_sma():
        return last_price <= self.last_sma and current_price > self.sma

    def can_exit_long():
        return self.current_position >= self.long_limit
```

### Performance

#### Bollinger Band strategy performance graph

Figure 2 shows the results of running the Bollinger Strategy orders through the market simulator.

![Bollinger Band Performance](output/bbp.png)


#### Bollinger Band strategy results

The market simulator results show the Bollinger Strategy resulted in a high sharpe ratio, at least for this specific time block. It also significantly outperformed the SPY:

    Data Range: 2007-12-31 to 2009-12-31

    Sharpe Ratio of Fund: 0.97745615082
    Sharpe Ratio of SPY: -0.21996865409

    Cumulative Return of Fund: 0.3614
    Cumulative Return of SPY: -0.240581328829

    Standard Deviation of Fund: 0.0108802922269
    Standard Deviation of SPY: 0.0219524869863

    Average Daily Return of Fund: 0.000669942567631
    Average Daily Return of SPY: -0.000304189525556

    Final Portfolio Value: 13614.0


## Momentum

### Strategy

The basis of this strategy is simply to reduce the daily noise in the asset's pricing and find a long-term trend. My first attempt was to utilize complex smoothing and forecasting methods, such as Kalman and particle filter movement modeling and prediction. These techniques produced mixed results and the added complexity of the models cast doubt on their efficacy. In every case, they were able to provide only a slight improvement on cumulative return, and never an improvement on risk adjusted return.

The next evolution was to try an established momentum indicator, for which I choose TRIX. This is the rate-of-change for a triple smoothed exponential moving average of our asset's daily price. Following the published methodology, I calculated the triple wrapped, 15 day, EMA and took the one day ROC of that value. This resulted in a smooth trend-line, with a fairly straightforward model for the smoothing. Unfortunately, the trend-line lagged noticeably behind the major movements in the asset's pricing, causing this strategy to loose out on opportunities to ride those trends. Performance with this strategy barely out performed the SPY.

The final form of the momentum indicator is as simple as it gets, but provided surprising results. I take the 15 day simple moving average of the asset's price and compute its one period ROC. This produces a chart of daily movement in the price's SMA. This resulted in a reasonably smooth trend line, along with a technical indicator with which to signal trades.


#### Momentum strategy description

The momentum trading strategy is simply to take ROC(1) on SMA(15) and trade long or short based on the direction of change. The recommendation engine includes an adjustable buffer value to prevent over-eager trading on minor movements. The initial value of this buffer was 0.1, which indicates that the one period ROC would have to be above 10% to trigger a buy and under 10% to trigger a sell. This produced reasonably good results, including out-performing the Bollinger Band strategy (cumulative return of ~0.6).

The intuition behind the buffer value is that we can adjust the strategy to filter out minor price movements, while attempting to ride larger trends. However, this only works if you can accurately determine how much movement should be filtered out. A buffer set too high would miss most trends, while setting it too low would cause our recommendation engine to wildly chase momentary fluctuations. 

In an attempt to tune this parameter a bit, I used scipy's simulated annealing function to search for a buffer value that would produce higher cumulative returns over this period. This is an obviously egregious sin, as I then utilized the optimized buffer value on the same dataset for testing (no cross validation and separate test dataset). To be clear, a large range of buffer values produced results that out performed the Bollinger Strategy, including the conservative initial estimate. Annealing produced an optimized buffer value of 0.005, which resulted in a cumulative return of 0.78.


#### Momentum strategy code

The final momentum strategy code is minimal. The majority of data processing can be shown in the following example:

```python
    dates = pd.date_range(start_date, end_date)
    prices = get_data([symbol], dates)
    prices.drop('SPY', axis=1, inplace=True)
    prices['sma'] = pd.rolling_mean(prices, 15)
    roc = (prices['sma'] / prices['sma'].shift(1)) - 1
```


Generating trades from the ROC series is equally minimal:

```python
    # Iterate through ROC starting 20 days in
    for date, sma_roc in roc[20:].iteritems():
        # trending up
        if sma_roc > signal_buffer and position <= 0:
            # Enter long position. Code excluded for brevity. 
        # trending down
        if sma_roc < -signal_buffer and position >= 0:
            # Enter short position. Code excluded for brevity. 
```


#### Momentum strategy graph

Using a signal buffer value of 0.005 results in only five trades during the period. These happen at major inflection points, with the exception of one minor movement captured in March, '09. This illustrates the limitation of the strategy as it's not immune to picking up false trending indicators. However, at least over this period, the large overall trends were captured with the ROC on SMA indicator, as can be seen in Figure 3. It's also worth mentioning that if we consider the transaction cost of placing orders, a strategy with so few trades would be advantageous.

![Momentum Strategy](output/ms.png "Momentum Strategy")

The top graph plots the price and 20 day SMA, while the bottom graph shows the ROC on the 20 day SMA. Green buy signals are triggered when this ROC value moves over 0.005 and the position is held until a red sell signal is reached at -0.005. The obvious major flaw in this strategy is that any long-term movement that falls inside these buffer values will go unnoticed. This could result in a gradual loss if, for example, after a buy signal the ROC then remained between 0.0 and just over -0.005. Our long position would never exit, as the asset's price continued a steady decline.

### Performance

#### Performance compared to Bollinger Band strategy

The simple momentum strategy significantly out performed the Bollinger Band strategy both in cumulative return and in the risk adjusted return. Final portfolio values were: 13614.0 for Bollinger and 17784.0 for simple momentum.

#### Backtest results

The following are the results from backtesting the momentum strategy with the market simulator:

    Data Range: 2007-12-31 to 2009-12-31

    Sharpe Ratio of Fund: 1.42550672124
    Sharpe Ratio of SPY: -0.21996865409

    Cumulative Return of Fund: 0.7784
    Cumulative Return of SPY: -0.240581328829

    Standard Deviation of Fund: 0.0137483778696
    Standard Deviation of SPY: 0.0219524869863

    Average Daily Return of Fund: 0.00123458347334
    Average Daily Return of SPY: -0.000304189525556

    Final Portfolio Value: 17784.0

And finally, the resulting performance graph can be seen in figure 4.

![Momentum Performance](output/mp.png "Momentum Performance")
