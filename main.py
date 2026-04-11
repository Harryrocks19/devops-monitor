from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
import psutil
from datetime import datetime
import logging
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import MetricRecord, AlertLog, ActionLog, IssueMemory, AgentRunLog, SimulationLog, MonitorTarget
from schemas import (
    MetricOut, AlertLogOut, ActionLogOut, TriggerActionRequest,
    IssueMemoryOut, FeedbackRequest, AgentRunOut,
    MonitorTargetIn, MonitorTargetOut, SimulationLogOut
)
from alerts import check_alerts
from anomaly import detect_anomalies
from predictor import predict_next
from actions import AVAILABLE_ACTIONS, restart_service
from notifier import send_alert
from learner import record_issue, apply_feedback, suggest_action
from agents.orchestrator import AgentOrchestrator
from optimizer import optimize
from simulator import run_simulation, SCENARIOS
from quantum_module import quantum_optimize
from multi_monitor import check_all_targets

Base.metadata.create_all(bind=engine)

logging.basicConfig(
    filename="metrics.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

app = FastAPI(title="DevOps Monitor", version="9.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def log_action(db: Session, result: dict, triggered_by: str = "manual"):
    entry = ActionLog(
        action=result.get("action", "unknown"),
        target=result.get("target"),
        success=result.get("success", False),
        message=result.get("message", ""),
        triggered_by=triggered_by
    )
    db.add(entry)
    db.commit()


@app.get("/")
def home():
    return {"message": "DevOps Monitor Running 🚀", "version": "9.0.0"}


@app.get("/dashboard", response_class=FileResponse)
def dashboard():
    return FileResponse("index.html")


@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net  = psutil.net_io_counters()

    data = {
        "cpu_usage":      cpu,
        "ram_usage":      ram,
        "disk_usage":     disk,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
    }

    fired_alerts = check_alerts(data)
    alert = fired_alerts[0]["message"] if fired_alerts else None

    record = MetricRecord(**data, alert=alert)
    db.add(record)

    for a in fired_alerts:
        db.add(AlertLog(
            metric=a["metric"],
            value=a["value"],
            threshold=a["threshold"],
            message=a["message"]
        ))
        send_alert(a["message"])

        # Use learner to pick best action
        suggestion = suggest_action(db, a["metric"])
        action_key = suggestion["suggestion"]

        if action_key in AVAILABLE_ACTIONS:
            result = AVAILABLE_ACTIONS[action_key]()
            log_action(db, result, triggered_by="auto")
            # Record in issue memory
            record_issue(db, metric=a["metric"], value=a["value"], action_taken=action_key)

    db.commit()
    logging.info({"data": data, "alerts": fired_alerts})

    return {
        "status":    "success",
        "timestamp": datetime.now().isoformat(),
        "data":      data,
        "alerts":    fired_alerts,
    }


@app.get("/metrics/history", response_model=List[MetricOut])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(limit).all()


@app.get("/alerts", response_model=List[AlertLogOut])
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(limit).all()


@app.post("/actions/trigger")
def trigger_action(req: TriggerActionRequest, db: Session = Depends(get_db)):
    if req.action == "restart_service":
        if not req.target:
            raise HTTPException(status_code=400, detail="'target' is required for restart_service.")
        result = restart_service(req.target)
    elif req.action in AVAILABLE_ACTIONS:
        result = AVAILABLE_ACTIONS[req.action]()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action '{req.action}'.")

    log_action(db, result, triggered_by="manual")
    send_alert(result["message"], subject=f"🤖 Action Triggered: {req.action}")

    return {
        "status":    "success",
        "timestamp": datetime.now().isoformat(),
        "result":    result
    }


@app.get("/actions/log", response_model=List[ActionLogOut])
def get_action_log(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(ActionLog).order_by(ActionLog.timestamp.desc()).limit(limit).all()


@app.get("/anomaly")
def get_anomaly(db: Session = Depends(get_db)):
    records = list(reversed(
        db.query(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(20).all()
    ))
    anomalies = detect_anomalies(records)
    return {
        "status":    "success",
        "timestamp": datetime.now().isoformat(),
        "anomalies": anomalies,
        "count":     len(anomalies)
    }


@app.get("/predict")
def get_prediction(db: Session = Depends(get_db)):
    records = list(reversed(
        db.query(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(30).all()
    ))
    return {
        "status":      "success",
        "timestamp":   datetime.now().isoformat(),
        "predictions": predict_next(records)
    }


# ── Level 6: Learning endpoints ──────────────────────────────────────────────

@app.get("/learn/history", response_model=List[IssueMemoryOut])
def learn_history(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(IssueMemory).order_by(IssueMemory.timestamp.desc()).limit(limit).all()


@app.get("/learn/suggest")
def learn_suggest(metric: str, db: Session = Depends(get_db)):
    valid = ["cpu_usage", "ram_usage", "disk_usage"]
    if metric not in valid:
        raise HTTPException(status_code=400, detail=f"metric must be one of {valid}")
    return suggest_action(db, metric)


@app.post("/learn/feedback")
def learn_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    issue = apply_feedback(db, req.issue_id, req.worked, req.notes)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue ID {req.issue_id} not found.")
    return {
        "status":  "success",
        "message": f"Feedback recorded. New score for '{issue.action_taken}' on '{issue.metric}': {issue.score}",
        "issue":   IssueMemoryOut.model_validate(issue)
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "time":   datetime.now().isoformat()
    }


# ── Level 7: Agent System endpoints ─────────────────────────────────────────

orchestrator = AgentOrchestrator()

@app.post("/agent/run")
def agent_run(db: Session = Depends(get_db)):
    report = orchestrator.run(db)

    # Persist run summary to DB
    log = AgentRunLog(
        started_at        = datetime.fromisoformat(report["started_at"]),
        system_status     = report["system_status"],
        issues_found      = report["decision"]["total"],
        actions_taken     = report["executor"]["total"],
        actions_succeeded = report["executor"]["succeeded"],
        summary           = f"Issues: {report['decision']['total']}, Actions: {report['executor']['total']}, Succeeded: {report['executor']['succeeded']}"
    )
    db.add(log)
    db.commit()

    return {
        "status": "success",
        "report": report
    }


@app.get("/agent/log", response_model=List[AgentRunOut])
def agent_log(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(AgentRunLog).order_by(AgentRunLog.started_at.desc()).limit(limit).all()


# ── Level 9: Advanced endpoints ─────────────────────────────────────────

# ─ Optimization ──────────────────────────────────────────────────────────────────
@app.get("/optimize")
def get_optimization(db: Session = Depends(get_db)):
    result = optimize(db)
    return {
        "status":    "success",
        "timestamp": datetime.now().isoformat(),
        "result":    result
    }


# ─ Simulation ───────────────────────────────────────────────────────────────────
@app.get("/simulate")
def simulate(scenario: str = "normal", db: Session = Depends(get_db)):
    result = run_simulation(scenario)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Save simulation log
    log = SimulationLog(
        scenario=scenario,
        total_alerts=result["total_alerts"],
        max_cpu=result["summary"]["max_cpu"],
        max_ram=result["summary"]["max_ram"],
        max_disk=result["summary"]["max_disk"],
    )
    db.add(log)
    db.commit()
    return result


@app.get("/simulate/scenarios")
def list_scenarios():
    return {
        "available_scenarios": [
            {"name": k, "description": v["description"]}
            for k, v in SCENARIOS.items()
        ]
    }


# ─ Quantum ─────────────────────────────────────────────────────────────────────
@app.get("/quantum")
def quantum(db: Session = Depends(get_db)):
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return quantum_optimize(cpu, ram, disk)


# ─ Multi-system Monitor ────────────────────────────────────────────────────
@app.post("/monitor/targets", response_model=MonitorTargetOut)
def add_target(req: MonitorTargetIn, db: Session = Depends(get_db)):
    target = MonitorTarget(name=req.name, url=req.url)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


@app.get("/monitor/targets", response_model=List[MonitorTargetOut])
def list_targets(db: Session = Depends(get_db)):
    return db.query(MonitorTarget).all()


@app.delete("/monitor/targets/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(MonitorTarget).filter(MonitorTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found.")
    target.active = False
    db.commit()
    return {"status": "success", "message": f"Target '{target.name}' deactivated."}


@app.get("/monitor/check")
async def monitor_check(db: Session = Depends(get_db)):
    return await check_all_targets(db)
