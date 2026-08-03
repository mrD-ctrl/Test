# AI-Powered Self-Learning Trading Bot for Trading 212

## Overview

An advanced autonomous trading bot designed for Trading 212 UK broker, targeting ISA and Invest accounts. The system features self-learning capabilities, continuous strategy optimization through shadow dry runs, and seamless integration with real trading when API credentials are provided.

## Key Features

### 🧠 Self-Learning & Optimization
- **Shadow Dry Run Mode**: Continuously learns and optimizes strategies using real market data without requiring broker credentials
- **Dual Learning Paths**:
  - Learns from simulated trades using Yahoo Finance data
  - Learns from actual broker outcomes when API key is added
- **Strategy Lab**: Automatically builds, tests, and optimizes trading strategies 24/7
- **Self-Tuning**: Adapts parameters based on market conditions and performance metrics

### 📊 Data Integration
- **Free Data Sources**:
  - Yahoo Finance (prices, historical data)
  - Google News & Yahoo News (sentiment analysis)
- **Optional Premium Sources** (user-provided API keys):
  - EODHD (end-of-day and intraday data)
  - FinHub (real-time financial data)
  - Other premium APIs as needed

### 🤖 Trading Strategies
- Momentum strategies
- Mean reversion
- Breakout detection
- Moving average crossovers
- RSI-based strategies
- Bollinger Bands
- MACD signals
- Volatility breakouts
- Custom ML-driven strategies

### 💼 Broker Integration
- Trading 212 API integration (based on official specs)
- Support for Invest and Stocks ISA accounts
- Demo and Live environments
- Order management (Market, Limit, Stop orders)
- Portfolio tracking

### 🎛️ Dashboard
- Real-time portfolio monitoring
- Strategy performance analytics
- Shadow vs Live comparison
- Trade history and logs
- Manual controls and overrides
- Interactive charts and visualizations

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     WEB DASHBOARD                               │
│         Flask-based UI with real-time updates                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MAIN ORCHESTRATOR                              │
│  Coordinates all components, manages modes, schedules tasks     │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌───────────────────────┐
│   DATA LAYER    │  │  STRATEGY LAB   │  │  EXECUTION ENGINE     │
│ • Yahoo Finance │  │ • Generate      │  │ • Shadow Dry Run      │
│ • News APIs     │  │ • Backtest      │  │ • Live Trading        │
│ • Broker API    │  │ • Optimize      │  │ • Order Management    │
│ • Cache Mgmt    │  │ • Deploy        │  │ • Position Tracking   │
└─────────────────┘  └─────────────────┘  └───────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEARNING ENGINE                               │
│      Performance Analysis • Pattern Recognition • Optimization  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                │
│  Strategies • Trade Logs • Performance Metrics • Historical Data│
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Quick Start

1. **Navigate to project directory**
```bash
cd /workspace/trading-bot-app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (optional for shadow mode)
```

5. **Run the application**
```bash
# Start main system (includes dashboard)
python src/main.py

# Or run dashboard separately in another terminal
python src/dashboard/app.py
```

6. **Access Dashboard**
Open your browser and navigate to: `http://localhost:5000`

## Configuration

### Environment Variables (.env)

```ini
# ==================== OPERATING MODE ====================
# Options: shadow, live, hybrid
# - shadow: No broker needed, learns from Yahoo data
# - live: Real trading with broker API
# - hybrid: Both simultaneously for validation
MODE=shadow

# ==================== TRADING 212 API ====================
# Only required for live/hybrid mode
TRADING212_API_KEY=your_api_key_here
TRADING212_ENV=demo  # Options: demo, live
TRADING212_ACCOUNT_TYPE=INVEST  # Options: INVEST, ISA

# ==================== PREMIUM DATA PROVIDERS ====================
# Optional - add your own API keys for enhanced data
EODHD_API_KEY=
FINHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=

# ==================== DASHBOARD SETTINGS ====================
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5000
DASHBOARD_DEBUG=false

# ==================== LEARNING PARAMETERS ====================
LEARNING_RATE=0.01
BACKTEST_DAYS=365
SHADOW_TRADES_PER_DAY=100
OPTIMIZATION_INTERVAL_HOURS=6
MAX_POSITION_SIZE_PERCENT=5.0
STOP_LOSS_PERCENT=2.0
TAKE_PROFIT_PERCENT=5.0

# ==================== RISK MANAGEMENT ====================
MAX_DAILY_LOSS_PERCENT=3.0
MAX_OPEN_POSITIONS=10
RISK_PER_TRADE_PERCENT=1.0
```

