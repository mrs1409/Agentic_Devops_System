# 🤖 Agentic DevOps System

**AI-Powered Autonomous Incident Response & Remediation Platform**

[![Build Status](https://github.com/s-hari-haran/devopsagent/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/s-hari-haran/devopsagent/actions)
[![Docker Hub](https://img.shields.io/badge/Docker-realhariharans-blue)](https://hub.docker.com/u/realhariharans)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/s-hari-haran/devopsagent)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docs.docker.com/compose/)

> A fully autonomous DevOps copilot that **detects incidents**, performs **AI-powered root cause analysis** (GPT-4 / Gemini 2.0), and executes **automated remediation** with intelligent human-in-the-loop approval workflows.

---

## 📋 Table of Contents

- [What This Does](#-what-this-does)
- [System Architecture](#-system-architecture)
- [The 5 AI Agents](#-the-5-ai-agents)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Dashboards](#-dashboards)
- [Testing](#-testing)
- [Deployment Options](#-deployment-options)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)

---

## 🎯 What This Does

The Agentic DevOps System runs **5 autonomous AI agents** that watch your infrastructure 24/7 and handle incidents automatically:

| Step | Agent | Action |
|------|-------|--------|
| 1️⃣ | **Monitor** | Detects anomalies (CPU spike, memory leak, error surge) |
| 2️⃣ | **Analyzer** | Uses LLM (Gemini/GPT-4) to find the root cause |
| 3️⃣ | **Auto-Response** | Decides: auto-fix or ask for human approval |
| 4️⃣ | **Notifier** | Sends Slack alerts + email + dashboard updates |
| 5️⃣ | **Memory** | Learns from past incidents to get smarter over time |

**Key numbers:**
- ⚡ Incident detected in **< 15 seconds**
- 🧠 Root cause analysis in **1–5 seconds**
- 🔧 Auto-remediation in **< 2 minutes** (fully automated path)
- 💰 LLM cost: ~**\$0.03–0.05 per incident** (with Redis caching)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Agentic DevOps System                  │
└─────────────────────────────────────────────────────────┘

  [Test App / Real Services]
         │ metrics
         ▼
  [Prometheus Scraper]
         │ scrape
         ▼
  ┌─────────────────┐
  │ Monitoring Agent │  ◄── Z-score anomaly detection
  └────────┬────────┘
           │ incident event (monitoring.incident.*)
           ▼
  ┌─────────────────┐
  │   RabbitMQ Bus   │  ◄── Topic exchange, durable queues
  └────────┬────────┘
           │
    ┌──────┴──────┬──────────────┐
    ▼             ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│Analyzer│  │ Notifier │  │  Memory  │
│ Agent  │  │  Agent   │  │  Agent   │
└───┬────┘  └──────────┘  └──────────┘
    │ calls
    ▼
┌──────────┐
│LLM Service│  ◄── GPT-4 / Gemini 2.0 / Claude
└──────────┘
    │ analysis result
    ▼
┌──────────────────┐
│ Auto-Response    │
│     Agent        │
│                  │
│ Confidence ≥95%? │──YES──► Auto-execute on K8s/Docker
│       NO         │──────► Approval Dashboard (human review)
└──────────────────┘
```

### How events flow (timeline)

```
T+0s   → Monitoring Agent detects anomaly (CPU > 80%)
T+1s   → Incident event published to RabbitMQ
T+2-5s → Analyzer queries RAG + sends to LLM → recommendations
T+5-6s → Auto-Response: confidence ≥ 95%? auto-execute : request approval
T+var  → Human approves/rejects in dashboard (if needed)
T+end  → Action executed on K8s / Docker Compose
T+end  → Slack notification + dashboard update + pattern stored
```

---

## 🤖 The 5 AI Agents

### 1. 📊 Monitoring Agent
Continuously polls Prometheus metrics and fires alerts when thresholds are breached.

| Trigger | Default Threshold |
|---------|-------------------|
| CPU usage | > 80% |
| Memory usage | > 85% |
| Error rate | > 5% |
| Pod restarts | > 3 |

- Uses **Z-score statistical analysis** (2.0σ sensitivity) for anomaly detection
- Publishes to RabbitMQ topic `monitoring.incident.*`

### 2. 🧠 Analyzer Agent
Takes an incident event and performs LLM-powered root cause analysis.

- Searches **Qdrant vector store** for similar past incidents (RAG)
- Sends enriched context to LLM → structured recommendations
- Outputs: root cause + confidence score (0–100%) + action list
- Caches LLM responses in Redis (300s TTL) to cut costs

### 3. ⚡ Auto-Response Agent
Decides whether to auto-fix or escalate to a human.

```
Confidence ≥ 95% + Low/Medium severity  →  Auto-execute immediately
Confidence < 95%  OR  High/Critical     →  Send to Approval Dashboard
No recommendations                      →  Manual Review queue
```

Supported actions: `scale_deployment`, `restart_pod`, `rollback_deployment`

Safety limits: min 1 replica, max 10 replicas, dry-run mode available.

### 4. 📢 Notifier Agent
Sends rich Slack notifications using Block Kit formatting for every pipeline event:
- 🚨 Incident detected
- 🔍 Analysis complete
- ✅ Action executed
- ⏳ Approval pending

### 5. 🧠💾 Memory Agent
Stores everything and detects recurring patterns:

| Pattern Type | How it works |
|-------------|--------------|
| **Exact match** | Same metric + target recurring (SQL GROUP BY) |
| **Semantic** | Similar issues via vector clustering (≥ 0.85 similarity) |
| **Temporal** | Same time-of-day / day-of-week patterns |

Storage: PostgreSQL (incidents/analyses/resolutions/patterns) + Qdrant (1536-dim embeddings).

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Agents** | Python 3.11, asyncio, aio-pika |
| **LLM Service** | FastAPI, OpenAI SDK, Google GenAI, Anthropic SDK |
| **Approval UI** | React 18 + Material-UI + Socket.io |
| **Ops Dashboard** | Next.js 14, TailwindCSS |
| **Message Broker** | RabbitMQ 3.12 |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Vector Store** | Qdrant |
| **Monitoring** | Prometheus + Grafana |
| **Reverse Proxy** | NGINX |
| **Containers** | Docker Compose (local) / Kubernetes (production) |
| **CI/CD** | GitHub Actions |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Docker Desktop | 24.0+ | Latest |
| RAM | 16 GB | 32 GB |
| Disk | 20 GB free | 50 GB |
| Python | 3.11+ | 3.11+ |

You'll also need **at least one LLM API key**:
- 🌟 **Google Gemini** ([get key](https://makersuite.google.com/app/apikey)) — free 2000 RPM, **recommended**
- OpenAI GPT-4 ([get key](https://platform.openai.com/api-keys))
- Anthropic Claude ([get key](https://console.anthropic.com/))

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/s-hari-haran/devopsagent.git
cd devopsagent
```

### Step 2 — Set up environment variables

```bash
# Copy the template
cp .env.example .env
```

Open `.env` and fill in at minimum:

```bash
# Required: at least one LLM key
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Slack notifications
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=your-channel-name

# Optional: Email
SMTP_PASSWORD=your-resend-api-key
FROM_EMAIL=noreply@yourdomain.com
EMAIL_RECIPIENTS=you@example.com
```

> Everything else (database, Redis, RabbitMQ) uses safe default values that work out-of-the-box with Docker Compose.

### Step 3 — Start all 18 services

```bash
docker-compose up -d --build
```

This will:
- Build all Docker images (~5–10 min first run)
- Start PostgreSQL, Redis, RabbitMQ
- Initialize the database schema
- Launch all 5 AI agents
- Start both dashboards + monitoring stack

### Step 4 — Wait for healthy status (~60–90 seconds)

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep devops
```

All containers should show `(healthy)`.

### Step 5 — Open the dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| 🎛️ **Approval Dashboard** | http://localhost:3001 | Review & approve AI actions |
| 📊 **Ops Dashboard** | http://localhost:3003 | System health & incident feed |
| 📈 **Grafana** | http://localhost:3002 | Metrics & graphs (admin/admin) |
| 🔍 **Prometheus** | http://localhost:9090 | Raw metrics & PromQL |
| 🐰 **RabbitMQ** | http://localhost:15672 | Message queue monitor (devops/devops123) |

### Step 6 — Trigger a test incident

```bash
python trigger_incident.py
```

Then watch the magic in real-time:

```bash
# All agent logs at once
docker-compose logs -f monitoring-agent analyzer-agent auto-response-agent notifier-agent llm-service
```

Expected flow:
1. ✅ **Monitoring Agent** — `🚨 Incident detected: threshold_breach`
2. ✅ **Analyzer Agent** — `🔍 Analyzing… ✓ confidence=75%`
3. ✅ **Auto-Response Agent** — `✓ Created approval request: #119`
4. ✅ **Approval Dashboard** — New card appears at http://localhost:3001
5. ✅ **Notifier Agent** — Slack message sent

---

## ⚙️ Configuration

### Environment Variables Reference

All agents read their config from environment variables. The main ones:

```bash
# --- LLM ---
GEMINI_API_KEY=...           # Google Gemini (recommended)
OPENAI_API_KEY=...           # OpenAI GPT-4
ANTHROPIC_API_KEY=...        # Anthropic Claude
LLM_PROVIDER=gemini          # Which provider to use: gemini | openai | anthropic
LLM_MODEL=gemini-2.0-flash   # Model name

# --- Thresholds ---
MONITORING_CPU_THRESHOLD=90.0        # CPU % to trigger alert
MONITORING_MEMORY_THRESHOLD=90.0     # Memory % to trigger alert
MONITORING_ERROR_RATE_THRESHOLD=5.0  # Error rate % to trigger alert
AUTORESPONSE_AUTO_EXECUTE_THRESHOLD=95  # Confidence % for auto-execution

# --- Safety ---
AUTORESPONSE_K8S_DRY_RUN=false  # Set true to simulate without executing
AUTORESPONSE_MAX_SCALE_REPLICAS=10
AUTORESPONSE_MIN_SCALE_REPLICAS=1
```

### Adjust thresholds per environment

**Development** (sensitive, see lots of alerts):
```bash
MONITORING_CPU_THRESHOLD=60.0
MONITORING_MEMORY_THRESHOLD=70.0
AUTORESPONSE_K8S_DRY_RUN=true   # don't actually change anything
```

**Production** (conservative, only real incidents):
```bash
MONITORING_CPU_THRESHOLD=90.0
MONITORING_MEMORY_THRESHOLD=90.0
AUTORESPONSE_AUTO_EXECUTE_THRESHOLD=100  # always require human approval
```

---

## 📊 Dashboards

### Approval Dashboard (port 3001)
Human-in-the-loop interface. Shows every incident the AI analyzed. You can:
- Read the AI's root cause analysis
- See recommended actions
- **Approve** (action executes immediately) or **Reject**
- Override with a manual action

### Ops Dashboard (port 3003)
Real-time system overview:
- Agent health status (green/red)
- Live incident feed
- Recent actions + outcomes
- System metrics summary

### Grafana (port 3002)
Pre-built dashboards for:
- Agent performance metrics
- Incident detection rates
- LLM API latency
- Queue depths

Default login: `admin` / `admin`

---

## 🧪 Testing

### Trigger different incident types

**High CPU:**
```bash
python trigger_incident.py
# Default: CPU spike
```

**Memory leak:**
```bash
curl -X POST http://localhost:8080/trigger \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"memory-test","type":"threshold_breach","metric":"memory_mb","value":950.0,"threshold":800.0,"severity":"high"}'
```

**Error rate spike:**
```bash
curl -X POST http://localhost:8080/trigger \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"error-test","type":"error_rate","metric":"errors_total","value":12.5,"threshold":5.0,"severity":"critical"}'
```

### Unit tests

```bash
# Run tests for a specific agent
cd services/monitoring-agent
pytest tests/ -v --cov=app

# All agents
./run_tests.sh      # Linux/Mac
./run_tests.ps1     # Windows PowerShell
```

### Integration tests

```bash
# Check RabbitMQ queues
docker exec devops-rabbitmq rabbitmqctl list_queues

# Check PostgreSQL incidents
docker exec devops-postgres psql -U devops -d devops_db \
  -c "SELECT * FROM incidents ORDER BY created_at DESC LIMIT 5;"

# Check Redis cache
docker exec devops-redis redis-cli -a redis123 KEYS "*llm*"

# Check vector store
curl http://localhost:6333/collections
```

---

## 🚢 Deployment Options

### Option A: Docker Compose (Local / Dev) ✅ Default

```bash
docker-compose up -d --build
```

### Option B: Kubernetes (Production)

```bash
kubectl create namespace devops-agents
kubectl apply -k k8s/overlays/production/
kubectl get pods -n devops-agents
```

### Option C: Azure Container Apps

```bash
az login
chmod +x deploy-from-dockerhub.sh
./deploy-from-dockerhub.sh
```

Estimated cost: **\$51–66/month** (Azure for Students: \$100 free credits).

---

## 🔧 Troubleshooting

### Containers not healthy

```bash
# Check specific container logs
docker logs devops-analyzer-agent --tail 50

# Restart a service
docker-compose restart analyzer-agent

# Rebuild and restart
docker-compose up -d --build analyzer-agent
```

### Out of memory

```bash
# Check Docker Desktop settings → increase to 16+ GB
docker stats
```

### Port already in use

```bash
# Windows
netstat -ano | findstr :3001

# Linux/Mac
lsof -i :3001
```

### LLM service errors

```bash
# Verify API key is loaded
docker exec devops-llm-service printenv | grep API_KEY

# Test LLM service directly
curl http://localhost:8000/health

# Check logs
docker logs devops-llm-service --tail 100
```

### Stop everything

```bash
# Graceful shutdown
docker-compose down

# Full clean (removes volumes = wipes database)
docker-compose down -v

# Full clean including images
docker-compose down -v --rmi all
```

---

## ❓ FAQ

**Which LLM should I use?**
- Google Gemini 2.0-Flash → free 2000 RPM, 1–3s latency, **best for getting started**
- OpenAI GPT-4 → highest quality, 2–5s, paid (~\$0.03–0.05/incident)
- Anthropic Claude → similar to GPT-4, alternative option

**Do I need Kubernetes?**
No. Docker Compose works perfectly for local and dev use. Kubernetes is optional for large-scale production.

**How do I require approval for every action?**
Set `AUTORESPONSE_AUTO_EXECUTE_THRESHOLD=100` in `.env`. Every action will go to the approval dashboard.

**How do I disable auto-execution entirely?**
Same: `AUTORESPONSE_AUTO_EXECUTE_THRESHOLD=100`.

**How do I add a new LLM provider?**
Edit `services/llm-service/app/llm_client.py` — follow the existing OpenAI/Anthropic/Google patterns.

**How do I add a new remediation action?**
Edit `services/auto-response-agent/app/executors/` — add your custom executor following the existing ones.

**What do the two dashboards do?**
- **Approval Dashboard (3001)** — human review & approve/reject AI actions
- **Ops Dashboard (3003)** — monitoring system health, incident feed, agent status

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit with clear messages: `git commit -m 'feat: add my feature'`
4. Push and open a Pull Request

**Code style:**
- Python: Black formatter, type hints, docstrings
- JavaScript: ESLint + Prettier
- Commits: [Conventional Commits](https://www.conventionalcommits.org/)

**Good areas to contribute:**
- 🧪 More unit & integration tests
- 📝 Documentation improvements
- 🎨 Dashboard UI/UX enhancements
- 🔌 New executor implementations (Ansible, Terraform, etc.)
- 🤖 Custom agent implementations
- 🌍 Internationalization

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Hari Haran S**
- GitHub: [@s-hari-haran](https://github.com/s-hari-haran)
- Docker Hub: [realhariharans](https://hub.docker.com/u/realhariharans)

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) for GPT-4
- [Google](https://deepmind.google) for Gemini 2.0
- [Anthropic](https://anthropic.com) for Claude
- [Qdrant](https://qdrant.tech) for the vector database
- [RabbitMQ](https://www.rabbitmq.com) for reliable messaging
- [Slack](https://slack.com) for notifications

---

**⚡ Built with passion for autonomous DevOps — transforming incident response from reactive to proactive.**

*Last Updated: November 2025 | Version: 1.0.0 | Status: Production Ready ✅*
