# Agentic DevOps System - Complete System Understanding

**Date:** October 31, 2025
**Status:** Ready for Option 2 Implementation

---

## 🎯 System Overview

The **Agentic DevOps System** is an autonomous incident detection and remediation platform featuring 5 AI agents that work together to:

1. **Detect** incidents from Prometheus metrics
2. **Analyze** root causes using LLM-powered analysis (GPT-4/Claude)
3. **Recommend** actionable remediation steps
4. **Execute** healing actions autonomously or with approval
5. **Learn** from past incidents using RAG (vector embeddings)

---

## 🏗️ System Architecture

### High-Level Flow

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Test App    │──────▶│  Prometheus  │──────▶│  Monitoring  │
│  (Chaos)     │metrics│              │scrape │    Agent     │
└──────────────┘       └──────────────┘       └──────┬───────┘
                                                      │ incidents
                                                      ▼
                                              ┌──────────────┐
                                              │   RabbitMQ   │
                                              │  Event Bus   │
                                              └──────┬───────┘
                                                      │
                        ┌─────────────────────────────┼─────────────────┐
                        │                             │                 │
                        ▼                             ▼                 ▼
              ┌──────────────┐            ┌──────────────┐   ┌──────────────┐
              │   Analyzer   │◀──────────▶│ LLM Service  │   │   Notifier   │
              │    Agent     │   analysis │ (GPT-4)      │   │    Agent     │
              └──────┬───────┘            └──────────────┘   └──────────────┘
                     │ recommendations
                     ▼
              ┌──────────────┐            ┌──────────────┐
              │Auto-Response │◀──────────▶│  Approval    │
              │    Agent     │   optional │  Dashboard   │
              └──────┬───────┘            └──────────────┘
                     │ actions
                     ▼
              ┌──────────────┐            ┌──────────────┐
              │  Docker /    │            │Memory Agent  │
              │  Kubernetes  │            │(PostgreSQL + │
              │  (Executor)  │            │   Qdrant)    │
              └──────────────┘            └──────────────┘
```

---

## 🤖 The 5 Agents Explained

### 1. **Monitoring Agent** 📊

**Purpose:** Continuously monitors Prometheus metrics and detects anomalies

**File:** `services/monitoring-agent/app/main.py`

**What it does:**
- Queries Prometheus every 15 seconds
- Checks metrics: `test_app_cpu_percent`, `test_app_memory_mb`, `test_app_errors_total`
- Applies threshold checks (CPU > 80%, Memory > 85%, Errors > 5%)
- Performs Z-score anomaly detection (2.0σ threshold)
- Checks Kubernetes pod health (if K8s available)

**Publishes to RabbitMQ:**
```json
{
  "incident_id": "uuid",
  "agent": "monitoring",
  "event_type": "incident_detected",
  "severity": "high|medium|low",
  "data": {
    "incident_type": "threshold_breach",
    "metric": "test_app_memory_mb",
    "current_value": 500,
    "threshold": 400,
    "affected_services": ["test-app"]
  }
}
```

**Routing Key:** `monitoring.incident.detected`

---

### 2. **Analyzer Agent** 🧠

**Purpose:** Performs LLM-powered root cause analysis and generates recommendations

**File:** `services/analyzer-agent/app/main.py`

**What it does:**
- Listens for incident events from monitoring agent
- Fetches recent logs (if enabled)
- Searches for similar past incidents using RAG (vector similarity search in Qdrant)
- Builds comprehensive prompt with incident context
- Calls LLM Service (GPT-4 or Claude) for analysis
- Parses LLM response into structured recommendations
- Maps LLM suggestions to executable actions using `ActionMapper`

**Key Files:**
- `main.py` - Main orchestration logic
- `action_mapper.py` - Converts LLM text to structured actions (✅ **Option 1 Fixed**)
- `prompts.py` - Builds structured prompts for LLM
- `llm_analyzer.py` - Calls LLM Service API

**Publishes to RabbitMQ:**
```json
{
  "agent": "analyzer",
  "type": "analysis_complete",
  "incident_id": "uuid",
  "analysis": {
    "root_cause": "Memory leak in test-app",
    "confidence": 85,
    "severity": "high"
  },
  "recommendations": [
    {
      "action_type": "restart_pods",
      "target": "test-app",
      "target_type": "deployment",
      "criticality": "medium",
      "confidence": 85,
      "reasoning": "Restart will clear memory leak",
      "parameters": {}
    }
  ]
}
```

**Routing Key:** `analyzer.analysis.complete`

**✅ Option 1 Status:** COMPLETE (October 30, 2025)
- Fixed `ActionMapper` to properly parse LLM recommendations
- Now generates 1-2 actionable recommendations per incident
- No more "Could not map action" errors

---

### 3. **Auto-Response Agent** ⚡

**Purpose:** Executes or requests approval for remediation actions

**File:** `services/auto-response-agent/app/main.py`

**What it does:**
- Listens for analysis events from analyzer agent
- Validates recommendations using `ActionValidator`
- Decides execution path:
  - **Auto-execute:** Confidence ≥ 95% + Low/Medium criticality
  - **Request approval:** Confidence < 95% OR High/Critical criticality
- Executes actions via executor (K8s or Docker Compose)
- Publishes execution results

**Key Files:**
- `main.py` - Main orchestration (lines 324-415: `execute_action()`)
- `k8s_executor.py` - Kubernetes executor (⏳ **Currently used, but K8s not available locally**)
- `action_validator.py` - Safety checks and cooldown periods
- `approval_client.py` - Approval dashboard API client

**Executor Methods Called:**
```python
# Currently using K8sExecutor (line 40-43)
self.k8s_executor = K8sExecutor(
    in_cluster=config.k8s_in_cluster,
    namespace=config.k8s_namespace,
    dry_run=config.k8s_dry_run
)

