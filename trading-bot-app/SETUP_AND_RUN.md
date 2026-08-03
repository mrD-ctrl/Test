# 🚀 Trading Bot App - Setup & Run Guide

## ✅ System Ready for Personal Use

Your self-learning trading bot is fully configured with:
- **Shadow Mode**: Works immediately without any API keys
- **Strategy Lab**: Auto-generates and optimizes strategies 24/7
- **Dashboard**: Real-time monitoring at http://localhost:5000
- **No Authority Conflicts**: Clear separation of responsibilities

---

## 📋 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd /workspace/trading-bot-app
pip install -r requirements.txt
```

### Step 2: Configure (Optional)
```bash
# Copy example config
cp .env.example .env

# Edit .env if you want to customize settings
# NOT REQUIRED for shadow mode - works with defaults!
```

### Step 3: Run the Bot
```bash
python src/main.py
```

Then open your browser: **http://localhost:5000**

---

## 🎯 Operating Modes

### Shadow Mode (Default - No API Keys Needed)
```bash
# Just run it - starts in shadow mode automatically
python src/main.py
```
- ✅ Fetches real data from Yahoo Finance
- ✅ Generates trading strategies
- ✅ Executes simulated trades
- ✅ Learns and optimizes continuously
- ✅ Zero financial risk

### Live Mode (With Trading 212 API Key)
```bash
# Add your API key to .env
echo "TRADING212_API_KEY=your_key_here" >> .env
echo "MODE=live" >> .env
python src/main.py
```

### Hybrid Mode (Both Shadow + Live)
```bash
# Run shadow learning alongside live trading
echo "TRADING212_API_KEY=your_key_here" >> .env
echo "MODE=hybrid" >> .env
python src/main.py
```

---

## 📊 Dashboard Features

### Real-Time Monitoring
- Portfolio value (shadow + live)
- Open positions
- Recent trades with P&L
- Strategy performance rankings
- Daily P&L chart
- Drawdown visualization

### Control Panel
- Start/Stop trading engine
- Force strategy optimization
- Generate new strategies manually
- Switch between modes
- Export performance reports

### Auto-Refresh
- Updates every 5 seconds
- No manual refresh needed

---

## 🧠 How It Learns

### Continuous Learning Loop
```
1. Generate Strategies → 2. Backtest → 3. Shadow Trade → 4. Analyze → 5. Optimize
                              ↑                                              ↓
                              └──────────────────────────────────────────────┘
```

### Self-Improvement Mechanisms
- **Genetic Algorithm**: Mutates parameters of top performers
- **Performance Tracking**: Sharpe ratio, Sortino, Max Drawdown
- **Automatic Retirement**: Bottom 10% strategies replaced
- **24/7 Operation**: Learns even when markets are closed

### Strategy Types (8 Total)
1. Momentum (trend following)
2. Mean Reversion (statistical arbitrage)
3. MA Crossover (classic trend)
4. RSI (momentum oscillator)
5. Bollinger Bands (volatility)
6. MACD (momentum + trend)
7. Breakout (support/resistance)
8. Volatility Breakout (ATR-based)

---

## 📁 Project Structure

```
trading-bot-app/
├── src/
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── orchestrator.py  # Central coordinator
│   │   └── risk_manager.py  # Risk controls
│   ├── strategies/
│   │   └── strategy_lab.py  # Strategy generation & optimization
│   ├── execution/
│   │   ├── shadow_engine.py # Simulated trading
│   │   └── trading212.py    # Broker integration
│   ├── data/
│   │   └── providers.py     # Yahoo Finance, News
│   └── dashboard/
│       └── app.py           # Web interface
├── storage/
│   ├── strategies/          # Saved strategies
│   ├── shadow_trades/       # Shadow trade history
│   ├── live_trades/         # Live trade history
│   └── logs/                # System logs
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Configuration Options

### Environment Variables (.env)

