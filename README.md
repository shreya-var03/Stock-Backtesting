# 📈 Risk-Managed Trend-Following Backtesting System (Indian Equities)

# Overview

This project is an **end-to-end Python backtesting framework** designed to evaluate **risk-managed trend-following strategies** on Indian equities using historical market data.

The system emphasizes **institutional-style thinking** by integrating:

* systematic signal generation,
* explicit risk management,
* position sizing,
* regime (trend) filtering, and
* robust performance evaluation.

The initial implementation focuses on **RELIANCE.NS** as a case study but is easily extendable to other equities.

---

# Strategy Logic (High-Level)

The strategy follows a **trend-following philosophy** with layered risk controls:

1. **Signal Generation**

   * Short-term vs long-term moving average crossover (SMA 20 / SMA 50)
   * Long-only strategy

2. **Regime Filter**

   * Trades are allowed only when price is above the **200-day moving average**
   * Avoids structurally bearish market regimes

3. **Risk Management**

   * Fixed fractional risk per trade (1% of capital)
   * Hard stop-loss at 8% from entry
   * Transaction costs modeled (0.1% per trade)

4. **Position Sizing**

   * Position size is determined by:

     ```
     position_value = (capital × risk_per_trade) / stop_loss_percentage
     ```
   * Ensures **risk-normalized exposure**, not fixed capital allocation

5. **Exit Logic**

   * Moving-average crossover exit
   * Stop-loss exit
   * Exit reason tracked for post-trade analysis

---

# Key Features

* 📊 Historical data ingestion via `yfinance`
* 📉 SMA-based signal generation and visualization
* 🧮 Event-driven backtesting engine
* 💰 Daily mark-to-market portfolio valuation
* ⚖️ Risk-normalized position sizing
* 🛑 Stop-loss based risk control
* 🧠 Trend (regime) filtering using long-term moving average
* 📈 Benchmark comparison against Buy & Hold
* 📑 Trade-level PnL tracking
* 🧾 Exit reason attribution (`MA_EXIT`, `STOP_LOSS`)
* 📐 Performance metrics:

  * Total Return
  * CAGR
  * Maximum Drawdown
  * Win Rate
  * Expectancy
  * Sharpe Ratio

---

# Performance Evaluation

The framework computes both **absolute** and **risk-adjusted** metrics to ensure the strategy is evaluated beyond headline returns.

Key outputs include:

* Equity curve
* Strategy vs Buy & Hold comparison
* Drawdown analysis
* Trade distribution by exit type
* Average PnL by exit reason

This allows clear diagnosis of **where returns come from** and **how risk is controlled**.

---

# Why This Project Matters

This project was intentionally designed to move beyond retail-style backtests by:

* Explicitly separating **signal generation** from **risk management**
* Avoiding full-capital exposure on every trade
* Tracking regime dependence and exit attribution
* Emphasizing **capital preservation** and **drawdown control**

The goal is to reflect how **systematic strategies are evaluated in institutional environments**, particularly in wealth management and quantitative research contexts.

---

# Tech Stack

* Python
* pandas
* matplotlib
* yfinance

---

# How to Run

```bash
pip install yfinance pandas matplotlib
```

```bash
python backtest.py
```

(Ensure an active internet connection for data download.)

---

# Future Enhancements

Planned extensions include:

* Multi-asset portfolio support
* Volatility-based position sizing
* Walk-forward / out-of-sample testing
* Parameter sensitivity analysis
* Strategy performance across market regimes

---

# Disclaimer

This project is for **educational and research purposes only**.
It does not constitute investment advice or a recommendation to trade live markets.
