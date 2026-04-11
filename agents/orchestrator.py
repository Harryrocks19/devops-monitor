from datetime import datetime
from agents.analyst  import AnalystAgent
from agents.decision import DecisionAgent
from agents.executor import ExecutorAgent


class AgentOrchestrator:
    """
    Runs the full agent pipeline:
    AnalystAgent → DecisionAgent → ExecutorAgent
    """

    def __init__(self):
        self.analyst  = AnalystAgent()
        self.decision = DecisionAgent()
        self.executor = ExecutorAgent()

    def run(self, db) -> dict:
        started_at = datetime.now().isoformat()

        # Step 1: Analyse
        analyst_report  = self.analyst.run(db)

        # Step 2: Decide
        decision_report = self.decision.run(db, analyst_report)

        # Step 3: Execute
        executor_report = self.executor.run(db, decision_report)

        return {
            "pipeline":  "AnalystAgent → DecisionAgent → ExecutorAgent",
            "started_at": started_at,
            "finished_at": datetime.now().isoformat(),
            "system_status": analyst_report["status"],
            "analyst":   analyst_report,
            "decision":  decision_report,
            "executor":  executor_report,
        }