# Calls these methods (lines 349-370):
await self.k8s_executor.scale_deployment(name, replicas, namespace)
await self.k8s_executor.restart_pods(deployment, namespace)
await self.k8s_executor.rollback_deployment(name, namespace)
```

**⏳ Option 2 Goal:** Replace K8sExecutor with abstraction that supports Docker Compose

---

### 4. **Notifier Agent** 📢

**Purpose:** Sends rich Slack notifications with context

**File:** `services/notifier-agent/app/main.py`

**What it does:**
- Listens for all agent events
- Formats messages using Slack Block Kit
- Sends to configured Slack channel (#devopsalerts)
- Message types: Incident detected, Analysis complete, Action executed, Approval pending

---

### 5. **Memory Agent** 🧠💾

**Purpose:** Stores incidents and detects patterns for continuous learning

**File:** `services/memory-agent/app/main.py`

**What it does:**
- Stores all incidents in PostgreSQL (4 tables)
- Generates embeddings using OpenAI (text-embedding-3-small, 1536 dimensions)
- Stores embeddings in Qdrant vector database
- Detects patterns:
  1. **Exact Match:** Same metric + target recurring (SQL GROUP BY)
  2. **Semantic:** Similar issues via vector clustering (similarity ≥ 0.85)
  3. **Temporal:** Time-based patterns (day of week + hour analysis)

---

## 🔄 Complete Event Flow

### Example: Memory Leak Incident

```
1. test-app: Memory leak starts (POST /trigger-memory)
   └─> Allocates 50MB every 10 seconds

2. test-app: Exposes metric at /metrics
   └─> test_app_memory_mb = 500

3. Prometheus: Scrapes metrics every 15s
   └─> Stores time series data

4. monitoring-agent: Queries Prometheus
   └─> SELECT test_app_memory_mb WHERE job='test-app'
   └─> Checks: 500 > threshold (400) = BREACH!
   └─> Publishes: monitoring.incident.detected

5. RabbitMQ: Routes event to all subscribers

6. analyzer-agent: Receives incident event
   └─> Fetches logs (optional)
   └─> Searches similar incidents in Qdrant (RAG)
   └─> Builds prompt with context
   └─> Calls LLM Service: "Analyze this incident..."
   └─> LLM responds: "Root cause: Memory leak. Recommendation: Restart service"
   └─> ActionMapper parses: {action_type: "restart_pods", target: "test-app"}
   └─> Publishes: analyzer.analysis.complete