## Usage Modes

### 1. Shadow Mode (Default - No API Keys Required)

Perfect for getting started immediately. The system:
- Fetches real market data from Yahoo Finance
- Generates and backtests trading strategies
- Simulates trades (dry run) with virtual portfolio
- Learns and optimizes continuously 24/7
- Stores all performance metrics
- Builds strategy library without any risk

```bash
MODE=shadow python src/main.py
```

**Benefits:**
- Zero financial risk
- Immediate operation (no setup required)
- Continuous learning even when you're not actively trading
- Validates strategies before live deployment

### 2. Live Mode (Requires Trading 212 API Key)

Real trading with your ISA or Invest account:
- Executes actual trades on Trading 212
- Applies optimized strategies from shadow testing
- Continues learning from live trade outcomes
- Full portfolio management
- Real-time P&L tracking

```bash
MODE=live python src/main.py
```

**Requirements:**
- Valid Trading 212 API key
- Funded ISA or Invest account
- Understanding of trading risks

### 3. Hybrid Mode (Recommended for Production)

Runs both shadow and live simultaneously:
- Shadow mode validates new strategies continuously
- Live mode executes only proven, high-performing strategies
- Compares performance between shadow and live
- Cross-validates strategy effectiveness
- Provides safety net through shadow verification

```bash
MODE=hybrid python src/main.py
```

**Benefits:**
- Continuous validation of new strategies
- Performance comparison (shadow vs live)
- Reduced risk through dual verification
- Ongoing optimization without interrupting live trading

## Strategy Lab

The Strategy Lab is the brain of the system, automatically:

### 1. Strategy Generation
- Creates new strategy variations daily
- Combines successful elements from existing strategies
- Tests different parameter combinations
- Explores new technical indicators

### 2. Backtesting Engine
- Tests strategies on historical data (configurable period)
- Simulates trades with realistic assumptions
- Calculates comprehensive performance metrics
- Identifies optimal entry/exit points

### 3. Shadow Validation
- Runs strategies in real-time with virtual money
- Tracks performance in current market conditions
- Validates backtest results against live simulation
- Builds confidence before live deployment

### 4. Continuous Optimization
- Analyzes performance every 6 hours (configurable)
- Adjusts parameters based on results
- Retires underperforming strategies
- Promotes top performers to live trading

### Strategy Metrics Tracked

| Metric | Description |
|--------|-------------|
| Total Return (%) | Overall profitability |
| Sharpe Ratio | Risk-adjusted return |
| Sortino Ratio | Downside risk-adjusted return |
| Max Drawdown (%) | Largest peak-to-trough decline |
| Win Rate (%) | Percentage of profitable trades |
| Profit Factor | Gross profit / Gross loss |
| Avg Trade Duration | Average time in trades |
| Recovery Factor | Net profit / Max drawdown |

### Storage Location
All strategies are saved in `storage/strategies/` as JSON files containing:
- Strategy configuration
- Parameter values
- Performance history
- Backtest results
- Deployment status

## Dashboard Features

Access the web dashboard at `http://localhost:5000`

### Real-Time Monitoring
- **Portfolio Overview**: Total value, P&L, cash balance (shadow & live)
- **Active Positions**: Current holdings with entry price and current P&L
- **Recent Trades**: Latest executed trades with outcomes
- **Performance Charts**: Interactive P&L graphs (daily, weekly, monthly)
- **Strategy Rankings**: Top performing strategies by various metrics

