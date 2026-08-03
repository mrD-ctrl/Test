import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-blue-400">Trading212 Smart Bot</h1>
        <p className="text-slate-400 text-sm">AI-Powered Trading for ISA & Invest Accounts</p>
      </header>
      
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Portfolio Summary Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold mb-4">Portfolio Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Total Value</span>
                <span className="font-mono">£10,245.67</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Today's P&L</span>
                <span className="text-green-400">+£124.50 (+1.23%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Account Type</span>
                <span className="text-blue-400">ISA</span>
              </div>
            </div>
          </div>

          {/* ML Signal Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold mb-4">AI Trading Signals</h2>
            <div className="space-y-3">
              <div className="bg-slate-700 rounded p-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">AAPL</span>
                  <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-sm">BUY</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">Confidence: 78%</p>
              </div>
              <div className="bg-slate-700 rounded p-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">TSLA</span>
                  <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-sm">HOLD</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">Confidence: 65%</p>
              </div>
            </div>
          </div>

          {/* License Info Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold mb-4">License Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Tier</span>
                <span className="text-purple-400 font-medium">Pro</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Status</span>
                <span className="text-green-400">Active</span>
              </div>
              <div className="text-xs text-slate-500 mt-4">
                One-time purchase - No subscription required
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-8 bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold mb-6">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-700/50 rounded">
              <div className="text-blue-400 mb-2">🤖</div>
              <h3 className="font-medium mb-1">Self-Learning AI</h3>
              <p className="text-sm text-slate-400">Continuously improves trading strategies through ML</p>
            </div>
            <div className="p-4 bg-slate-700/50 rounded">
              <div className="text-green-400 mb-2">📊</div>
              <h3 className="font-medium mb-1">Multi-Source Data</h3>
              <p className="text-sm text-slate-400">Yahoo Finance, Google News + optional premium APIs</p>
            </div>
            <div className="p-4 bg-slate-700/50 rounded">
              <div className="text-purple-400 mb-2">🛡️</div>
              <h3 className="font-medium mb-1">Risk Management</h3>
              <p className="text-sm text-slate-400">Automatic stop-loss, position sizing, drawdown protection</p>
            </div>
            <div className="p-4 bg-slate-700/50 rounded">
              <div className="text-yellow-400 mb-2">🇬🇧</div>
              <h3 className="font-medium mb-1">ISA Optimized</h3>
              <p className="text-sm text-slate-400">Tax-efficient trading for UK ISA accounts</p>
            </div>
          </div>
        </div>

        {/* Pricing Tiers */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-6 text-center">One-Time Purchase Options</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-xl font-bold mb-2">Basic</h3>
              <div className="text-3xl font-bold text-blue-400 mb-4">£99</div>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>✓ Single account</li>
                <li>✓ Yahoo Finance data</li>
                <li>✓ Basic strategies</li>
                <li>✓ Manual execution</li>
                <li>✗ Auto-trading</li>
              </ul>
            </div>
            <div className="bg-gradient-to-b from-purple-900/50 to-slate-800 rounded-lg p-6 border-2 border-purple-500">
              <div className="absolute top-0 right-0 bg-purple-500 text-white px-3 py-1 rounded-bl-lg text-sm font-medium">Popular</div>
              <h3 className="text-xl font-bold mb-2">Pro</h3>
              <div className="text-3xl font-bold text-purple-400 mb-4">£199</div>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>✓ Unlimited accounts</li>
                <li>✓ All free data sources</li>
                <li>✓ ML optimization</li>
                <li>✓ Auto-execution</li>
                <li>✓ Backtesting module</li>
              </ul>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-xl font-bold mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-yellow-400 mb-4">£399</div>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>✓ Everything in Pro</li>
                <li>✓ Premium API support</li>
                <li>✓ Custom strategies</li>
                <li>✓ Priority support</li>
                <li>✓ White-label options</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <p className="text-sm text-yellow-200">
            <strong>⚠️ Risk Warning:</strong> Trading involves significant risk of loss. Past performance does not guarantee future results. 
            This software is for educational purposes only and does not constitute financial advice. Always comply with FCA regulations 
            and Trading212 terms of service.
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
