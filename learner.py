from sqlalchemy.orm import Session
from models import IssueMemory

# Default action map per metric
DEFAULT_ACTIONS = {
    "cpu_usage":  "kill_high_cpu",
    "ram_usage":  "free_memory",
    "disk_usage": "free_memory",
}


def record_issue(db: Session, metric: str, value: float, action_taken: str) -> IssueMemory:
    """Store a new issue + action taken into memory."""
    issue = IssueMemory(
        metric=metric,
        value=value,
        action_taken=action_taken,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def apply_feedback(db: Session, issue_id: int, worked: bool, notes: str = None) -> IssueMemory:
    """Record whether the action worked and update the score."""
    issue = db.query(IssueMemory).filter(IssueMemory.id == issue_id).first()
    if not issue:
        return None

    issue.worked = worked
    issue.notes  = notes

    # Recalculate score: % of times this action worked for this metric
    all_feedback = db.query(IssueMemory).filter(
        IssueMemory.metric       == issue.metric,
        IssueMemory.action_taken == issue.action_taken,
        IssueMemory.worked       != None
    ).all()

    if all_feedback:
        success_count = sum(1 for i in all_feedback if i.worked)
        new_score = round(success_count / len(all_feedback), 2)
        # Update score on all records for this metric+action
        db.query(IssueMemory).filter(
            IssueMemory.metric       == issue.metric,
            IssueMemory.action_taken == issue.action_taken
        ).update({"score": new_score})

    db.commit()
    db.refresh(issue)
    return issue


def suggest_action(db: Session, metric: str) -> dict:
    """
    Suggest the best action for a metric based on past success scores.
    Falls back to default if no history exists.
    """
    # Get all distinct actions tried for this metric with feedback
    records = db.query(IssueMemory).filter(
        IssueMemory.metric  == metric,
        IssueMemory.worked  != None
    ).all()

    if not records:
        default = DEFAULT_ACTIONS.get(metric, "free_memory")
        return {
            "metric":     metric,
            "suggestion": default,
            "score":      None,
            "reason":     "No history yet — using default action."
        }

    # Group scores by action
    action_scores = {}
    for r in records:
        if r.action_taken not in action_scores:
            action_scores[r.action_taken] = []
        action_scores[r.action_taken].append(1 if r.worked else 0)

    best_action = max(action_scores, key=lambda a: sum(action_scores[a]) / len(action_scores[a]))
    best_score  = round(sum(action_scores[best_action]) / len(action_scores[best_action]), 2)

    return {
        "metric":     metric,
        "suggestion": best_action,
        "score":      best_score,
        "reason":     f"Best historical success rate: {best_score * 100:.0f}%"
    }
