#!/usr/bin/env python3
"""
Web interface for the Multi-Agent Trading System
"""

import asyncio
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from config.settings import Settings
from services.trading_orchestrator import TradingOrchestrator
from utils.logging_config import setup_logging
import threading

app = Flask(__name__)

# Global variables
orchestrator = None
current_results = {}
system_status = "initializing"

def setup_system():
    """Initialize the trading system"""
    global orchestrator, system_status
    
    try:
        setup_logging()
        settings = Settings()
        orchestrator = TradingOrchestrator(settings)
        system_status = "ready"
        logging.info("Web interface initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize system: {str(e)}")
        system_status = "error"

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': system_status,
        'timestamp': datetime.now().isoformat(),
        'results': current_results
    })

@app.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """Run trading analysis"""
    global current_results, system_status
    
    try:
        if system_status != "ready":
            return jsonify({'error': 'System not ready'}), 400
        
        data = request.json
        symbol = data.get('symbol', 'RELIANCE')
        
        # Run analysis in a separate thread
        def run_async_analysis():
            global current_results, system_status
            
            try:
                system_status = "running"
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def analyze():
                    global orchestrator
                    await orchestrator.initialize()
                    # Override target symbol if provided
                    orchestrator.settings.TARGET_SYMBOL = symbol
                    result = await orchestrator.run_trading_cycle()
                    return result
                
                result = loop.run_until_complete(analyze())
                current_results = result
                system_status = "completed"
                
            except Exception as e:
                logging.error(f"Error in analysis: {str(e)}")
                current_results = {'error': str(e)}
                system_status = "error"
        
        thread = threading.Thread(target=run_async_analysis)
        thread.start()
        
        return jsonify({'message': 'Analysis started', 'status': 'running'})
        
    except Exception as e:
        logging.error(f"Error starting analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/results')
def get_results():
    """Get latest analysis results"""
    return jsonify(current_results)

# Template and static folders are configured in Flask initialization

# Create templates directory and files
import os

def create_template_files():
    """Create template files for the web interface"""
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Trading System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div class="container-fluid">
                        <a class="navbar-brand" href="#">
                            <i class="fas fa-chart-line me-2"></i>
                            Multi-Agent Trading System
                        </a>
                        <span class="navbar-text">
                            <span id="systemStatus" class="badge bg-secondary">Initializing...</span>
                        </span>
                    </div>
                </nav>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cogs me-2"></i>Control Panel</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="symbolInput" class="form-label">Symbol</label>
                            <input type="text" class="form-control" id="symbolInput" value="RELIANCE">
                        </div>
                        <button id="runAnalysisBtn" class="btn btn-primary w-100">
                            <i class="fas fa-play me-2"></i>Run Analysis
                        </button>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>System Status</h5>
                    </div>
                    <div class="card-body">
                        <div id="statusInfo">
                            <p>System initializing...</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-area me-2"></i>Analysis Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="resultsContainer">
                            <div class="text-center text-muted">
                                <i class="fas fa-chart-line fa-3x mb-3"></i>
                                <p>Run an analysis to see results</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-terminal me-2"></i>Agent Messages</h5>
                    </div>
                    <div class="card-body">
                        <div id="messagesContainer" style="height: 300px; overflow-y: auto; background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                            <p class="text-muted">No messages yet...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let pollInterval;
        
        // Update system status
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('systemStatus');
                    const statusInfo = document.getElementById('statusInfo');
                    
                    statusElement.textContent = data.status;
                    statusElement.className = 'badge ' + getStatusClass(data.status);
                    
                    statusInfo.innerHTML = `
                        <p><strong>Status:</strong> ${data.status}</p>
                        <p><strong>Last Update:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                    `;
                    
                    if (data.results && Object.keys(data.results).length > 0) {
                        displayResults(data.results);
                    }
                })
                .catch(error => console.error('Error updating status:', error));
        }
        
        function getStatusClass(status) {
            switch(status) {
                case 'ready': return 'bg-success';
                case 'running': return 'bg-warning';
                case 'completed': return 'bg-info';
                case 'error': return 'bg-danger';
                default: return 'bg-secondary';
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('resultsContainer');
            const messagesContainer = document.getElementById('messagesContainer');
            
            if (results.error) {
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error: ${results.error}
                    </div>
                `;
                return;
            }
            
            const marketData = results.market_data || {};
            const technicalAnalysis = results.technical_analysis || {};
            const tradingSignals = results.trading_signals || {};
            const riskAssessment = results.risk_assessment || {};
            const executionResult = results.execution_result || {};
            
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-chart-line me-2"></i>Market Data</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Symbol:</strong> ${marketData.symbol || 'N/A'}</p>
                                <p><strong>Price:</strong> ₹${marketData.current_price || 'N/A'}</p>
                                <p><strong>Volume:</strong> ${marketData.volume || 'N/A'}</p>
                                <p><strong>High:</strong> ₹${marketData.high || 'N/A'}</p>
                                <p><strong>Low:</strong> ₹${marketData.low || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-chart-bar me-2"></i>Technical Analysis</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Trend:</strong> ${technicalAnalysis.trend_direction || 'N/A'}</p>
                                <p><strong>RSI:</strong> ${(results.technical_indicators || {}).rsi || 'N/A'}</p>
                                <p><strong>Strength:</strong> ${technicalAnalysis.trend_strength || 'N/A'}</p>
                                <p><strong>Score:</strong> ${technicalAnalysis.overall_score || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-signal me-2"></i>Trading Signals</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Signal:</strong> 
                                    <span class="badge ${getSignalClass(tradingSignals.final_signal)}">${tradingSignals.final_signal || 'N/A'}</span>
                                </p>
                                <p><strong>Confidence:</strong> ${tradingSignals.confidence || 'N/A'}%</p>
                                <p><strong>RSI Signal:</strong> ${(tradingSignals.simple_signals || {}).rsi_signal || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-shield-alt me-2"></i>Risk Assessment</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Risk Level:</strong> ${(riskAssessment.comprehensive_analysis || {}).risk_level || 'N/A'}</p>
                                <p><strong>Approval:</strong> 
                                    <span class="badge ${getApprovalClass(riskAssessment.final_approval)}">${riskAssessment.final_approval || 'N/A'}</span>
                                </p>
                                <p><strong>Position Size:</strong> ${(riskAssessment.position_sizing || {}).shares || 'N/A'} shares</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-exchange-alt me-2"></i>Execution Result</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Executed:</strong> ${executionResult.executed || false}</p>
                                <p><strong>Order ID:</strong> ${executionResult.order_id || 'N/A'}</p>
                                <p><strong>Status:</strong> ${executionResult.execution_status || 'N/A'}</p>
                                <p><strong>Price:</strong> ₹${executionResult.execution_price || 'N/A'}</p>
                                <p><strong>Quantity:</strong> ${executionResult.execution_quantity || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Display messages
            if (results.messages && results.messages.length > 0) {
                messagesContainer.innerHTML = results.messages.map(msg => 
                    `<div class="mb-2"><i class="fas fa-chevron-right me-2"></i>${msg}</div>`
                ).join('');
            }
        }
        
        function getSignalClass(signal) {
            switch(signal) {
                case 'BUY': return 'bg-success';
                case 'SELL': return 'bg-danger';
                case 'HOLD': return 'bg-warning';
                default: return 'bg-secondary';
            }
        }
        
        function getApprovalClass(approval) {
            switch(approval) {
                case 'approved': return 'bg-success';
                case 'rejected': return 'bg-danger';
                case 'conditional': return 'bg-warning';
                default: return 'bg-secondary';
            }
        }
        
        // Run analysis
        document.getElementById('runAnalysisBtn').addEventListener('click', function() {
            const symbol = document.getElementById('symbolInput').value.trim();
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Running...';
            
            fetch('/api/run-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol: symbol })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    // Start polling for results
                    pollInterval = setInterval(updateStatus, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error starting analysis');
            })
            .finally(() => {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-play me-2"></i>Run Analysis';
            });
        });
        
        // Initialize
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w') as f:
        f.write(index_html)

if __name__ == '__main__':
    # Create template files
    create_template_files()
    
    # Initialize system
    setup_system()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
