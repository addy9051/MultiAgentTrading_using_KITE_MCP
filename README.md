# Multi-Agent Kite Trading System

A debate-driven multi-agent algorithmic trading system powered by LangGraph and Zerodha KITE MCP. The system uses 14 specialized AI agents organized in a graph pipeline with adversarial debate loops and multi-perspective risk analysis.

## Architecture

```
Market Data → Technical → Fundamentals → Sentiment → News
                                                       ↓
                                              Bull Researcher ←→ Bear Researcher (debate loop)
                                                       ↓
                                              Research Arbiter (judges debate)
                                                       ↓
                                              Trade Strategist (craft proposal)
                                                       ↓
                                              Risk Hawk → Risk Dove → Risk Owl (panel rotation)
                                                       ↓
                                              Risk Arbiter (final verdict)
                                                       ↓
                                              Portfolio Manager (execute via KITE MCP)
```

### Agent Roles

| Agent | Role |
|-------|------|
| **Market Data Agent** | Fetches real-time data from KITE MCP |
| **Technical Analysis** | Computes RSI, MACD, Bollinger Bands, etc. |
| **Fundamentals Analyst** | Evaluates financial health and valuation |
| **Sentiment Analyst** | Gauges social media and news sentiment |
| **News Analyst** | Assesses news impact and catalysts |
| **Bull Researcher** | Builds and defends bullish investment thesis |
| **Bear Researcher** | Builds and defends bearish investment thesis |
| **Research Arbiter** | Judges the bull/bear debate, renders verdict |
| **Trade Strategist** | Synthesizes analysis into trade proposals |
| **Risk Hawk** | Aggressive risk perspective |
| **Risk Dove** | Conservative risk perspective |
| **Risk Owl** | Balanced, data-driven risk perspective |
| **Risk Arbiter** | Final risk approval/rejection authority |
| **Portfolio Manager** | Executes approved trades via KITE MCP |

### Key Features

- **Adversarial Debate**: Bull and Bear researchers debate over multiple rounds, with an impartial Arbiter judging the quality of arguments
- **Multi-Perspective Risk Panel**: Three risk agents (Hawk/Dove/Owl) discuss risk from aggressive, conservative, and balanced perspectives before a Risk Arbiter makes the final call
- **Agent Memory**: Agents retain context across trading cycles via a lightweight JSON memory system
- **KITE MCP Integration**: Real-time market data and order execution through Zerodha's KITE Connect API via MCP
- **LangGraph Orchestration**: Full StateGraph with conditional edges controlling debate loops and risk panel rotation

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key (optional — falls back to sample data without it)
- Zerodha KITE MCP server (optional — runs in simulation mode by default)

### Installation

```bash
pip install -e .
```

### Environment Variables

```bash
# Required for live LLM analysis
OPENAI_API_KEY=your_key

# Required for live trading (optional — simulation mode is default)
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
KITE_ACCESS_TOKEN=your_token
KITE_MCP_URL=http://localhost:8080

# Trading configuration
TARGET_SYMBOL=RELIANCE
EXCHANGE=NSE
SIMULATION_MODE=true

# Debate/risk settings
MAX_DEBATE_ROUNDS=2
MAX_RISK_DISCUSSION_ROUNDS=2
```

### Running

```bash
# Simple run
python main.py

# Detailed output with rich summary
python main_enhanced.py

# Web interface
python app.py
```

## Project Structure

```
├── agents/                          # All 14 agent implementations
│   ├── market_data_agent.py         # KITE MCP data fetching
│   ├── technical_analysis_agent.py  # Technical indicators
│   ├── fundamentals_analyst.py      # Fundamental analysis
│   ├── sentiment_analyst.py         # Sentiment analysis
│   ├── news_analyst.py              # News impact analysis
│   ├── bull_researcher.py           # Bullish thesis + debate
│   ├── bear_researcher.py           # Bearish thesis + debate
│   ├── research_arbiter.py          # Debate judge
│   ├── trade_strategist.py          # Trade proposal generation
│   ├── risk_hawk.py                 # Aggressive risk view
│   ├── risk_dove.py                 # Conservative risk view
│   ├── risk_owl.py                  # Balanced risk view
│   ├── risk_arbiter.py              # Risk verdict authority
│   └── portfolio_manager.py         # Execution via KITE MCP
├── graph/                           # LangGraph pipeline
│   ├── agent_graph.py               # StateGraph builder
│   └── graph_conditions.py          # Conditional edge routing
├── services/                        # Infrastructure
│   ├── trading_orchestrator.py      # Graph wrapper
│   └── kite_mcp_client.py           # KITE MCP client
├── models/
│   └── trading_state.py             # Shared state schema
├── config/
│   ├── settings.py                  # Environment config
│   └── default_config.py            # Default values
├── utils/
│   ├── agent_memory.py              # Cross-cycle memory
│   ├── technical_indicators.py      # Indicator calculations
│   └── logging_config.py            # Logging setup
├── main.py                          # CLI entry point
├── main_enhanced.py                 # Rich output entry point
└── app.py                           # Flask web interface
```

## Inspiration

This project draws inspiration from [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) for the concept of multi-agent debate-driven trading analysis. The implementation uses original architecture, naming, and integration with Zerodha's KITE MCP for real Indian market trading.
