import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# download data
stock = "RELIANCE.NS"
data = yf.download(stock, start="2019-01-01", end="2024-01-01")

# Flatten multi-level columns
data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

# reset index
data.reset_index(inplace=True)
print("Rows:", len(data))
print(data[['Date', 'Close']].head())
print("NaNs in Close:", data['Close'].isna().sum())

print(data.head())

# plot close price
plt.figure(figsize=(12,5))
plt.plot(data['Date'].values, data['Close'].values)
plt.title("RELIANCE Close Price")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)
plt.show()


# Calculate Moving Averages
data['SMA_20'] = data['Close'].rolling(window=20).mean()
data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()

# Plot price and moving averages
plt.figure(figsize=(12,6))
plt.plot(data['Date'].values, data['Close'].values, label='Close')
plt.plot(data['Date'].values, data['SMA_20'].values, label='SMA 20')
plt.plot(data['Date'].values, data['SMA_50'].values, label='SMA 50')
plt.title("RELIANCE - Moving Average Strategy")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()

# Create signal column
data['Signal'] = 0

# Generate signals
data.loc[data['SMA_20'] > data['SMA_50'], 'Signal'] = 1
data.loc[data['SMA_20'] < data['SMA_50'], 'Signal'] = -1

# Identify crossover points
data['Position'] = data['Signal'].diff()

plt.figure(figsize=(12,6))
plt.plot(data['Date'], data['Close'], label='Close Price', alpha=0.6)
plt.plot(data['Date'], data['SMA_20'], label='SMA 20')
plt.plot(data['Date'], data['SMA_50'], label='SMA 50')

# Buy signals
plt.scatter(
    data.loc[data['Position'] == 2, 'Date'],
    data.loc[data['Position'] == 2, 'Close'],
    label='Buy',
    marker='^',
    color='green'
)

# Sell signals
plt.scatter(
    data.loc[data['Position'] == -2, 'Date'],
    data.loc[data['Position'] == -2, 'Close'],
    label='Sell',
    marker='v',
    color='red'
)

plt.title("Moving Average Crossover Signals")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()

data['Trade_PnL'] = 0.0
data['Exit_Reason'] = None

# backtesting engine
initial_capital = 100000
capital = initial_capital
cash = initial_capital
position = 0
entry_price = 0
transaction_cost = 0.001  # 0.1% per trade
risk_per_trade = 0.01      # 1% risk
stop_loss_pct = 0.08       # 8% stop loss


data['Trade'] = 0
data['PnL'] = 0.0          # ← add this
data['Capital'] = float(initial_capital)

for i in range(1, len(data)):

    price = data['Close'].iloc[i]

    # =========================
    # STOP LOSS CHECK (ADD HERE)
    # =========================
    if position > 0:
        stop_price = entry_price * (1 - stop_loss_pct)  # 8% stop loss

        if price <= stop_price:
            gross_value = position * price
            cost = gross_value * transaction_cost

            capital = gross_value - cost
            capital = cash
            pnl = (price - entry_price) * position

            data.at[i, 'Trade'] = -1
            data.at[i, 'PnL'] = pnl
            data.at[i, 'Capital'] = capital
            data.at[i, 'Trade_PnL'] = pnl
            data.at[i, 'Exit_Reason'] = 'STOP_LOSS'

            position = 0
            continue   # VERY IMPORTANT

    
    # Buy
    if (
    data['Position'].iloc[i] == 2 and
    position == 0 and
    price > data['SMA_200'].iloc[i]
):


        buy_price = price

        # Risk parameters
        # risk_amount = capital * risk_per_trade
        # position_value = risk_amount / stop_loss_pct

        # Cap position size
        # position_value = min(position_value, capital)

        # Shares to buy
        # position = position_value / buy_price

        # Fully invest capital but normalize risk via stop loss
        position_value = capital
        position = position_value / buy_price


        # Transaction cost
        cost = position_value * transaction_cost
        cash -= cost

        entry_price = buy_price
        data.at[i, 'Trade'] = 1


    # Sell
    elif data['Position'].iloc[i] == -2 and position > 0:
        sell_price = data['Close'].iloc[i]
        gross_value = position * sell_price
        cost = gross_value * transaction_cost
    
        capital = gross_value - cost
        capital = cash
        pnl = (sell_price - entry_price) * position
    
        data.at[i, 'Trade'] = -1
        data.at[i, 'PnL'] = pnl
        data.at[i, 'Capital'] = capital
        data.at[i, 'Trade_PnL'] = pnl
        data.at[i, 'Exit_Reason'] = 'MA_EXIT'
    
        position = 0

        print("Min Capital:", data['Capital'].min())
        print("Max Capital:", data['Capital'].max())


    # Daily portfolio value (KEY FIX)
    if position > 0:
        data.at[i, 'Capital'] = cash + position * price
    else:
        data.at[i, 'Capital'] = cash