### Controls Panel
- **Start/Stop Trading**: Pause or resume automated trading
- **Mode Switching**: Change between shadow/live/hybrid modes
- **Risk Parameters**: Adjust position sizes, stop-loss, take-profit
- **Manual Trading**: Execute manual trades (live mode only)
- **Strategy Deployment**: Activate/deactivate specific strategies

### Analytics Section
- **Performance Analytics**: Detailed charts and statistics
- **Strategy Comparison**: Side-by-side strategy performance
- **Win/Loss Distribution**: Visual breakdown of trade outcomes
- **Drawdown Analysis**: Historical drawdown periods
- **Learning Progress**: System improvement over time
- **Market Sentiment**: News sentiment indicators

### Strategy Lab Interface
- **View Strategies**: Browse all generated strategies
- **Backtest Tool**: Test custom strategies on historical data
- **Parameter Optimization**: Fine-tune strategy parameters
- **Deploy/Retract**: Move strategies between shadow and live
- **Performance History**: Detailed strategy track records

### System Status
- **Data Feed Status**: Connection status for all data sources
- **API Health**: Broker API connectivity
- **System Resources**: CPU, memory usage
- **Logs Viewer**: Real-time system and trade logs
- **Alerts**: Notifications for important events

## Learning System

### How It Learns

#### 1. Pattern Recognition
- Identifies successful trade patterns across strategies
- Recognizes market conditions that favor certain approaches
- Detects correlations between news sentiment and price movements
- Learns from both winning and losing trades

#### 2. Parameter Tuning
- Automatically adjusts strategy parameters
- Optimizes entry and exit thresholds
- Fine-tunes stop-loss and take-profit levels
- Adapts position sizing based on volatility

#### 3. Market Regime Detection
- Identifies different market conditions (trending, ranging, volatile)
- Adapts strategy selection to current regime
- Recognizes regime changes early
- Adjusts risk parameters accordingly

#### 4. Risk Management Learning
- Learns optimal position sizing for different scenarios
- Adjusts exposure based on portfolio performance
- Implements dynamic stop-loss strategies
- Balances risk-reward ratios

#### 5. Strategy Evolution
- Combines successful elements from multiple strategies
- Mutates parameters to explore new possibilities
- Selects fittest strategies for deployment
- Maintains diversity in strategy pool

### Learning Cycle

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   Data Collection → Strategy Generation → Backtesting       │
│         ↑                                      ↓            │
│         │                              Shadow Trading        │
│         │                                      ↓            │
│   Repeat ← Outcome Analysis ← Live Trading ← Optimization   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Continuous Improvement Schedule

| Activity | Frequency | Description |
|----------|-----------|-------------|
| Data Collection | Real-time | Fetches prices, news, market data |
| Shadow Trades | Continuous | Simulates trades in real-time |
| Strategy Generation | Daily | Creates new strategy variations |
| Backtesting | Daily | Tests on historical data |
| Optimization | Every 6 hours | Tunes parameters based on performance |
| Performance Review | Daily | Comprehensive analysis |
| Strategy Deployment | As needed | Promotes/retires strategies |

**Key Point**: The system runs 24/7, continuing to learn and optimize even when markets are closed (backtesting, optimization, strategy generation).

## API Integration

### Trading 212

