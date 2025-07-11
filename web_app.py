"""
Web interface for the Multi-Agent Trading System
"""

import os
import asyncio
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from config.settings import Settings
from services.trading_orchestrator import TradingOrchestrator
from utils.logging_config import setup_logging

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Global variables
current_results = None
system_status = "ready"
orchestrator = None
start_time = datetime.now()

def setup_system():
    """Initialize the trading system"""
    global orchestrator
    try:
        # Setup logging
        setup_logging()
        
        # Initialize settings
        settings = Settings()
        
        # Initialize orchestrator
        orchestrator = TradingOrchestrator(settings)
        
        logging.info("Trading system initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error initializing trading system: {str(e)}")
        return False

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/status')
def get_status():
    """Get system status"""
    global start_time
    uptime = str(datetime.now() - start_time).split('.')[0]
    
    return jsonify({
        'status': system_status,
        'uptime': uptime,
        'mode': 'Sample Data' if not os.getenv('OPENAI_API_KEY') else 'Live Data',
        'target_symbol': 'RELIANCE',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    """Run trading analysis"""
    global current_results, system_status, orchestrator
    
    try:
        system_status = "running"
        
        def run_async_analysis():
            global current_results, system_status
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def analyze():
                    await orchestrator.initialize()
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
        
        return jsonify({'success': True, 'message': 'Analysis started', 'status': 'running'})
        
    except Exception as e:
        logging.error(f"Error starting analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/results')
def get_results():
    """Get latest analysis results"""
    if current_results:
        return jsonify({'results': current_results})
    else:
        return jsonify({'results': None, 'message': 'No analysis results available'})

if __name__ == '__main__':
    if setup_system():
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to initialize trading system")