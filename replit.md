# Multi-Agent Algorithmic Trading System MVP

## Overview

This is a sophisticated multi-agent algorithmic trading system that integrates with Kite Connect 3 API through an MCP (Model Context Protocol) server. The system uses LangChain and LangGraph frameworks to orchestrate multiple specialized agents that work together to analyze market data, generate trading signals, and manage risk.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Framework
- **LangChain & LangGraph**: The system is built on LangChain for individual agent implementation and LangGraph for orchestrating multi-agent workflows
- **Multi-Agent Pattern**: Follows the TauricResearch/TradingAgents repository design principles with clear separation of concerns
- **Asynchronous Processing**: Uses Python's asyncio for handling concurrent operations and API calls

### Agent Architecture
The system implements a sequential multi-agent workflow:
1. **Market Data Agent** → fetches live and historical market data
2. **Technical Analysis Agent** → calculates technical indicators
3. **Signal Generation Agent** → generates trading signals using LLM analysis
4. **Risk Assessment Agent** → evaluates position sizing and risk management

### State Management
- **Shared State**: All agents work with a common `TradingState` TypedDict for seamless data sharing
- **Message Passing**: Agents communicate through structured state updates
- **Error Handling**: Centralized error tracking and handling across the workflow

## Key Components

### Market Data Integration
- **Kite MCP Client**: Secure communication with Kite Connect 3 API through MCP server
- **Real-time Data**: Live quote fetching and historical data retrieval
- **Data Validation**: Comprehensive error handling for API responses

### Technical Analysis Engine
- **Multiple Indicators**: RSI, Moving Averages (SMA/EMA), MACD, Bollinger Bands, Stochastic Oscillator, ATR
- **Configurable Parameters**: RSI periods, overbought/oversold thresholds
- **Numpy Integration**: Efficient numerical calculations for indicators

### Trading Signal Generation
- **Multi-factor Analysis**: Combines multiple technical indicators
- **LLM-powered Analysis**: Uses GPT-4o for pattern recognition and sentiment analysis
- **Confidence Scoring**: Signals include strength assessment and confidence levels

### Risk Management
- **Position Sizing**: Calculates optimal position size based on account balance and risk tolerance
- **Stop Loss/Take Profit**: Automatic calculation of risk management levels
- **Volatility Assessment**: Market volatility consideration in risk calculations

### Web Interface
- **Flask Application**: Simple web interface for monitoring system status
- **Real-time Updates**: API endpoints for system status and trading results
- **Dashboard**: Basic visualization of trading system state

## Data Flow

1. **Initialization**: System loads configuration and initializes MCP client connection
2. **Market Data Collection**: Fetches live quotes and historical data for target symbol
3. **Technical Analysis**: Calculates various technical indicators from historical data
4. **Signal Generation**: Combines technical indicators with LLM analysis to generate trading signals
5. **Risk Assessment**: Evaluates position sizing and risk management parameters
6. **Order Simulation**: Logs potential orders (simulation mode enabled by default)

## External Dependencies

### APIs and Services
- **Kite Connect 3 API**: Primary trading API accessed through MCP server
- **OpenAI API**: GPT-4o model for LLM-powered analysis and signal generation
- **Kite MCP Server**: Intermediary server for secure API communication

### Python Libraries
- **LangChain/LangGraph**: Core framework for agent orchestration
- **Flask**: Web interface framework
- **aiohttp**: Asynchronous HTTP client for API calls
- **numpy**: Numerical computations for technical indicators
- **requests**: HTTP client for synchronous requests

### Configuration
- **Environment Variables**: All sensitive configuration through environment variables
- **Simulation Mode**: Safe testing mode enabled by default
- **Configurable Parameters**: Trading parameters, risk management settings, and API endpoints

## Deployment Strategy

### Development Setup
- **Local Development**: Designed to run locally with minimal setup
- **Environment Configuration**: Uses `.env` file pattern for configuration
- **Logging**: Comprehensive logging with file rotation and console output

### Production Considerations
- **MCP Server**: Requires separate Kite MCP server instance
- **API Keys**: Secure handling of Kite Connect and OpenAI API keys
- **Risk Management**: Multiple safety layers including simulation mode

### Monitoring and Observability
- **Structured Logging**: Comprehensive logging across all components
- **Error Tracking**: Centralized error handling and logging
- **Performance Metrics**: Basic performance tracking and status monitoring

### Security
- **API Key Management**: Environment variable-based configuration
- **MCP Server**: Secure communication through dedicated MCP server
- **Simulation Mode**: Safe testing environment with order simulation