from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MetricOut(BaseModel):
    id:             int
    timestamp:      datetime
    cpu_usage:      float
    ram_usage:      float
    disk_usage:     float
    net_bytes_sent: float
    net_bytes_recv: float
    alert:          Optional[str]

    class Config:
        from_attributes = True


class AlertLogOut(BaseModel):
    id:        int
    timestamp: datetime
    metric:    str
    value:     float
    threshold: float
    message:   str

    class Config:
        from_attributes = True


class ActionLogOut(BaseModel):
    id:           int
    timestamp:    datetime
    action:       str
    target:       Optional[str]
    success:      bool
    message:      str
    triggered_by: Optional[str]

    class Config:
        from_attributes = True


class TriggerActionRequest(BaseModel):
    action: str
    target: Optional[str] = None


class IssueMemoryOut(BaseModel):
    id:           int
    timestamp:    datetime
    metric:       str
    value:        float
    action_taken: str
    worked:       Optional[bool]
    score:        float
    notes:        Optional[str]

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    issue_id: int
    worked:   bool
    notes:    Optional[str] = None


class AgentRunOut(BaseModel):
    id:                int
    started_at:        datetime
    system_status:     str
    issues_found:      int
    actions_taken:     int
    actions_succeeded: int
    summary:           Optional[str]

    class Config:
        from_attributes = True


class MonitorTargetIn(BaseModel):
    name: str
    url:  str


class MonitorTargetOut(BaseModel):
    id:       int
    name:     str
    url:      str
    active:   bool
    added_at: datetime

    class Config:
        from_attributes = True


class SimulationLogOut(BaseModel):
    id:           int
    timestamp:    datetime
    scenario:     str
    total_alerts: int
    max_cpu:      float
    max_ram:      float
    max_disk:     float

    class Config:
        from_attributes = True