7. auto-response-agent: Receives analysis event
   └─> Validates recommendation
   └─> Checks confidence (85%) and criticality (medium)
   └─> Decision: Auto-execute (confidence ≥ 80%, criticality ≤ medium)
   └─> Calls executor.restart_pods("test-app")
   └─> ERROR: K8s client not available! ⚠️ (This is the problem!)
   └─> Publishes: autoresponse.action.failed

8. notifier-agent: Sends Slack notification
   └─> "❌ Failed to execute action: K8s client not available"
```

**⏳ The Problem:** Step 7 fails because we're using Docker Compose locally, not Kubernetes!

---

## 🐳 Current Deployment Architecture

### Local Environment (Docker Compose)

**File:** `docker-compose.yml`

**Services Running:**
1. `test-app` - Flask app with chaos endpoints (Port 8080)
2. `prometheus` - Metrics collection (Port 9090)
3. `monitoring-agent` - Detects incidents
4. `analyzer-agent` - Analyzes with LLM
5. `auto-response-agent` - Executes healing ⚠️ **Currently broken**
6. `notifier-agent` - Sends Slack alerts
7. `memory-agent` - Stores incidents
8. `llm-service` - LLM API wrapper (Port 8000)
9. `rabbitmq` - Event bus (Port 5672, Management: 15672)
10. `postgres` - Incident storage (Port 5432)
11. `grafana` - Dashboards (Port 3002)

**Key Configuration (docker-compose.yml lines 150-199):**
```yaml
monitoring-agent:
  environment:
    - MONITORING_PROMETHEUS_URL=http://prometheus:9090  # NOT K8s!
    - MONITORING_K8S_IN_CLUSTER=false
    - MONITORING_K8S_NAMESPACE=default
```

**This confirms: System uses Docker Compose + Prometheus, NOT Kubernetes locally**

---

## 🔍 Test App - Chaos Engineering

**File:** `services/test-app/app/main.py`

**Purpose:** Deliberately generates incidents for testing

**Chaos Endpoints:**

| Endpoint | Action | Result |
|----------|--------|--------|
| `POST /trigger-memory` | Memory leak | Allocates 50MB every 10s |
| `POST /trigger-cpu` | CPU burn | Busy loop consuming 80%+ CPU for 2 min |
| `POST /trigger-errors` | HTTP 500s | 30% of requests return 500 |
| `POST /trigger-crash` | Crash app | Force exit after 2s |
| `POST /reset` | Stop chaos | Clears all active scenarios |
| `GET /status` | Check state | Returns current chaos status |
| `GET /metrics` | Prometheus | Exposes metrics for scraping |

**Metrics Exposed:**
```python
test_app_requests_total{endpoint="/health", status="200"}
test_app_errors_total
test_app_cpu_percent
test_app_memory_mb
test_app_chaos_active{type="memory"}
```

---

## ⚠️ Current Problem (Option 2)

### What's Broken:

**File:** `services/auto-response-agent/app/main.py` (line 40-43)

```python
self.k8s_executor = K8sExecutor(
    in_cluster=config.k8s_in_cluster,  # False
    namespace=config.k8s_namespace,
    dry_run=config.k8s_dry_run
)
```

**File:** `services/auto-response-agent/app/k8s_executor.py` (line 31-46)

```python
try:
    if in_cluster:
        k8s_config.load_incluster_config()
    else:
        k8s_config.load_kube_config()  # ⚠️ Fails - no kubeconfig!

    self.apps_v1 = client.AppsV1Api()
    self.core_v1 = client.CoreV1Api()
    self.available = True

except Exception as e:
    logger.warning(f"Kubernetes client not available: {e}")
    self.available = False  # ⚠️ Always False in local environment
```

**When executing actions (line 75-76):**
```python
if not self.is_available():
    raise RuntimeError("Kubernetes client not available")  # ⚠️ Always fails!
```

**Result:** Auto-response agent cannot execute ANY actions in local Docker Compose environment!

---

## ✅ Solution (Option 2): Docker Compose Executor

### Goal:
Create abstraction that supports both Kubernetes (production) and Docker Compose (local).

### Architecture Design:

```
┌─────────────────────────────────────────────────────────────┐
│                  ExecutorFactory                            │
│  • Auto-detects environment (K8s or Docker)                 │
│  • Returns appropriate executor instance                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌──────────────┐        ┌──────────────┐
│BaseExecutor  │        │BaseExecutor  │
│  (abstract)  │        │  (abstract)  │
└──────┬───────┘        └──────┬───────┘
       │                       │
       ▼                       ▼
