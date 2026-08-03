"""
Flask Web Dashboard for Trading Bot
Real-time monitoring and control interface
"""
from flask import Flask, render_template_string, jsonify, request
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# HTML Template for Dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 { font-size: 2em; color: #00d9ff; }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-running { background: #00c853; color: #000; }
        .status-stopped { background: #ff5252; color: #fff; }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h3 { 
            color: #00d9ff; 
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child { border-bottom: none; }
        .metric-value { 
            font-weight: bold; 
            font-size: 1.2em;
        }
        .positive { color: #00c853; }
        .negative { color: #ff5252; }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin: 5px;
            transition: all 0.3s;
        }
        .btn-primary { background: #00d9ff; color: #000; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-success { background: #00c853; color: #000; }
        .btn:hover { transform: translateY(-2px); opacity: 0.9; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th { color: #00d9ff; }
        tr:hover { background: rgba(255,255,255,0.05); }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d9ff, #00c853);
            transition: width 0.5s;
        }
        #lastUpdate { color: #888; font-size: 0.9em; }
        .refresh-btn { 
            background: transparent; 
            border: 1px solid #00d9ff;
            color: #00d9ff;
            padding: 5px 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🤖 Trading Bot Dashboard</h1>
                <p id="lastUpdate">Last updated: --</p>
            </div>
            <div>
                <span id="modeBadge" class="status-badge status-running">Shadow Mode</span>
                <button class="btn refresh-btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
        </header>

        <div class="grid">
            <!-- Shadow Portfolio -->
            <div class="card">
                <h3>📊 Shadow Portfolio</h3>
                <div class="metric">
                    <span>Initial Capital:</span>
                    <span class="metric-value">$100,000</span>
                </div>
                <div class="metric">
                    <span>Current Value:</span>
                    <span class="metric-value" id="shadowValue">$--</span>
                </div>
                <div class="metric">
                    <span>Total Return:</span>
                    <span class="metric-value" id="shadowReturn">--%</span>
                </div>
                <div class="metric">
                    <span>Positions:</span>
                    <span class="metric-value" id="shadowPositions">0</span>
                </div>
                <div class="metric">
                    <span>Trades Today:</span>
                    <span class="metric-value" id="shadowTrades">0</span>
                </div>
            </div>

            <!-- Strategy Lab -->
            <div class="card">
                <h3>🧪 Strategy Lab</h3>
                <div class="metric">
                    <span>Total Strategies:</span>
                    <span class="metric-value" id="totalStrategies">0</span>
                </div>
                <div class="metric">
                    <span>Best Sharpe Ratio:</span>
                    <span class="metric-value" id="bestSharpe">--</span>
                </div>
                <div class="metric">
                    <span>Best Return:</span>
                    <span class="metric-value" id="bestReturn">--%</span>
                </div>
                <div class="metric">
                    <span>Last Optimization:</span>
                    <span class="metric-value" id="lastOptimization">--</span>
                </div>
            </div>

            <!-- System Status -->
            <div class="card">
                <h3>⚙️ System Status</h3>
                <div class="metric">
                    <span>Mode:</span>
                    <span class="metric-value" id="systemMode">Shadow</span>
                </div>
                <div class="metric">
                    <span>Data Provider:</span>
                    <span class="metric-value">Yahoo Finance</span>
                </div>
                <div class="metric">
                    <span>Watchlist Size:</span>
                    <span class="metric-value" id="watchlistSize">0</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="metric-value" id="uptime">--</span>
                </div>
            </div>

            <!-- Controls -->
            <div class="card">
                <h3>🎮 Controls</h3>
                <button class="btn btn-success" onclick="startTrading()">▶ Start</button>
                <button class="btn btn-danger" onclick="stopTrading()">⏹ Stop</button>
                <button class="btn btn-primary" onclick="optimizeStrategies()">🔬 Optimize</button>
                <button class="btn btn-primary" onclick="generateStrategies()">➕ Generate</button>
            </div>
        </div>

        <!-- Top Strategies -->
        <div class="card">
            <h3>🏆 Top Performing Strategies</h3>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Return %</th>
                        <th>Sharpe</th>
                        <th>Max DD %</th>
                        <th>Trades</th>
                    </tr>
                </thead>
                <tbody id="strategiesTable">
                    <tr><td colspan="5">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Recent Trades -->
        <div class="card" style="margin-top: 20px;">
            <h3>📈 Recent Shadow Trades</h3>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Symbol</th>
                        <th>Shares</th>
                        <th>Price</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="tradesTable">
                    <tr><td colspan="5">No trades yet</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => updateDashboard(data));
        }

        function updateDashboard(data) {
            document.getElementById('lastUpdate').textContent = 
                'Last updated: ' + new Date().toLocaleTimeString();
            
            // Shadow Portfolio
            if (data.shadow_performance) {
                const perf = data.shadow_performance;
                document.getElementById('shadowValue').textContent = 
                    '$' + perf.current_value.toLocaleString(undefined, {maximumFractionDigits: 2});
                
                const returnEl = document.getElementById('shadowReturn');
                returnEl.textContent = perf.total_return_pct.toFixed(2) + '%';
                returnEl.className = 'metric-value ' + (perf.total_return_pct >= 0 ? 'positive' : 'negative');
                
                document.getElementById('shadowPositions').textContent = perf.position_count;
                document.getElementById('shadowTrades').textContent = perf.trade_count;
            }

            // Strategy Lab
            if (data.strategy_stats) {
                document.getElementById('totalStrategies').textContent = data.strategy_stats.total_strategies;
                document.getElementById('bestSharpe').textContent = data.strategy_stats.best_sharpe || '--';
                
                const bestReturnEl = document.getElementById('bestReturn');
                bestReturnEl.textContent = (data.strategy_stats.best_return || 0).toFixed(2) + '%';
                bestReturnEl.className = 'metric-value ' + ((data.strategy_stats.best_return || 0) >= 0 ? 'positive' : 'negative');
            }

            // System
            document.getElementById('systemMode').textContent = data.mode || 'Shadow';
            document.getElementById('watchlistSize').textContent = data.watchlist_size || 0;

            // Strategies Table
            if (data.top_strategies && data.top_strategies.length > 0) {
                let html = '';
                data.top_strategies.slice(0, 10).forEach(s => {
                    const p = s.performance || {};
                    html += `
                        <tr>
                            <td>${s.name}</td>
                            <td class="${(p.total_return_pct || 0) >= 0 ? 'positive' : 'negative'}">
                                ${(p.total_return_pct || 0).toFixed(2)}%
                            </td>
                            <td>${(p.sharpe_ratio || 0).toFixed(2)}</td>
                            <td class="negative">${(p.max_drawdown_pct || 0).toFixed(2)}%</td>
                            <td>${p.trade_count || 0}</td>
                        </tr>
                    `;
                });
                document.getElementById('strategiesTable').innerHTML = html;
            }

            // Trades Table
            if (data.recent_trades && data.recent_trades.length > 0) {
                let html = '';
                data.recent_trades.slice(-10).reverse().forEach(t => {
                    html += `
                        <tr>
                            <td class="${t.type === 'buy' ? 'positive' : 'negative'}">${t.type.toUpperCase()}</td>
                            <td>${t.symbol}</td>
                            <td>${t.shares}</td>
                            <td>$${t.price?.toFixed(2) || '--'}</td>
                            <td>${new Date(t.timestamp).toLocaleTimeString()}</td>
                        </tr>
                    `;
                });
                document.getElementById('tradesTable').innerHTML = html;
            }
        }

        function startTrading() { fetch('/api/start', {method: 'POST'}).then(refreshData); }
        function stopTrading() { fetch('/api/stop', {method: 'POST'}).then(refreshData); }
        function optimizeStrategies() { fetch('/api/optimize', {method: 'POST'}).then(refreshData); }
        function generateStrategies() { fetch('/api/generate', {method: 'POST'}).then(refreshData); }

        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
        refreshData();
    </script>
</body>
</html>
"""


class DashboardApp:
    """Flask dashboard application."""
    
    def __init__(self, settings, orchestrator=None):
        self.settings = settings
        self.orchestrator = orchestrator
        self.app = Flask(__name__)
        self.start_time = datetime.now()
        
        self._setup_routes()
        logger.info("Initialized Dashboard App")
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/status')
        def get_status():
            """Get current system status."""
            status = {
                'mode': self.settings.MODE,
                'watchlist_size': len(self.settings.WATCHLIST),
                'uptime': str(datetime.now() - self.start_time),
                'shadow_performance': {},
                'strategy_stats': {},
                'top_strategies': [],
                'recent_trades': []
            }
            
            # Get shadow performance if available
            if self.orchestrator and hasattr(self.orchestrator, 'shadow_engine'):
                try:
                    status['shadow_performance'] = self.orchestrator.shadow_engine.get_performance()
                    
                    # Get recent trades
                    trade_history = self.orchestrator.shadow_engine.portfolio.trade_history
                    status['recent_trades'] = trade_history[-20:] if trade_history else []
                except Exception as e:
                    logger.error(f"Error getting shadow performance: {str(e)}")
            
            # Get strategy stats
            if self.orchestrator and hasattr(self.orchestrator, 'strategy_lab'):
                try:
                    strategies = self.orchestrator.strategy_lab.load_strategies()
                    status['strategy_stats'] = {
                        'total_strategies': len(strategies),
                        'best_sharpe': None,
                        'best_return': None
                    }
                    
                    if strategies:
                        best_sharpe = max(strategies, key=lambda x: x.get('performance', {}).get('sharpe_ratio', 0))
                        best_return = max(strategies, key=lambda x: x.get('performance', {}).get('total_return', 0))
                        
                        status['strategy_stats']['best_sharpe'] = f"{best_sharpe['performance'].get('sharpe_ratio', 0):.2f}"
                        status['strategy_stats']['best_return'] = best_return['performance'].get('total_return', 0) * 100
                    
                    status['top_strategies'] = sorted(
                        strategies,
                        key=lambda x: x.get('performance', {}).get('sharpe_ratio', 0),
                        reverse=True
                    )[:10]
                except Exception as e:
                    logger.error(f"Error getting strategy stats: {str(e)}")
            
            return jsonify(status)
        
        @self.app.route('/api/start', methods=['POST'])
        def start_trading():
            """Start trading."""
            if self.orchestrator:
                self.orchestrator.start()
            return jsonify({'status': 'started'})
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_trading():
            """Stop trading."""
            if self.orchestrator:
                self.orchestrator.stop()
            return jsonify({'status': 'stopped'})
        
        @self.app.route('/api/optimize', methods=['POST'])
        def optimize():
            """Trigger strategy optimization."""
            if self.orchestrator and hasattr(self.orchestrator, 'strategy_lab'):
                count = self.orchestrator.strategy_lab.optimize_strategies()
                return jsonify({'status': 'optimized', 'count': count})
            return jsonify({'status': 'error', 'message': 'No orchestrator'})
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate():
            """Generate new strategies."""
            if self.orchestrator and hasattr(self.orchestrator, 'strategy_lab'):
                strategies = self.orchestrator.strategy_lab.generate_strategies()
                return jsonify({'status': 'generated', 'count': len(strategies)})
            return jsonify({'status': 'error', 'message': 'No orchestrator'})
    
    def run(self, host=None, port=None, debug=None):
        """Run the dashboard."""
        host = host or self.settings.DASHBOARD_HOST
        port = port or self.settings.DASHBOARD_PORT
        debug = debug if debug is not None else self.settings.DASHBOARD_DEBUG
        
        logger.info(f"Starting dashboard on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