data['Capital'] = data['Capital'].replace(0, pd.NA).ffill()


# equity curve
plt.figure(figsize=(12,6))
plt.plot(data['Date'], data['Capital'])
plt.title("Equity Curve - MA Crossover Strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.show()

# Buy & Hold (RELIANCE)
data['BuyHold'] = 100000 * (data['Close'] / data['Close'].iloc[0])

plt.figure(figsize=(12,6))
plt.plot(data['Date'], data['Capital'], label='MA Strategy')
plt.plot(data['Date'], data['BuyHold'], label='Buy & Hold', linestyle='--')
plt.title('Strategy vs Buy & Hold')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.legend()
plt.grid(True)
plt.show()

# total return
final_capital = data['Capital'].iloc[-1]
total_return = (final_capital - initial_capital) / initial_capital * 100

print(f"Final Capital: ₹{final_capital:.2f}")
print(f"Total Return: {total_return:.2f}%")

# CAGR (Compound Annual Growth Rate)
start_date = data['Date'].iloc[0]
end_date = data['Date'].iloc[-1]
years = (end_date - start_date).days / 365

cagr = ((final_capital / initial_capital) ** (1 / years) - 1) * 100
print(f"CAGR: {cagr:.2f}%")

# Maximum Drawdown (Risk Measure)
data['Rolling_Max'] = data['Capital'].cummax()
data['Drawdown'] = (data['Capital'] - data['Rolling_Max']) / data['Rolling_Max']

max_drawdown = data['Drawdown'].min() * 100
print(f"Max Drawdown: {max_drawdown:.2f}%")

# Number of Trades
total_trades = data['Trade'].abs().sum() // 2
print(f"Total Trades: {int(total_trades)}")

# Win Rate
trade_pnls = data.loc[data['Trade'] == -1, 'Trade_PnL']

winning_trades = (trade_pnls > 0).sum()
total_closed_trades = len(trade_pnls)

win_rate = (winning_trades / total_closed_trades) * 100 if total_closed_trades > 0 else 0
print(f"Win Rate: {win_rate:.2f}%")

# Average win and loss
winning_trades_pnl = trade_pnls[trade_pnls > 0]
losing_trades_pnl = trade_pnls[trade_pnls < 0]

avg_win = winning_trades_pnl.mean() if len(winning_trades_pnl) > 0 else 0
avg_loss = abs(losing_trades_pnl.mean()) if len(losing_trades_pnl) > 0 else 0

# Expectancy
win_rate_decimal = win_rate / 100

expectancy = (win_rate_decimal * avg_win) - ((1 - win_rate_decimal) * avg_loss)
print(f"Expectancy per trade: ₹{expectancy:.2f}")

# Sharpe Ratio (Risk-Adjusted Return)
daily_returns = data['Capital'].pct_change().dropna()

sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5)
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(data['Exit_Reason'].value_counts())
print(data.groupby('Exit_Reason')['Trade_PnL'].mean())
print(data[data['Exit_Reason'] == 'STOP_LOSS'][['Date', 'Trade_PnL']].head())