┌──────────────┐        ┌──────────────┐
│K8sExecutor   │        │DockerCompose │
│              │        │  Executor    │
│ • restart()  │        │              │
│ • scale()    │        │ • restart()  │
│ • rollback() │        │ • scale()    │
└──────────────┘        │ • rollback() │
                        └──────────────┘
```

### Files to Create:

```
auto-response-agent/app/
  executors/
    __init__.py               # Exports
    base.py                   # BaseExecutor abstract class
    docker_executor.py        # DockerComposeExecutor
    k8s_executor.py           # K8sExecutor (refactored)
    factory.py                # ExecutorFactory
```

### DockerComposeExecutor Implementation:

**Will execute these commands:**
```bash
# Restart service
docker-compose -f /compose/docker-compose.yml restart test-app

# Scale service
docker-compose -f /compose/docker-compose.yml up -d --scale test-app=3

# Check services
docker-compose -f /compose/docker-compose.yml config --services

# Check status
docker-compose -f /compose/docker-compose.yml ps test-app
```

### Integration Changes:

**Before (main.py line 40-43):**
```python
self.k8s_executor = K8sExecutor(...)
```

**After:**
```python
from app.executors.factory import ExecutorFactory

self.executor = ExecutorFactory.create_executor(
    executor_type=config.executor_type,  # 'auto', 'docker-compose', or 'kubernetes'
    config=config
)
```

### Environment Configuration:

**docker-compose.yml changes:**
```yaml
auto-response-agent:
  environment:
    - EXECUTOR_TYPE=docker-compose
    - DOCKER_COMPOSE_FILE=/compose/docker-compose.yml
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock  # ⚠️ Security: Full Docker access
    - ./docker-compose.yml:/compose/docker-compose.yml:ro
```

---

## 📋 Implementation Plan (Option 2)

### Phase 1: Code Discovery & Analysis ✅ COMPLETE
- Located K8sExecutor implementation
- Understood integration points
- Verified Docker Compose architecture

### Phase 2: Design Executor Abstraction ⏳ IN PROGRESS
- Design BaseExecutor abstract class
- Design DockerComposeExecutor
- Design ExecutorFactory

### Phase 3: Implementation
- Create executors/ module
- Implement base.py
- Implement docker_executor.py
- Refactor k8s_executor.py
- Implement factory.py
- Update main.py integration
- Update docker-compose.yml

### Phase 4: Testing
- Unit tests for Docker executor
- Unit tests for factory
- Integration tests
- E2E test: Trigger chaos → Auto-healing

### Phase 5: Validation & Documentation
- Test multiple chaos scenarios
- Verify metrics
- Update documentation

---

## 🎯 Success Criteria

**Option 2 is complete when:**

1. ✅ Auto-response-agent uses DockerComposeExecutor
2. ✅ Executor can restart Docker Compose services
3. ✅ Complete flow works: chaos → incident → analysis → auto-healing → chaos cleared
4. ✅ Test-app container actually restarts (verified with `docker inspect`)
5. ✅ No "K8s client not available" errors
6. ✅ All tests pass
7. ✅ Documentation complete

**Expected Flow After Implementation:**
```
test-app: Memory leak triggered (50MB/10s)
monitoring-agent: ⚠️ Incident detected: test_app_memory_mb > threshold
analyzer-agent: 🔍 Analyzing with GPT-4...
analyzer-agent: ✓ Root cause: Memory leak. Recommendation: RESTART test-app
auto-response-agent: Using executor: docker-compose ✅
auto-response-agent: Validating action: RESTART test-app
auto-response-agent: Decision: Auto-execute (confidence: 85%)
auto-response-agent: Executing: docker-compose restart test-app
auto-response-agent: ✓ Successfully restarted test-app in 2.3s ✅
test-app: [Container restarted - chaos cleared]
test-app: Memory: 120MB (back to normal) ✅
notifier-agent: ✅ Action executed successfully
```

---

## 🔒 Security Considerations

**⚠️ CRITICAL: Docker Socket Access**

Mounting `/var/run/docker.sock` gives **FULL Docker control:**
- Can start/stop ANY container
- Can access host filesystem
- Can escalate privileges
- Can break out of container

**Mitigations:**
1. Only use in trusted dev environments
2. For production, use Kubernetes with RBAC
3. Add action validation (whitelist services)
4. Add approval workflow for risky actions
5. Implement audit logging
6. Consider Docker API with TLS instead of socket

---

## 📊 Key Metrics to Monitor

**Grafana Dashboard (http://localhost:3002):**

| Metric | Description | Target |
|--------|-------------|--------|
| `monitoring_incidents_detected_total` | Incidents detected | > 0 |
| `analyzer_recommendations_generated_total` | Recommendations generated | > 0 |
| `autoresponse_actions_executed_total` | Actions executed | > 0 |
| `autoresponse_execution_success_total` | Successful executions | = executed |
| `autoresponse_execution_failures_total` | Failed executions | 0 |
| `incident_resolution_time_seconds` | Time to resolution | < 120s |

---

## 🚀 Quick Start Commands

### Check System Status
```bash
cd devopsagent-main
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f monitoring-agent
docker-compose logs -f analyzer-agent
docker-compose logs -f auto-response-agent
```

### Trigger Test Incident
```bash
# Trigger memory leak
curl -X POST http://localhost:8080/trigger-memory

