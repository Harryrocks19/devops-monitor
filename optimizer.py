import numpy as np
from sqlalchemy.orm import Session
from models import MetricRecord


def optimize(db: Session) -> dict:
    """
    Analyze historical metrics and suggest resource optimizations.
    """
    records = db.query(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(100).all()

    if len(records) < 10:
        return {"error": "Need at least 10 records for optimization analysis."}

    cpu_vals  = np.array([r.cpu_usage  for r in records], dtype=float)
    ram_vals  = np.array([r.ram_usage  for r in records], dtype=float)
    disk_vals = np.array([r.disk_usage for r in records], dtype=float)

    suggestions = []

    # CPU optimization
    cpu_avg, cpu_max = cpu_vals.mean(), cpu_vals.max()
    if cpu_avg < 20 and cpu_max < 50:
        suggestions.append({
            "resource": "CPU",
            "status":   "underutilized",
            "avg":      round(cpu_avg, 2),
            "max":      round(cpu_max, 2),
            "suggestion": "Consider downsizing instance type to save cost. Average CPU is very low."
        })
    elif cpu_avg > 70:
        suggestions.append({
            "resource": "CPU",
            "status":   "overloaded",
            "avg":      round(cpu_avg, 2),
            "max":      round(cpu_max, 2),
            "suggestion": "Consider upgrading instance type or adding horizontal scaling."
        })
    else:
        suggestions.append({
            "resource": "CPU",
            "status":   "optimal",
            "avg":      round(cpu_avg, 2),
            "max":      round(cpu_max, 2),
            "suggestion": "CPU usage is within optimal range."
        })

    # RAM optimization
    ram_avg, ram_max = ram_vals.mean(), ram_vals.max()
    if ram_avg < 30:
        suggestions.append({
            "resource": "RAM",
            "status":   "underutilized",
            "avg":      round(ram_avg, 2),
            "max":      round(ram_max, 2),
            "suggestion": "RAM is underutilized. Consider reducing memory allocation."
        })
    elif ram_avg > 75:
        suggestions.append({
            "resource": "RAM",
            "status":   "overloaded",
            "avg":      round(ram_avg, 2),
            "max":      round(ram_max, 2),
            "suggestion": "High RAM usage detected. Consider adding more memory or optimizing app."
        })
    else:
        suggestions.append({
            "resource": "RAM",
            "status":   "optimal",
            "avg":      round(ram_avg, 2),
            "max":      round(ram_max, 2),
            "suggestion": "RAM usage is within optimal range."
        })

    # Disk optimization
    disk_avg = disk_vals.mean()
    if disk_avg > 80:
        suggestions.append({
            "resource": "Disk",
            "status":   "critical",
            "avg":      round(disk_avg, 2),
            "suggestion": "Disk usage is critically high. Clean up logs or expand storage."
        })
    else:
        suggestions.append({
            "resource": "Disk",
            "status":   "optimal",
            "avg":      round(disk_avg, 2),
            "suggestion": "Disk usage is fine."
        })

    # Overall efficiency score (0-100)
    efficiency = round(100 - (
        max(0, cpu_avg - 50) * 0.4 +
        max(0, ram_avg - 50) * 0.4 +
        max(0, disk_avg - 70) * 0.2
    ), 2)

    return {
        "records_analyzed": len(records),
        "efficiency_score": max(0, efficiency),
        "suggestions":      suggestions,
    }
