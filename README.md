# Multi-Agent Algorithmic Trading System MVP

A sophisticated multi-agent trading system built with LangChain and LangGraph, integrating with Kite Connect 3 API through MCP server for secure market data access and trading signal generation.

## 🏗️ Architecture

This system implements a multi-agent framework inspired by the TauricResearch/TradingAgents repository, featuring:

### Core Agents
- **Market Data Agent**: Fetches live/historical market data via Kite MCP server
- **Technical Analysis Agent**: Calculates technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Signal Generation Agent**: Generates trading signals using LLM-powered analysis
- **Risk Assessment Agent**: Evaluates position sizing and risk management

### Workflow Orchestration
- **LangGraph StateGraph**: Coordinates agent interactions and data flow
- **Sequential Processing**: Market Data → Technical Analysis → Signal Generation → Risk Assessment → Execution
- **Shared State**: All agents work with a common TradingState for seamless data sharing

## 🚀 Features

### Market Data Integration
- Real-time quote fetching through Kite MCP server
- Historical data retrieval for technical analysis
- Market sentiment analysis using GPT-4o
- Volume and volatility assessment

### Technical Analysis
- RSI (Relative Strength Index)
- Moving Averages (SMA, EMA)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Average True Range (ATR)

### Trading Signals
- Multi-factor signal generation
- LLM-powered pattern recognition
- Confidence scoring and signal strength assessment
- Entry/exit point identification

### Risk Management
- Position sizing based on account balance and risk tolerance
- Stop-loss and take-profit calculations
- Market volatility assessment
- Trade approval workflow

### Order Simulation
- Safe simulation mode for testing
- Detailed order logging
- Execution result tracking
- No real money at risk during development

## 🔧 Setup Instructions

### Prerequisites
1. Python 3.9+
2. Zerodha account with Kite Connect API access
3. OpenAI API key for LLM functionality
4. Kite MCP server (hosted or self-hosted)

### Environment Variables
Create a `.env` file or set these environment variables:

```bash
# Kite Connect API
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_access_token  # Optional for some operations
KITE_MCP_URL=http://localhost:8080  # or https://mcp.kite.trade/mcp

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o

# Trading Configuration
TARGET_SYMBOL=RELIANCE
EXCHANGE=NSE
QUANTITY=1

# Strategy Parameters
RSI_PERIOD=14
RSI_OVERBOUGHT=70.0
RSI_OVERSOLD=30.0

# Risk Management
MAX_POSITION_SIZE=0.02  # 2% of portfolio
STOP_LOSS_PERCENT=0.05  # 5% stop loss

# System Configuration
LOG_LEVEL=INFO
SIMULATION_MODE=true  # Keep as true for safety
