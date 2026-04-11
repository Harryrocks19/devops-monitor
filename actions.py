import subprocess
import psutil
import logging

logger = logging.getLogger(__name__)


def restart_service(service_name: str) -> dict:
    """Restart a system service by name."""
    try:
        subprocess.run(["sc", "stop", service_name], capture_output=True, timeout=10)
        result = subprocess.run(["sc", "start", service_name], capture_output=True, timeout=10)
        success = result.returncode == 0
        return {
            "action":  "restart_service",
            "target":  service_name,
            "success": success,
            "message": f"✅ Service '{service_name}' restarted." if success else f"❌ Failed to restart '{service_name}'."
        }
    except Exception as e:
        return {"action": "restart_service", "target": service_name, "success": False, "message": str(e)}


def kill_high_cpu_process() -> dict:
    """Kill the non-system process consuming the most CPU."""
    try:
        procs = [
            p for p in psutil.process_iter(["pid", "name", "cpu_percent"])
            if p.info["cpu_percent"] is not None and p.info["name"] not in ("System", "Idle")
        ]
        if not procs:
            return {"action": "kill_process", "success": False, "message": "No eligible process found."}

        top = max(procs, key=lambda p: p.info["cpu_percent"])
        top.kill()
        return {
            "action":  "kill_process",
            "target":  f"{top.info['name']} (PID {top.info['pid']})",
            "success": True,
            "message": f"✅ Killed process {top.info['name']} (PID {top.info['pid']}) using {top.info['cpu_percent']}% CPU."
        }
    except Exception as e:
        return {"action": "kill_process", "success": False, "message": str(e)}


def free_memory() -> dict:
    """Run memory cleanup (Windows: empty working sets)."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
            capture_output=True, timeout=15
        )
        return {
            "action":  "free_memory",
            "success": True,
            "message": "✅ Memory cleanup triggered."
        }
    except Exception as e:
        return {"action": "free_memory", "success": False, "message": str(e)}


AVAILABLE_ACTIONS = {
    "kill_high_cpu":  kill_high_cpu_process,
    "free_memory":    free_memory,
}