```bash
# Operating Mode
MODE=shadow                    # shadow, live, or hybrid

# Trading 212 (only for live/hybrid mode)
TRADING212_API_KEY=            # Your API key
TRADING212_ENV=demo            # demo or live
TRADING212_ACCOUNT_TYPE=INVEST # INVEST or ISA

# Risk Management
MAX_POSITION_SIZE_PERCENT=5.0  # Max 5% per position
STOP_LOSS_PERCENT=2.0          # 2% stop loss
TAKE_PROFIT_PERCENT=5.0        # 5% take profit
MAX_DAILY_LOSS_PERCENT=3.0     # Max 3% daily loss
MAX_OPEN_POSITIONS=10          # Max 10 positions
RISK_PER_TRADE_PERCENT=1.0     # 1% risk per trade

# Learning Parameters
OPTIMIZATION_INTERVAL_HOURS=6  # Optimize every 6 hours
BACKTEST_DAYS=365              # 1 year backtest window
SHADOW_TRADES_PER_DAY=100      # Max 100 shadow trades/day

# Watchlist (UK + US stocks)
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,AMZN,META,VOD,LLOY,BP,SHEL,HSBA,GSK,RIO

# Premium Data (optional - add your own keys)
EODHD_API_KEY=                 # EOD Historical Data
FINHUB_API_KEY=                # Financial Modeling Hub
ALPHA_VANTAGE_API_KEY=         # Alpha Vantage

# Dashboard
DASHBOARD_PORT=5000
DASHBOARD_HOST=0.0.0.0
```

---

## 🔒 Security & Compliance

### UK Trading Regulations
- ✅ ISA account restrictions respected (no shorting, no leverage)
- ✅ Invest account standard rules
- ✅ Trading 212 API rate limits honored

### Data Privacy
- All data stored locally in `/storage`
- No external data transmission except API calls
- API keys stored in `.env` (not committed to git)

### Risk Disclaimers
⚠️ **IMPORTANT**: This is for educational/personal use only
- Not financial advice
- Past performance ≠ future results
- Always test in shadow mode before live trading
- Only trade money you can afford to lose

---

## 📈 Monitoring & Analytics

### View Logs
```bash
# Real-time logs
tail -f storage/logs/system.log

# Strategy performance
cat storage/strategies/*.json | jq '.performance'
```

### Export Reports
Use the dashboard's "Export Report" button to download:
- Trade history (CSV)
- Strategy performance (JSON)
- Portfolio analytics (PDF)

---

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt --upgrade
```

**Dashboard won't load:**
```bash
# Check if port 5000 is available
lsof -i :5000
# Kill process if needed, then restart
```

**No strategies generated:**
- Wait 5-10 minutes for initial backtesting
- Check logs: `tail -f storage/logs/system.log`
- Verify Yahoo Finance connectivity

**API rate limits:**
- Reduce watchlist size
- Increase data refresh interval
- Add premium API keys for higher limits

---

## 🎓 Next Steps

1. **Run in Shadow Mode** (first 2-4 weeks)
   - Let it learn and optimize
   - Monitor strategy performance
   - Adjust risk parameters if needed

2. **Review Performance**
   - Check Sharpe ratio (>1.5 target)
   - Review max drawdown (<15% target)
   - Analyze win rate (>55% target)

3. **Switch to Hybrid Mode**
   - Add Trading 212 API key
   - Start with small position sizes
   - Compare shadow vs live results

4. **Go Live** (when confident)
   - Monitor closely first week
   - Keep shadow mode running for comparison
   - Adjust parameters based on real-world feedback

---

## 📚 Additional Resources

- `RESEARCH_FINDINGS.md` - Market research & best practices
- `README.md` - Full documentation
- `QUICKSTART.md` - 5-minute setup guide
- Trading 212 API Docs: https://api.trading212.com/

---

## 💡 Tips for Best Results

1. **Be Patient**: Allow 2-4 weeks of shadow learning before live trading
2. **Diversify**: Use a watchlist of 10-20 symbols across sectors
3. **Conservative Risk**: Start with 0.5-1% risk per trade
4. **Regular Reviews**: Check strategy performance weekly
5. **Continuous Learning**: Let it run 24/7 for best optimization

---

**Happy Trading! 🚀📈**

Remember: This is a learning tool. Always do your own research and never risk more than you can afford to lose.
