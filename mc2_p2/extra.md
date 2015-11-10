---
title: MC2-Project-2 - Extra Credit
author: Magahet Mendiola
date: November, 2015
---

## Overview

We will review the performance of the simple momentum indicator in time periods before and after 2008-2009. Using the same time period for training our strategy and testing is not a good idea. We can perfectly tune our trades to extract maximum value during a set period. However, applying that same strategy on any other dataset would almost certainly produce poor results. What we should do in these cases is work with at least two datasets; one for training and another for testing. Ideally, we could utilize cross-validation on our training set as well.

## Testing

### 2006 - 2007

Figure 1 shows the trading signals issued during the period 2006-2007. The recommendation engine made four trades at what it interpreted as inflection points in the pricing trend. The first trade was good, in that it captured a raise of about $10. However, it's next trade mistook a momentary downswing as a trend and thus lost ~$10. We can see in the performance graph in Figure 2, how we gained and then lost all this value. This clearly illustrates the strategy's reliance on the buffer value to filter out false signals.

Another interesting point to note is the complete inactivity for the first eight months. This shows that the strategy is dependent on long-term vertical movements in pricing. Mostly horizontal movement will simply be filtered out. It also illustrates that buffer values that filter these small movements may work during certain periods, such as 2006, then later be too small to filter out false indicators, as seen in April, 2007.

![Momentum Strategy - 2006-2007](output/before-s.png)

![Momentum Performance - 2006-2007](output/before-p.png)

Overall performance of the momentum strategy was quite poor during the 2006-2007 period, as can be seen in the market simulation results:

    Data Range: 2005-12-31 to 2007-12-31
    Sharpe Ratio of Fund: -0.317286144317
    Sharpe Ratio of SPY: 0.619156351493

    Cumulative Return of Fund: -0.1053
    Cumulative Return of SPY: 0.157282471627

    Standard Deviation of Fund: 0.00905352087205
    Standard Deviation of SPY: 0.00837589003042

    Average Daily Return of Fund: -0.000180954065107
    Average Daily Return of SPY: 0.000326686380163

    Final Portfolio Value: 8947.0


## 2010 - 2011

Figure 3 shows the trading signals issued during the period 2010-2011. The recommendation engine again made four trades in this time window. The first few trade make the other limitation of the simple momentum strategy very clear. We see a false short at the beginning, which is held for nearly a year, as the overall price trend gradually increases. This is due to the ROC never exceeding the buffer value to trigger a buy signal. One method for addressing this could be to implement a more sophisticated metric. Possibly something that acts similar to PID control, and would account for not only the price differential, but also the volume of value change over time. We could also extend it to make trades in proportion to the ROC value and not just as a binary buy/sell signal.

![Momentum Strategy - 2010-2011](output/after-s.png)
![Momentum Performance - 2010-2011](output/after-p.png)

Performance of the momentum strategy for 2009-2011 also performed quite poorly. Most of the lost value was due to missing the slow price increase in the first year.

    Data Range: 2009-12-31 to 2011-12-31

    Sharpe Ratio of Fund: -0.489192180567
    Sharpe Ratio of SPY: 0.393165319464

    Cumulative Return of Fund: -0.6368
    Cumulative Return of SPY: 0.127791229486

    Standard Deviation of Fund: 0.0397259409442
    Standard Deviation of SPY: 0.0131086008359

    Average Daily Return of Fund: -0.00122420296989
    Average Daily Return of SPY: 0.000324661859049

    Final Portfolio Value: 3632.0
