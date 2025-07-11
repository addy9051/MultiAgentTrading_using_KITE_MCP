"""
Enhanced Web Interface for the 7-Agent Trading System
Showcases TauricResearch/TradingAgents architecture
"""

import asyncio
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from config.settings import Settings
from services.enhanced_trading_orchestrator import EnhancedTradingOrchestrator
from services.kite_mcp_client import KiteMCPClient
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

app = Flask(__name__)

# Global variables
orchestrator = None
latest_results = {}
system_status = "initializing"

def setup_system():
    """Initialize the enhanced trading system"""
    global orchestrator, system_status
    try:
        logger.info("Initializing enhanced trading system...")
        
        # Load settings
        settings = Settings()
        
        # Initialize Kite MCP client
        kite_client = KiteMCPClient(settings)
        
        # Initialize client in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(kite_client.initialize())
        
        # Create enhanced orchestrator
        orchestrator = EnhancedTradingOrchestrator(settings, kite_client)
        
        system_status = "ready"
        logger.info("Enhanced trading system initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing enhanced system: {str(e)}")
        system_status = f"error: {str(e)}"

@app.route('/')
def index():
    """Enhanced dashboard"""
    return render_template('enhanced_dashboard.html')

@app.route('/status')
def get_status():
    """Get enhanced system status"""
    global system_status, orchestrator
    
    status_data = {
        "status": system_status,
        "timestamp": datetime.now().isoformat(),
        "architecture": "TauricResearch 7-Agent System",
        "stages": 5,
        "agents": [
            "Market Data Agent",
            "Technical Analysis Agent", 
            "Fundamentals Analyst",
            "Sentiment Analyst",
            "News Analyst",
            "Bull Researcher",
            "Bear Researcher",
            "Signal Generation Agent",
            "Risk Assessment Agent",
            "Portfolio Manager"
        ]
    }
    
    if orchestrator:
        status_data.update(orchestrator.get_system_status())
    
    return jsonify(status_data)

@app.route('/run_analysis', methods=['POST'])
def run_analysis():
    """Run enhanced trading analysis"""
    global orchestrator, latest_results, system_status
    
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 500
        
        if system_status != "ready":
            return jsonify({"error": f"System not ready: {system_status}"}), 500
        
        # Get symbol from request
        symbol = request.json.get('symbol', 'RELIANCE') if request.json else 'RELIANCE'
        
        # Run analysis in background thread
        def run_async_analysis():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the analysis
                async def analyze():
                    global latest_results
                    results = await orchestrator.run_trading_cycle(symbol)
                    latest_results = results
                    return results
                
                # Execute analysis
                loop.run_until_complete(analyze())
                
            except Exception as e:
                logger.error(f"Error in async analysis: {str(e)}")
                global latest_results
                latest_results = {"error": str(e)}
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=run_async_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({
            "status": "started",
            "message": f"Enhanced analysis started for {symbol}",
            "estimated_time": "10-15 seconds"
        })
        
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def get_results():
    """Get latest enhanced analysis results"""
    global latest_results
    
    if not latest_results:
        return jsonify({"message": "No results available yet"})
    
    return jsonify(latest_results)

@app.route('/agent_summary')
def get_agent_summary():
    """Get agent-specific summary"""
    global latest_results
    
    if not latest_results:
        return jsonify({"message": "No results available"})
    
    # Extract key information for each agent
    summary = {
        "market_data": latest_results.get("market_data", {}),
        "technical_analysis": latest_results.get("technical_analysis", {}),
        "fundamentals": latest_results.get("fundamentals_analysis", {}),
        "sentiment": latest_results.get("sentiment_analysis", {}),
        "news": latest_results.get("news_analysis", {}),
        "bull_research": latest_results.get("bull_research", {}),
        "bear_research": latest_results.get("bear_research", {}),
        "signals": latest_results.get("trading_signals", {}),
        "risk": latest_results.get("risk_assessment", {}),
        "portfolio": latest_results.get("portfolio_decision", {}),
        "execution": latest_results.get("execution_result", {}),
        "messages": latest_results.get("messages", [])
    }
    
    return jsonify(summary)

