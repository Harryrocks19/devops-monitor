import numpy as np
from datetime import datetime


SCENARIOS = {
    "spike": {
        "description": "Sudden CPU/RAM spike for 5 steps then recovery",
        "steps": 10,
        "cpu_pattern":  [10, 15, 20, 95, 98, 97, 40, 20, 15, 10],
        "ram_pattern":  [40, 42, 45, 88, 90, 85, 55, 45, 42, 40],
        "disk_pattern": [60, 60, 61, 62, 63, 63, 62, 61, 60, 60],
    },
    "gradual": {
        "description": "Gradual increase in all resources over time",
        "steps": 10,
        "cpu_pattern":  [10, 20, 30, 40, 50, 60, 70, 80, 85, 90],
        "ram_pattern":  [30, 35, 40, 48, 55, 62, 70, 75, 80, 85],
        "disk_pattern": [50, 52, 54, 57, 60, 63, 67, 71, 75, 80],
    },
    "stress": {
        "description": "Maximum stress — all resources at critical levels",
        "steps": 10,
        "cpu_pattern":  [85, 88, 90, 92, 95, 97, 98, 99, 99, 100],
        "ram_pattern":  [80, 82, 85, 87, 88, 90, 92, 93, 95, 96],
        "disk_pattern": [88, 89, 90, 91, 92, 93, 94, 95, 96, 97],
    },
    "normal": {
        "description": "Normal healthy system operation",
        "steps": 10,
        "cpu_pattern":  [15, 18, 20, 22, 19, 17, 21, 23, 18, 16],
        "ram_pattern":  [45, 46, 47, 45, 44, 46, 48, 47, 45, 44],
        "disk_pattern": [60, 60, 61, 61, 60, 60, 61, 61, 60, 60],
    },
}


def run_simulation(scenario_name: str) -> dict:
    if scenario_name not in SCENARIOS:
        return {"error": f"Unknown scenario. Available: {list(SCENARIOS.keys())}"}

    scenario = SCENARIOS[scenario_name]
    steps    = []
    alerts   = []

    for i in range(scenario["steps"]):
        cpu  = scenario["cpu_pattern"][i]
        ram  = scenario["ram_pattern"][i]
        disk = scenario["disk_pattern"][i]

        step_alerts = []
        if cpu > 80:
            step_alerts.append(f"⚠️ CPU critical: {cpu}%")
        if ram > 80:
            step_alerts.append(f"⚠️ RAM critical: {ram}%")
        if disk > 90:
            step_alerts.append(f"⚠️ Disk critical: {disk}%")

        alerts.extend(step_alerts)
        steps.append({
            "step":        i + 1,
            "cpu_usage":   cpu,
            "ram_usage":   ram,
            "disk_usage":  disk,
            "alerts":      step_alerts,
        })

    return {
        "scenario":    scenario_name,
        "description": scenario["description"],
        "timestamp":   datetime.now().isoformat(),
        "steps":       steps,
        "total_alerts": len(alerts),
        "summary": {
            "max_cpu":  max(scenario["cpu_pattern"]),
            "max_ram":  max(scenario["ram_pattern"]),
            "max_disk": max(scenario["disk_pattern"]),
            "avg_cpu":  round(np.mean(scenario["cpu_pattern"]), 2),
            "avg_ram":  round(np.mean(scenario["ram_pattern"]), 2),
        }
    }
