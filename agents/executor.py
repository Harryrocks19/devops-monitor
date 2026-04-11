from datetime import datetime
from actions import AVAILABLE_ACTIONS
from notifier import send_alert
from learner import record_issue


class ExecutorAgent:
    """
    Takes decisions from DecisionAgent.
    Executes each action, logs results, sends notifications.
    """
    name = "ExecutorAgent"

    def run(self, db, decision_report: dict) -> dict:
        results = []

        for decision in decision_report.get("decisions", []):
            action_key = decision["action"]
            metric     = decision["metric"]
            value      = decision["value"]

            if action_key not in AVAILABLE_ACTIONS:
                results.append({
                    "metric":  metric,
                    "action":  action_key,
                    "success": False,
                    "message": f"❌ Unknown action: {action_key}",
                })
                continue

            # Execute action
            result = AVAILABLE_ACTIONS[action_key]()

            # Record in issue memory for future learning
            record_issue(db, metric=metric, value=value, action_taken=action_key)

            # Notify
            send_alert(
                result["message"],
                subject=f"🤖 Agent Action: {action_key} on {metric}"
            )

            results.append({
                "metric":   metric,
                "action":   action_key,
                "success":  result.get("success", False),
                "message":  result.get("message", ""),
                "severity": decision["severity"],
            })

        success_count = sum(1 for r in results if r["success"])

        return {
            "agent":         self.name,
            "timestamp":     datetime.now().isoformat(),
            "actions_taken": results,
            "total":         len(results),
            "succeeded":     success_count,
            "failed":        len(results) - success_count,
        }
