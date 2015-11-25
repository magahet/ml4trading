---
title: MC3-Project-2 - ML Trading Strategy
author: Magahet Mendiola
date: November, 2015
---

## Overview

We will evaluate the use of machine learning algorithms on creating trading strategies. Specifically, we will evaluate the use of KNN on forecasting future asset prices given a set of technical indicators.


### Regression Task

The following indicators were used as features in the regression task:

1. Bollinger Band Value w/ 20-day SMA/STDEV
2. 5 Day Price Momentum
3. 20 Day Rolling Standard Deviation

The regression task was set to predict the 5 day future asset price change. KNN was used with K=3 and euclidean distance as the metric.


### Trading Strategy

The predicted future price change was used to create a trading strategy that would enter a long position of 100 shares whenever the predicted change went over 1%, entered a short position of -100 shares when predicted change dropped below -1%, and exited any long/short positions when predicted change fell between 1% and -1%.


## ML4T-399 Dataset

### 2008-2009 Time Period

#### Regression Results

![Training Y/Price/Predicted Y - ML4T-399 '08-'09](output/m399-y-09.png)

Figure 1 illustrates actual 5 day future price, predicted future price, and current price on the ML4T-399 dataset. We see that future prices, both actual and predicted, correctly lag 5 trading days behind current prices. We also see that predicted future prices and actual future prices visually match. This is validated by low cumulative error between predicted and actual Y values (RMSE: 0.0004, corr: 0.99).


#### Generated Trades

Figure 2 shows the entry and exits points for period 2008-2009. The plot has asset prices on top and the predicted 5 day price change on the bottom. We can see how the trading strategy is entering long positions as this value moves above 0.01. Likewise, short positions are shown in red when the predicted change falls below -0.01. We can see in the top plot that this strategy does capture much of the movement, both up and down, in the asset price. However, it could be tuned further as it currently looses some value in the threshold window 0.01 to -0.01. It would be possible to remove this window completely and trade strictly on movements above and below a change of 0.0. This would likely cause our regression trading strategy to perform more poorly on data without such obvious trends.


![Entries/Exits - ML4T-399 '08-'09](output/m399-orders-09.png)


#### Trading Strategy Backtest

![Backtest - ML4T-399 '08-'09](output/m399-perf-09.png)

Figure 3 shows the performance of our trading strategy for ML4T-399 2008-2009. We see a cumulative return of 7.7 (-0.2 on SPY). The Sharpe ratio of our portfolio is 9.3 (-0.2 on SPY).


### 2010 Time Period

#### Generated Trades

The KNN learner was trained on ML4T-399 data during the 2008-2009 time period. Pricing data from 2010 was then loaded and technical indicators calculated on this dataset. Using the 2008-2009 trained learner, queries were made with the 2010 attributes. As before, trades were generated using the +/- 0.01 trading signal.

Figure 4 shows the results of these generated trades. As before, the strategy does well at capturing the movement in asset price. Error on this test set is: RMSE: 0.0018, Corr: 0.99, indicating that our KNN learner performed quite well in predicting price changes with test samples outside the original training data.

![Entries/Exits - ML4T-399 '10](output/m399-orders-10.png)


#### Trading Strategy Backtest

Figure 5 shows the performance results of our 2010 portfolio as created with the KNN based trading strategy. We see a cumulative return of 3.7 (0.1 on SPY) and a Sharpe ratio of 10.4 (0.8 on SPY).

![Backtest - ML4T-399 '10](output/m399-perf-10.png)


## ML4T-399 Dataset

### 2008-2009 Time Period

#### Generated Trades

Using the same learning and trading strategy on IBM during 2008-2009 shows positive, though not overly impressive, results. Figure 6 shows generated orders, IBM price, and

![Training Y/Price/Predicted Y - IBM '08-'09](output/ibm-orders-09.png)

    In sample results
    RMSE:  0.0310958524397
    corr:  0.697132609597


#### Trading Strategy Backtest

IBM Data In Sample Backtest

![Backtest - IBM '08-'09](output/ibm-perf-09.png)

    Data Range: 2007-12-31 to 2009-12-31

    Sharpe Ratio of Fund: 3.70915105837
    Sharpe Ratio of $SPX: -0.21996865409

    Cumulative Return of Fund: 2.0096
    Cumulative Return of $SPX: -0.240581328829

    Standard Deviation of Fund: 0.00954080200275
    Standard Deviation of $SPX: 0.0219524869863

    Average Daily Return of Fund: 0.00222925183849
    Average Daily Return of $SPX: -0.000304189525556

    Final Portfolio Value: 30096.0


### 2010 Time Period

#### Generated Trades

IBM Data Out of Sample Entries/Exits: Freeze your model based on the 2008-2009 data. Now test it for the year 2010 -- Plot that illustrates entry & exits, generate trades,

![Entries/Exits - IBM '10](output/ibm-orders-10.png)


#### Trading Strategy Backtest

IBM Data Out of Sample Backtest

![Backtest - IBM '10](output/ibm-perf-10.png)

    Data Range: 2009-12-31 to 2010-12-31

    Sharpe Ratio of Fund: 0.679632745049
    Sharpe Ratio of $SPX: 0.756512754402

    Cumulative Return of Fund: 0.0985
    Cumulative Return of $SPX: 0.127827100708

    Standard Deviation of Fund: 0.00983141011967
    Standard Deviation of $SPX: 0.0113715303326

    Average Daily Return of Fund: 0.000420910575847
    Average Daily Return of $SPX: 0.000541919649169

    Final Portfolio Value: 10985.0

Learning results

    In sample results
    RMSE:  0.04283663904
    corr:  0.140995673532