Based on official Trading 212 API specifications (https://github.com/trading212-labs/agent-skills):

#### Supported Endpoints
- **Demo Environment**: For testing without real money
- **Live Environment**: For actual trading

#### Account Types
- **Invest Account**: Standard investment account
- **Stocks ISA**: Tax-efficient Individual Savings Account

#### Operations
- Get portfolio positions
- Place orders (Market, Limit, Stop)
- Cancel pending orders
- Get order history
- Check account balance
- Get instrument details

#### Authentication
- API Key-based authentication
- Secure token management
- Automatic token refresh

### Yahoo Finance

#### Data Available
- Real-time stock prices
- Historical OHLCV data (Open, High, Low, Close, Volume)
- Company information and fundamentals
- Market indices
- Currency exchange rates
- Cryptocurrency prices

#### Update Frequency
- Real-time during market hours
- Delayed for some markets
- End-of-day updates for historical data

### News Sentiment

#### Sources
- Yahoo Finance News
- Google News RSS feeds
- Financial news aggregators

#### Processing
- Article collection and deduplication
- Sentiment analysis (positive/negative/neutral)
- Relevance scoring to portfolio holdings
- Impact assessment on trading decisions

### Optional Premium Providers

Users can add their own API keys for enhanced data:

#### EODHD (End-of-Day Historical Data)
- Extended historical data
- Fundamental data
- Economic calendar
- Insider transactions

#### FinHub (Financial Data)
- Real-time data
- Options data
- Crypto data
- Forex data

#### Alpha Vantage
- Technical indicators
- Crypto currencies
- Forex
- Commodities

## File Structure

```
trading-bot-app/
│
├── src/
│   ├── main.py                 # Main orchestrator - starts all components
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management, env variables
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── providers.py        # Data fetchers (Yahoo, News, Premium)
│   │   └── cache.py            # Data caching and management
│   │
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py    # Base strategy class
│   │   ├── strategy_lab.py     # Strategy generation & optimization
│   │   ├── momentum.py         # Momentum strategies
│   │   ├── mean_reversion.py   # Mean reversion strategies
│   │   ├── breakout.py         # Breakout strategies
│   │   └── ml_strategies.py    # Machine learning strategies
│   │
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── engine.py           # Trade execution engine
│   │   ├── trading212.py       # Trading 212 API client
│   │   ├── shadow_engine.py    # Shadow trading simulator
│   │   └── order_manager.py    # Order lifecycle management
│   │
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── optimizer.py        # Learning & optimization engine
│   │   ├── pattern_recognition.py  # Pattern detection
│   │   └── performance_analyzer.py # Performance analysis
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── app.py              # Flask web application
│   │   ├── routes.py           # API routes
│   │   └── templates/          # HTML templates
│   │       ├── index.html
│   │       ├── dashboard.html
│   │       └── strategies.html
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py          # Utility functions
│       ├── logging_config.py   # Logging setup
│       └── security.py         # Security utilities
│
├── storage/
│   ├── strategies/             # Saved strategy JSON files
│   ├── logs/                   # System and trade logs
│   ├── data/                   # Cached market data
│   └── models/                 # Trained ML models
│
├── config/
│   └── .env                    # Environment configuration
│
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment file
├── README.md                   # This documentation
└── LICENSE                     # MIT License
```

## Safety & Risk Management

### ⚠️ Important Disclaimers

**This software is provided for educational and personal use only:**

- Past performance does not guarantee future results
- Trading involves substantial risk of loss
- Always test thoroughly in shadow mode before live trading
- Never invest money you cannot afford to lose
- This is not financial advice
- You are responsible for your own trading decisions
- Consult with a financial advisor before making investment decisions

### Built-in Safeguards

#### Position Limits
- Maximum position size as percentage of portfolio
- Maximum number of open positions
- Maximum exposure per sector/industry

#### Loss Limits
- Daily loss limit (trading pauses if exceeded)
- Per-trade stop-loss enforcement
- Maximum drawdown threshold

#### Risk Controls
- Position sizing based on volatility
- Diversification requirements
- Correlation checks

#### Operational Safeguards
- Shadow mode validation before live deployment
- Minimum backtest period requirement
- Performance thresholds for live deployment
- Emergency stop functionality

#### Audit Trail
- Comprehensive logging of all trades
- Strategy change history
- Performance tracking
- Error logging and alerting

## Performance Optimization

### Tips for Best Results

1. **Start in Shadow Mode**
   - Run for at least 2-4 weeks before considering live trading
   - Build confidence in strategy performance
   - Allow system to learn and optimize

2. **Gradual Live Deployment**
   - Start with small position sizes
   - Monitor closely in first weeks
   - Increase exposure gradually as confidence builds

3. **Regular Monitoring**
   - Check dashboard daily
   - Review weekly performance reports
   - Adjust parameters based on comfort level

4. **Continuous Learning**
   - Keep system running 24/7 for best results
   - Allow overnight optimization cycles
   - Review strategy updates regularly

5. **Risk Management**
   - Set conservative limits initially
   - Adjust based on personal risk tolerance
   - Never exceed comfortable exposure levels

6. **Stay Informed**
   - Monitor market conditions
   - Review news sentiment impact
   - Understand strategy logic

## Troubleshooting

### Common Issues

#### No Data Appearing in Dashboard
**Solution:**
- Verify main.py is running
- Check internet connectivity
- Test Yahoo Finance access manually
- Review logs in `storage/logs/`

#### Trading 212 API Errors
**Solution:**
- Verify API key is correct and active
- Ensure account type matches (ISA vs Invest)
- Check demo/live environment setting
- Confirm API access enabled in Trading 212 account
- Review API rate limits

#### High Memory Usage
**Solution:**
- Reduce backtest period in settings
- Clear old data cache: `rm -rf storage/data/*`
- Restart application periodically
- Limit number of concurrent strategies

#### Slow Dashboard Performance
**Solution:**
- Reduce data refresh frequency
- Limit historical data range in charts
- Clear browser cache
- Check system resources

#### Strategies Not Generating
**Solution:**
- Verify sufficient historical data available
- Check strategy lab logs
- Ensure optimization interval hasn't passed
- Review minimum data requirements

### Log Locations

- System logs: `storage/logs/system.log`
- Trade logs: `storage/logs/trades.log`
- Strategy logs: `storage/logs/strategies.log`
- Error logs: `storage/logs/errors.log`

## Updates & Maintenance

### Updating Strategies

Strategies auto-update every 6 hours. To manually trigger:

```bash
python src/strategies/strategy_lab.py --force-optimize
```

### Clearing Cache

```bash
# Clear data cache
rm -rf storage/data/*

# Clear old logs
rm -rf storage/logs/*

# Clear all cached data
python src/utils/clear_cache.py
```

### Backup Strategies

```bash
# Backup all strategies
cp -r storage/strategies /backup/location/strategies_$(date +%Y%m%d)

# Backup entire storage
cp -r storage /backup/location/storage_$(date +%Y%m%d)
```

### System Updates

Check for updates regularly:
```bash
git pull origin main  # If using git
pip install --upgrade -r requirements.txt
```

## Advanced Configuration

### Custom Strategies

Add custom strategies in `src/strategies/`:

```python
from strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, params):
        super().__init__(params)
    
    def generate_signal(self, data):
        # Your strategy logic here
        pass
    
    def calculate_position_size(self, portfolio):
        # Your position sizing logic here
        pass
```

### Custom Data Providers

Extend data providers in `src/data/providers.py`:

```python
class CustomDataProvider:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_price(self, symbol):
        # Your data fetching logic here
        pass
```

### Dashboard Customization

Modify dashboard in `src/dashboard/app.py` and templates in `src/dashboard/templates/`

## Support & Development

This is a personal use project. For custom modifications:

- Edit `src/config/settings.py` for default configurations
- Add custom strategies in `src/strategies/`
- Extend data providers in `src/data/providers.py`
- Customize dashboard in `src/dashboard/app.py`
- Review code comments for implementation details

## Contributing

For personal use, feel free to modify as needed. Key areas for extension:

1. New strategy types
2. Additional data sources
3. Enhanced machine learning models
4. Improved risk management
5. Dashboard enhancements

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Final Notes

🎯 **Remember**: This system is designed to learn and improve continuously. Give it time to build its strategy library and optimize performance. Start in shadow mode, be patient, and always prioritize risk management.

📈 **Success Formula**: Shadow Testing + Continuous Learning + Gradual Live Deployment + Strict Risk Management = Best Chance of Success

💡 **Pro Tip**: The system learns most effectively when running 24/7. Consider deploying on a VPS or cloud server for uninterrupted operation.

⚠️ **Critical**: Never trade with money you cannot afford to lose. Always understand the risks involved in trading.

---

**Happy Trading! Trade responsibly and may your strategies be profitable!**