# Create enhanced dashboard template
def create_enhanced_template():
    """Create enhanced dashboard template"""
    template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Multi-Agent Trading System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #0f3460;
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            color: #a0a0a0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .system-status {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid #0f3460;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .status-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .status-item h3 {
            color: #00d4ff;
            margin-bottom: 5px;
        }
        
        .controls {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .btn {
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .result-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        
        .result-card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .result-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .result-item:last-child {
            border-bottom: none;
        }
        
        .result-label {
            font-weight: bold;
            color: #a0a0a0;
        }
        
        .result-value {
            color: #ffffff;
        }
        
        .positive {
            color: #00ff88;
        }
        
        .negative {
            color: #ff4444;
        }
        
        .neutral {
            color: #ffaa00;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #00d4ff;
        }
        
        .error {
            background: rgba(255, 68, 68, 0.2);
            border: 1px solid #ff4444;
            color: #ff4444;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .agent-workflow {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .workflow-stages {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        
        .stage {
            background: rgba(0, 212, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.9em;
        }
        
        .stage h4 {
            color: #00d4ff;
            margin-bottom: 5px;
        }
        
        @media (max-width: 768px) {
            .workflow-stages {
                grid-template-columns: 1fr;
            }
            
            .results-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enhanced Multi-Agent Trading System</h1>
        <p>TauricResearch/TradingAgents Architecture - 7 Agents, 5 Stages</p>
    </div>
    
    <div class="container">
        <div class="system-status">
            <h2>System Status</h2>
            <div class="status-grid">
                <div class="status-item">
                    <h3>Status</h3>
                    <div id="system-status">Loading...</div>
                </div>
                <div class="status-item">
                    <h3>Architecture</h3>
                    <div id="architecture">TauricResearch 7-Agent</div>
                </div>
                <div class="status-item">
                    <h3>Stages</h3>
                    <div id="stages">5-Stage Workflow</div>
                </div>
                <div class="status-item">
                    <h3>Last Analysis</h3>
                    <div id="last-analysis">None</div>
                </div>
            </div>
        </div>
        
        <div class="agent-workflow">
            <h2>Agent Workflow</h2>
            <div class="workflow-stages">
                <div class="stage">
                    <h4>Stage I</h4>
                    <div>Analyst Team</div>
                    <small>Market Data, Technical, Fundamentals, Sentiment, News</small>
                </div>
                <div class="stage">
                    <h4>Stage II</h4>
                    <div>Research Team</div>
                    <small>Bull vs Bear Debate</small>
                </div>
                <div class="stage">
                    <h4>Stage III</h4>
                    <div>Trading Signals</div>
                    <small>Signal Generation</small>
                </div>
                <div class="stage">
                    <h4>Stage IV</h4>
                    <div>Risk Management</div>
                    <small>Risk Assessment</small>
                </div>
                <div class="stage">
                    <h4>Stage V</h4>
                    <div>Portfolio Manager</div>
                    <small>Final Decision</small>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="runAnalysis()">Run Enhanced Analysis</button>
            <button class="btn" onclick="getResults()">Get Results</button>
            <button class="btn" onclick="refreshStatus()">Refresh Status</button>
        </div>
        
        <div id="results-container">
            <div class="loading">Ready to run enhanced analysis...</div>
        </div>
    </div>
    
    <script>
        let analysisRunning = false;
        
        // Auto-refresh status
        setInterval(refreshStatus, 5000);
        
        // Initial status load
        refreshStatus();
        
        function refreshStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('system-status').textContent = data.status;
                    document.getElementById('architecture').textContent = data.architecture || 'TauricResearch 7-Agent';
                    document.getElementById('stages').textContent = data.stages + '-Stage Workflow' || '5-Stage Workflow';
                    document.getElementById('last-analysis').textContent = data.latest_symbol || 'None';
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                    document.getElementById('system-status').textContent = 'Error';
                });
        }
        
        function runAnalysis() {
            if (analysisRunning) return;
            
            analysisRunning = true;
            const btn = document.querySelector('.btn');
            btn.disabled = true;
            btn.textContent = 'Running Analysis...';
            
            document.getElementById('results-container').innerHTML = 
                '<div class="loading">Running enhanced 7-agent analysis...</div>';
            
            fetch('/run_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({symbol: 'RELIANCE'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Poll for results
                setTimeout(() => {
                    pollForResults();
                }, 2000);
            })
            .catch(error => {
                document.getElementById('results-container').innerHTML = 
                    '<div class="error">Error: ' + error.message + '</div>';
                analysisRunning = false;
                btn.disabled = false;
                btn.textContent = 'Run Enhanced Analysis';
            });
        }
        
        function pollForResults() {
            fetch('/results')
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // Still processing
                        setTimeout(pollForResults, 2000);
                        return;
                    }
                    
                    displayResults(data);
                    analysisRunning = false;
                    const btn = document.querySelector('.btn');
                    btn.disabled = false;
                    btn.textContent = 'Run Enhanced Analysis';
                })
                .catch(error => {
                    console.error('Error polling results:', error);
                    setTimeout(pollForResults, 2000);
                });
        }
        
        function getResults() {
            fetch('/results')
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        document.getElementById('results-container').innerHTML = 
                            '<div class="loading">' + data.message + '</div>';
                        return;
                    }
                    displayResults(data);
                })
                .catch(error => {
                    document.getElementById('results-container').innerHTML = 
                        '<div class="error">Error: ' + error.message + '</div>';
                });
        }
        
        function displayResults(data) {
            const market = data.market_data || {};
            const fundamentals = data.fundamentals_analysis || {};
            const sentiment = data.sentiment_analysis || {};
            const news = data.news_analysis || {};
            const bull = data.bull_research || {};
            const bear = data.bear_research || {};
            const signals = data.trading_signals || {};
            const risk = data.risk_assessment || {};
            const portfolio = data.portfolio_decision || {};
            
            const html = `
                <div class="results-grid">
                    <div class="result-card">
                        <h3>📊 Market Data</h3>
                        <div class="result-item">
                            <span class="result-label">Symbol:</span>
                            <span class="result-value">${data.symbol || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Price:</span>
                            <span class="result-value">$${(market.current_price || 0).toFixed(2)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Volume:</span>
                            <span class="result-value">${(market.volume || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Trend:</span>
                            <span class="result-value">${market.trend || 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>📈 Fundamentals</h3>
                        <div class="result-item">
                            <span class="result-label">Health:</span>
                            <span class="result-value">${fundamentals.financial_health || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Valuation:</span>
                            <span class="result-value">${fundamentals.valuation_assessment || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Target:</span>
                            <span class="result-value">$${(fundamentals.price_target || 0).toFixed(2)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Recommendation:</span>
                            <span class="result-value">${fundamentals.recommendation || 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>🗣️ Sentiment</h3>
                        <div class="result-item">
                            <span class="result-label">Overall:</span>
                            <span class="result-value ${sentiment.overall_sentiment === 'bullish' ? 'positive' : sentiment.overall_sentiment === 'bearish' ? 'negative' : 'neutral'}">${sentiment.overall_sentiment || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Score:</span>
                            <span class="result-value">${(sentiment.sentiment_score || 0).toFixed(2)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Social Buzz:</span>
                            <span class="result-value">${sentiment.social_media_buzz || 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>📰 News</h3>
                        <div class="result-item">
                            <span class="result-label">Sentiment:</span>
                            <span class="result-value ${news.overall_news_sentiment === 'positive' ? 'positive' : news.overall_news_sentiment === 'negative' ? 'negative' : 'neutral'}">${news.overall_news_sentiment || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Impact:</span>
                            <span class="result-value">${news.market_moving_potential || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Recommendation:</span>
                            <span class="result-value">${news.trading_recommendation || 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>🐂 Bull Research</h3>
                        <div class="result-item">
                            <span class="result-label">Upside:</span>
                            <span class="result-value positive">${bull.upside_potential || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Action:</span>
                            <span class="result-value">${bull.recommended_action || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Confidence:</span>
                            <span class="result-value">${bull.confidence_level || 0}%</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>🐻 Bear Research</h3>
                        <div class="result-item">
                            <span class="result-label">Downside:</span>
                            <span class="result-value negative">${bear.downside_potential || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Action:</span>
                            <span class="result-value">${bear.recommended_action || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Confidence:</span>
                            <span class="result-value">${bear.confidence_level || 0}%</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>🎯 Portfolio Decision</h3>
                        <div class="result-item">
                            <span class="result-label">Decision:</span>
                            <span class="result-value ${portfolio.final_decision === 'BUY' ? 'positive' : portfolio.final_decision === 'SELL' ? 'negative' : 'neutral'}">${portfolio.final_decision || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Position:</span>
                            <span class="result-value">${portfolio.position_size || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Risk-Reward:</span>
                            <span class="result-value">${(portfolio.risk_reward_ratio || 0).toFixed(2)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Confidence:</span>
                            <span class="result-value">${portfolio.confidence_level || 0}%</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3>⚠️ Risk Assessment</h3>
                        <div class="result-item">
                            <span class="result-label">Risk Level:</span>
                            <span class="result-value">${risk.risk_level || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Approval:</span>
                            <span class="result-value">${risk.trade_approval || 'N/A'}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Position Size:</span>
                            <span class="result-value">${risk.recommended_position_size || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('results-container').innerHTML = html;
        }
    </script>
</body>
</html>
    """
    
    # Ensure templates directory exists
    import os
    os.makedirs('templates', exist_ok=True)
    
    # Write template
    with open('templates/enhanced_dashboard.html', 'w') as f:
        f.write(template_content)

if __name__ == '__main__':
    # Create enhanced template
    create_enhanced_template()
    
    # Setup system
    setup_system()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)