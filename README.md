# DevOps Monitor 🚀

An intelligent, self-healing DevOps monitoring system with AI agents, ML prediction, and cloud deployment.

## Tech Stack
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL
- **ML**: scikit-learn, numpy
- **Deployment**: Docker, GitHub Actions CI/CD, AWS EC2 (Ubuntu)

## Levels Progress
- [x] Level 1 — Foundation (FastAPI + System Metrics)
- [x] Level 2 — Data & Storage (PostgreSQL + History API)
- [x] Level 3 — Dashboard (Live graphs + Alert banner)
- [x] Level 4 — Intelligence (Rule alerts + Anomaly detection + ML prediction)
- [x] Level 5 — Automation (Auto-actions + Email alerts + API trigger)
- [x] Level 6 — Learning (Issue memory + Feedback loop + Smart suggestions)
- [x] Level 7 — Agent System (Analyst + Decision + Executor agents)
- [x] Level 8 — DevOps + Cloud (Docker + CI/CD + AWS EC2)
- [x] Level 9 — Advanced (Optimizer + Simulator + Quantum + Multi-monitor)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Home |
| `GET /dashboard` | Live monitoring dashboard |
| `GET /metrics` | Live metrics |
| `GET /metrics/history` | Last 50 stored records |
| `GET /alerts` | All fired alert logs |
| `POST /actions/trigger` | Manually trigger an action |
| `GET /actions/log` | All action execution logs |
| `GET /anomaly` | Z-score anomaly detection |
| `GET /predict` | ML prediction for next values |
| `GET /learn/history` | All past issues + actions taken |
| `GET /learn/suggest?metric=cpu_usage` | Best action suggestion |
| `POST /learn/feedback` | Submit feedback on whether action worked |
| `POST /agent/run` | Run full agent pipeline |
| `GET /agent/log` | All agent run history |
| `GET /optimize` | Resource optimization suggestions |
| `GET /simulate?scenario=spike` | Run load simulation |
| `GET /simulate/scenarios` | List available scenarios |
| `GET /quantum` | Quantum circuit optimization |
| `POST /monitor/targets` | Add a system to monitor |
| `GET /monitor/targets` | List all monitored systems |
| `GET /monitor/check` | Check all monitored systems |
| `DELETE /monitor/targets/{id}` | Remove a monitored system |
| `GET /health` | Service health status |

---

## Run Locally (without Docker)

```bash
# 1. Create and activate venv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up .env
cp .env.example .env
# Edit .env — set DATABASE_URL to localhost

# 4. Run
uvicorn main:app --reload
```

---

## Run with Docker (recommended)

```bash
# 1. Set up .env
cp .env.example .env
# Make sure DATABASE_URL uses 'db' as host (already set in .env.example)

# 2. Build and start
docker compose up --build -d

# 3. Open dashboard
# http://localhost:8000/dashboard
```

---

## Deploy on AWS EC2 (Ubuntu)

### Step 1 — Launch EC2
- AMI: Ubuntu 22.04 LTS
- Instance type: t2.micro (free tier)
- Security group: open ports 22, 80, 8000

### Step 2 — Setup EC2
```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
newgrp docker

# Clone your repo
git clone https://github.com/<your-username>/devops-monitor.git
cd devops-monitor

# Set up .env
cp .env.example .env
nano .env   # fill in your values

# Run
docker compose up -d
```

### Step 3 — Setup Nginx (optional, for port 80)
```bash
sudo apt install -y nginx
sudo cp nginx.conf /etc/nginx/sites-available/devops-monitor
sudo ln -s /etc/nginx/sites-available/devops-monitor /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## CI/CD with GitHub Actions

### GitHub Secrets to set
Go to: `GitHub repo → Settings → Secrets → Actions`

| Secret | Value |
|--------|-------|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token |
| `EC2_HOST` | EC2 public IP address |
| `EC2_SSH_KEY` | Contents of your `.pem` key file |

### Pipeline flow
```
Push to main
    │
    ├── test     → starts app + hits /health
    ├── build    → builds Docker image → pushes to DockerHub
    └── deploy   → SSH into EC2 → pulls new image → restarts containers
```
