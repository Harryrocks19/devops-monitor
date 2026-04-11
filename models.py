from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from database import Base
from datetime import datetime

class MetricRecord(Base):
    __tablename__ = "metrics"

    id             = Column(Integer, primary_key=True, index=True)
    timestamp      = Column(DateTime, default=datetime.utcnow)
    cpu_usage      = Column(Float)
    ram_usage      = Column(Float)
    disk_usage     = Column(Float)
    net_bytes_sent = Column(Float)
    net_bytes_recv = Column(Float)
    alert          = Column(String, nullable=True)


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id        = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric    = Column(String)
    value     = Column(Float)
    threshold = Column(Float)
    message   = Column(String)


class ActionLog(Base):
    __tablename__ = "action_logs"

    id           = Column(Integer, primary_key=True, index=True)
    timestamp    = Column(DateTime, default=datetime.utcnow)
    action       = Column(String)
    target       = Column(String, nullable=True)
    success      = Column(Boolean)
    message      = Column(String)
    triggered_by = Column(String, nullable=True)  # 'auto' or 'manual'


class IssueMemory(Base):
    __tablename__ = "issue_memory"

    id           = Column(Integer, primary_key=True, index=True)
    timestamp    = Column(DateTime, default=datetime.utcnow)
    metric       = Column(String)
    value        = Column(Float)
    action_taken = Column(String)
    worked       = Column(Boolean, nullable=True)
    score        = Column(Float, default=0.0)
    notes        = Column(String, nullable=True)


class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"

    id                = Column(Integer, primary_key=True, index=True)
    started_at        = Column(DateTime, default=datetime.utcnow)
    system_status     = Column(String)
    issues_found      = Column(Integer)
    actions_taken     = Column(Integer)
    actions_succeeded = Column(Integer)
    summary           = Column(String, nullable=True)


class SimulationLog(Base):
    __tablename__ = "simulation_logs"

    id          = Column(Integer, primary_key=True, index=True)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    scenario    = Column(String)
    total_alerts = Column(Integer)
    max_cpu     = Column(Float)
    max_ram     = Column(Float)
    max_disk    = Column(Float)


class MonitorTarget(Base):
    __tablename__ = "monitor_targets"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String)
    url       = Column(String)
    active    = Column(Boolean, default=True)
    added_at  = Column(DateTime, default=datetime.utcnow)