# Check status
curl http://localhost:8080/status | jq

# Reset chaos
curl -X POST http://localhost:8080/reset
```

### Monitor Event Flow
```bash
# Terminal 1: Monitoring
docker-compose logs -f monitoring-agent | grep "Incident detected"

# Terminal 2: Analyzer
docker-compose logs -f analyzer-agent | grep "recommendation"

# Terminal 3: Auto-Response
docker-compose logs -f auto-response-agent | grep "Executing"

# Terminal 4: Test App
docker-compose logs -f test-app | grep "restart"
```

---

## 📚 Key Files Reference

### Agent Main Files
| Agent | Main File | Purpose |
|-------|-----------|---------|
| Monitoring | `services/monitoring-agent/app/main.py` | Detect incidents |
| Analyzer | `services/analyzer-agent/app/main.py` | Analyze with LLM |
| Auto-Response | `services/auto-response-agent/app/main.py` | Execute healing |
| Notifier | `services/notifier-agent/app/main.py` | Send Slack alerts |
| Memory | `services/memory-agent/app/main.py` | Store incidents |

### Critical Configuration
| File | Lines | Purpose |
|------|-------|---------|
| `docker-compose.yml` | 150-199 | Monitoring agent config |
| `docker-compose.yml` | 200-250 | Auto-response agent config |
| `services/auto-response-agent/app/main.py` | 40-43 | Executor initialization |
| `services/auto-response-agent/app/k8s_executor.py` | 31-46 | K8s client initialization |
| `services/analyzer-agent/app/action_mapper.py` | 1-300 | LLM to action mapping |

---

## ✅ Current Status

**Option 1 (Action Mapping):** ✅ COMPLETE (October 30, 2025)
- Analyzer generates 1-2 actionable recommendations per incident
- No more "Could not map action" errors
- ActionMapper properly parses LLM recommendations

**Option 2 (Docker Executor):** ⏳ IN PROGRESS
- **Phase 1:** ✅ Complete (Code discovery)
- **Phase 2:** ⏳ In Progress (Design abstraction)
- **Phase 3:** Pending (Implementation)
- **Phase 4:** Pending (Testing)
- **Phase 5:** Pending (Validation)

**Combined Status:** 50% complete
- Incident detection: ✅ Working
- Root cause analysis: ✅ Working
- Recommendation generation: ✅ Working
- Action execution: ⚠️ Broken (needs Docker executor)

---

## 🎯 Next Steps

1. **Complete Phase 2:** Design executor abstraction (BaseExecutor, DockerComposeExecutor, ExecutorFactory)
2. **Start Phase 3:** Implement all executor classes
3. **Integrate:** Update main.py to use factory pattern
4. **Test:** E2E test with chaos scenarios
5. **Validate:** Confirm complete auto-healing works

**Once Option 2 is complete, the system will have full autonomous incident response!** 🎉

---

**This document provides complete understanding of the system and is ready for implementation.**
