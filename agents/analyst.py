import psutil
from datetime import datetime
from anomaly import detect_anomalies


class AnalystAgent:
    """
    Reads live system metrics + recent history.
    Produces a situation report for the Decision Agent.
    """
    name = "AnalystAgent"

    def run(self, db) -> dict:
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net  = psutil.net_io_counters()

        metrics = {
            "cpu_usage":      cpu,
            "ram_usage":      ram,
            "disk_usage":     disk,
            "net_bytes_sent": net.bytes_sent,
            "net_bytes_recv": net.bytes_recv,
        }

        # Pull last 20 records for anomaly check
        from models import MetricRecord
        recent = list(reversed(
            db.query(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(20).all()
        ))
        anomalies = detect_anomalies(recent)

        # Identify which metrics are critical
        issues = []
        if cpu > 80:
            issues.append({"metric": "cpu_usage",  "value": cpu,  "severity": "high"})
        if ram > 80:
            issues.append({"metric": "ram_usage",  "value": ram,  "severity": "high"})
        if disk > 90:
            issues.append({"metric": "disk_usage", "value": disk, "severity": "critical"})

        return {
            "agent":     self.name,
            "timestamp": datetime.now().isoformat(),
            "metrics":   metrics,
            "issues":    issues,
            "anomalies": anomalies,
            "status":    "critical" if issues else "healthy",
        }
