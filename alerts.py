ALERT_THRESHOLDS = {
    "cpu_usage":  80.0,
    "ram_usage":  80.0,
    "disk_usage": 90.0,
}

def check_alerts(data: dict) -> list:
    fired = []
    for metric, threshold in ALERT_THRESHOLDS.items():
        value = data.get(metric, 0)
        if value > threshold:
            fired.append({
                "metric":    metric,
                "value":     value,
                "threshold": threshold,
                "message":   f"⚠️ {metric.replace('_', ' ').title()} is {value}% (limit: {threshold}%)"
            })
    return fired
