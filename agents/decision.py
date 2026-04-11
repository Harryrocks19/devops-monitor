from datetime import datetime
from learner import suggest_action


class DecisionAgent:
    """
    Takes the analyst report.
    Decides what action to take for each issue using the learner.
    """
    name = "DecisionAgent"

    def run(self, db, analyst_report: dict) -> dict:
        decisions = []

        for issue in analyst_report.get("issues", []):
            metric     = issue["metric"]
            suggestion = suggest_action(db, metric)

            decisions.append({
                "metric":     metric,
                "value":      issue["value"],
                "severity":   issue["severity"],
                "action":     suggestion["suggestion"],
                "confidence": suggestion["score"],
                "reason":     suggestion["reason"],
            })

        # Also flag anomalies that aren't already in issues
        issue_metrics = {i["metric"] for i in analyst_report.get("issues", [])}
        for anomaly in analyst_report.get("anomalies", []):
            if anomaly["metric"] not in issue_metrics:
                suggestion = suggest_action(db, anomaly["metric"])
                decisions.append({
                    "metric":     anomaly["metric"],
                    "value":      anomaly["value"],
                    "severity":   "anomaly",
                    "action":     suggestion["suggestion"],
                    "confidence": suggestion["score"],
                    "reason":     f"Anomaly detected (z={anomaly['z_score']}). {suggestion['reason']}",
                })

        return {
            "agent":     self.name,
            "timestamp": datetime.now().isoformat(),
            "decisions": decisions,
            "total":     len(decisions),
        }
