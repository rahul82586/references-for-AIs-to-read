# Broker Platform

Tier-1 Institutional Brokerage Platform combining MetaTrader 5's strict rule-based core with modern AI-driven capabilities.

## Architecture

This platform uses **Domain-Driven Design (DDD)**, **CQRS**, and **Dependency Injection** to provide:

- **MT5-style Core**: Groups as rule engines, Trade Modifications, Account Types (Real, Demo, Preliminary, Coverage, Contest)
- **Modern Intelligence Layer**: ClickHouse time-series, LLM Agents, Portfolio Analytics, Real-time Risk
- **Flexible Infrastructure**: Python-first with hot-path migration to Rust via PyO3

## Directory Structure

```
broker-platform/
├── core/                    # Pure Domain Logic (No frameworks, no DBs)
│   ├── domains/             # Business entities and rules
│   ├── ports/               # Interface contracts
│   └── events/              # Domain events
├── application/             # Use Cases & Orchestration (CQRS)
│   ├── commands/            # Write operations
│   ├── queries/             # Read operations
│   ├── services/            # Cross-domain services
│   └── di/                  # Dependency Injection Container
├── infrastructure/          # Adapters (Implementations of Ports)
│   ├── persistence/         # SQL/NoSQL repositories
│   ├── messaging/           # Redis/Kafka event bus
│   ├── cluster/             # Node synchronization
│   ├── security/            # SSL, JWT, OAuth, 2FA
│   ├── gateways/            # LP connectors (FIX, REST)
│   ├── feeds/               # Market data ingestors
│   ├── engines/             # Matching engine (Python → Rust)
│   ├── cache/               # Redis caching
│   └── notifications/       # Email, SMS, Push, Telegram
├── api/                     # Edge Layer
│   ├── admin/               # Eclipse Theia UI Backend
│   ├── client/              # Trader Terminal API
│   ├── fix/                 # FIX API Server
│   ├── webhooks/            # External integrations
│   └── grpc/                # Internal node communication
├── intelligence/            # Godel/Fincept Layer
│   ├── timeseries/          # ClickHouse/TimescaleDB
│   ├── ai_agents/           # LLM integrations
│   ├── portfolio/           # Factor models, VaR, Greeks
│   ├── news/                # NLP tagging, sentiment
│   ├── screening/           # Factor screening
│   └── reporting/           # EOD/Monthly statements
├── config/                  # Configuration files
├── ops/                     # DevOps & Infrastructure
├── cli/                     # Command Line Interface
├── tests/                   # Testing suites
└── docs/                    # Documentation
```

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- ClickHouse (optional for analytics)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd broker-platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start the server
uvicorn api.main:app --reload
```

### Development

```bash
# Run tests
pytest

# Run linters
black .
ruff check .
mypy .

# Start development servers (requires Docker)
docker-compose up -d postgres redis
```

## Key Features

### 1. Group-Based Rule Engine
Groups define margin, leverage, commissions, swaps, permissions, and routing rules for accounts.

### 2. Trade Modifications
Dealers can correct any trade parameter post-execution with full audit trail and automatic balance recalculation.

### 3. Cluster Synchronization
Multi-node architecture with automatic data sync, conflict resolution, and certificate management.

### 4. Dealer Workflow
Color-coded tickets, dealer queues, manual confirmation/requote capabilities with real-time UI updates.

### 5. AI-Powered Intelligence
- LLM agents for customer support and trade analysis
- Real-time portfolio analytics (VaR, Sharpe, Greeks)
- Millisecond news ingestion with NLP sentiment
- Interactive chat with trade history context

## Configuration

Edit `config/settings.yaml` for global settings. Group templates and symbol definitions are in `config/groups/` and `config/symbols/`.

## License

MIT
