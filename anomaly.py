import numpy as np

def detect_anomalies(records: list) -> list:
    """
    Z-score anomaly detection on last N records.
    A metric is anomalous if its latest value is > 2 std deviations from mean.
    """
    if len(records) < 5:
        return []

    metrics = ["cpu_usage", "ram_usage", "disk_usage"]
    anomalies = []

    for metric in metrics:
        values = np.array([getattr(r, metric) for r in records], dtype=float)
        mean, std = values.mean(), values.std()

        if std == 0:
            continue

        latest = values[-1]
        z_score = abs((latest - mean) / std)

        if z_score > 2.0:
            anomalies.append({
                "metric":  metric,
                "value":   round(latest, 2),
                "mean":    round(mean, 2),
                "std":     round(std, 2),
                "z_score": round(z_score, 2),
                "message": f"🔍 Anomaly in {metric.replace('_', ' ').title()}: value={latest:.1f}%, z={z_score:.2f}"
            })

    return anomalies
