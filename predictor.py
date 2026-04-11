import numpy as np
from sklearn.linear_model import LinearRegression

def predict_next(records: list) -> dict:
    """
    Predict next value for CPU, RAM, Disk using LinearRegression
    on the last N records.
    """
    if len(records) < 5:
        return {"error": "Not enough data. Need at least 5 records."}

    metrics = ["cpu_usage", "ram_usage", "disk_usage"]
    predictions = {}
    X = np.arange(len(records)).reshape(-1, 1)
    next_x = np.array([[len(records)]])

    for metric in metrics:
        y = np.array([getattr(r, metric) for r in records], dtype=float)
        model = LinearRegression()
        model.fit(X, y)
        predicted = float(model.predict(next_x)[0])
        predicted = max(0.0, min(100.0, predicted))  # clamp 0-100
        predictions[metric] = round(predicted, 2)

    return predictions
