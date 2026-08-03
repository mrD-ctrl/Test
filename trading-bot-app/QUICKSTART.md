# Quick Start Guide - Trading Bot App

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd /workspace/trading-bot-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure (Optional)

For **Shadow Mode** (default), no configuration needed! Just run:

```bash
python src/main.py
```

To customize settings, copy the example env file:

```bash
cp .env.example .env
```

Edit `.env` to change:
- Operating mode (shadow/live/hybrid)
- Trading 212 API key (for live trading)
- Risk parameters
- Watchlist symbols

### Step 3: Run the Bot

```bash
python src/main.py
```

### Step 4: Open Dashboard

Navigate to: **http://localhost:5000**

You'll see:
- Shadow portfolio performance
- Strategy lab statistics
- Top performing strategies
- Recent trades
- Control buttons

---

## 📋 What Happens When You Run

1. **System Starts**
   - Initializes in shadow mode (no API key needed)
   - Creates necessary directories
   - Sets up logging

2. **Strategy Lab Activates**
   - Generates 10 initial strategies if none exist
   - Strategies include: Momentum, Mean Reversion, RSI, MA Crossover, Bollinger Bands

3. **Data Collection Begins**
   - Fetches historical data from Yahoo Finance for all watchlist symbols
   - Caches data for fast access

4. **Shadow Trading Starts**
   - Executes simulated trades based on strategy signals
   - Tracks virtual portfolio performance
   - No real money involved

5. **Dashboard Launches**
   - Web interface available at http://localhost:5000
   - Auto-refreshes every 5 seconds
   - Shows real-time performance metrics

---

## 🎮 Dashboard Controls

| Button | Action |
|--------|--------|
| ▶ Start | Start/restart trading |
| ⏹ Stop | Pause trading |
| 🔬 Optimize | Trigger strategy optimization |
| ➕ Generate | Create new strategy variations |
| 🔄 Refresh | Manually refresh data |

---

## 📊 Understanding the Modes

### Shadow Mode (Default)
✅ No API keys required  
✅ Zero financial risk  
✅ Continuous learning  
✅ Validates strategies  

**Best for:** Getting started, testing, learning

### Live Mode
⚠️ Requires Trading 212 API key  
⚠️ Real money trading  
✅ Applies optimized strategies  
✅ Learns from actual outcomes  

**Best for:** Production trading (after thorough shadow testing)

### Hybrid Mode
✅ Runs both simultaneously  
✅ Shadow validates new strategies  
✅ Live executes proven strategies  
✅ Performance comparison  

**Best for:** Production with safety net

---

## 📈 First Time Expectations

### Minute 1:
- System initializes
- 10 strategies generated
- Data fetched for 15 symbols

### Minute 5:
- First shadow trades executed
- Dashboard shows initial performance

### Hour 1:
- Multiple trades executed
- Strategy performance tracked

### Hour 6:
- First optimization cycle runs
- New strategy variations created
- Best strategies identified

### Day 1:
- 50+ shadow trades executed
- Strategy library growing
- Performance patterns emerging

---

## 🔧 Common First Steps

### Add Your Favorite Stocks
Edit `.env`:
```
WATCHLIST=AAPL,GOOGL,TSLA,YOUR_SYMBOL,HERE
```

### Adjust Risk Parameters
Edit `.env`:
```
RISK_PER_TRADE_PERCENT=0.5
MAX_POSITION_SIZE_PERCENT=3.0
STOP_LOSS_PERCENT=3.0
```

### Switch to Live Mode (Advanced)
1. Get Trading 212 API key from https://api.trading212.com/
2. Edit `.env`:
```
MODE=hybrid
TRADING212_API_KEY=your_key_here
TRADING212_ENV=demo  # Start with demo!
```

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Dashboard won't load
- Check if main.py is running
- Verify port 5000 is not in use
- Check `storage/logs/system.log`

### No strategies showing
- Wait a few minutes for initial generation
- Click "➕ Generate" button manually
- Check logs for errors

### No data in dashboard
- Wait for first data refresh (5 minutes)
- Check internet connection
- Verify Yahoo Finance is accessible

---

## 💡 Pro Tips

1. **Start in Shadow Mode**: Run for at least 2 weeks before considering live trading

2. **Monitor Regularly**: Check dashboard daily to understand system behavior

3. **Adjust Gradually**: Make small parameter changes and observe impact

4. **Backup Strategies**: Copy `storage/strategies/` folder regularly

5. **Keep Running**: System learns best when running 24/7

---

## 📚 Next Steps

1. Read full [README.md](README.md) for detailed documentation
2. Explore generated strategies in `storage/strategies/`
3. Review logs in `storage/logs/`
4. Customize strategies in `src/strategies/`
5. Consider adding premium data sources

---

## ⚠️ Important Reminders

- This is for **personal/educational use only**
- **Not financial advice**
- Always test thoroughly before live trading
- Never risk money you can't afford to lose
- Past performance ≠ future results

---

**Happy Trading! 🚀**

Questions? Check the full README or review the code comments.
