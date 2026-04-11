"""
Quantum-Ready Optimization Module
Uses Qiskit to build a quantum circuit that encodes system health
and applies quantum optimization logic.

This is a real quantum circuit — can run on IBM Quantum hardware
by connecting to IBM Quantum account.
"""
from datetime import datetime

try:
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


def _normalize(value: float, max_val: float = 100.0) -> float:
    """Normalize a metric value to 0-1 range."""
    return min(1.0, max(0.0, value / max_val))


def quantum_optimize(cpu: float, ram: float, disk: float) -> dict:
    """
    Encode system metrics into a quantum circuit.
    Uses rotation gates to represent metric severity.
    Measures qubit states to determine optimization priority.
    """
    if not QISKIT_AVAILABLE:
        return {
            "quantum_available": False,
            "message": "Qiskit not installed. Run: pip install qiskit",
            "classical_fallback": _classical_optimize(cpu, ram, disk)
        }

    import math

    # 3 qubits — one per metric (CPU, RAM, Disk)
    qc = QuantumCircuit(3, 3)

    # Encode metrics as rotation angles (Ry gate)
    # Higher metric value = larger rotation = more likely to measure |1>
    cpu_angle  = _normalize(cpu)  * math.pi
    ram_angle  = _normalize(ram)  * math.pi
    disk_angle = _normalize(disk) * math.pi

    qc.ry(cpu_angle,  0)  # qubit 0 = CPU
    qc.ry(ram_angle,  1)  # qubit 1 = RAM
    qc.ry(disk_angle, 2)  # qubit 2 = Disk

    # Entangle qubits to model resource interdependencies
    qc.cx(0, 1)  # CPU affects RAM
    qc.cx(1, 2)  # RAM affects Disk

    # Measure all qubits
    qc.measure([0, 1, 2], [0, 1, 2])

    # Run on statevector sampler (local simulation)
    sampler = StatevectorSampler()
    job     = sampler.run([qc], shots=512)
    result  = job.result()
    counts  = result[0].data.c.get_counts()

    # Interpret results
    priority = _interpret_counts(counts, cpu, ram, disk)

    return {
        "quantum_available": True,
        "timestamp":         datetime.now().isoformat(),
        "inputs": {
            "cpu_usage":  cpu,
            "ram_usage":  ram,
            "disk_usage": disk,
        },
        "circuit": {
            "qubits":      3,
            "gates":       ["Ry(cpu)", "Ry(ram)", "Ry(disk)", "CX(0,1)", "CX(1,2)"],
            "shots":       512,
            "top_counts":  dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:4]),
        },
        "optimization_priority": priority,
    }


def _interpret_counts(counts: dict, cpu: float, ram: float, disk: float) -> list:
    """Map quantum measurement results to optimization priorities."""
    priorities = []
    total = sum(counts.values())

    # Probability of each qubit being |1> (critical)
    cpu_prob  = sum(v for k, v in counts.items() if k[-1] == "1") / total
    ram_prob  = sum(v for k, v in counts.items() if len(k) > 1 and k[-2] == "1") / total
    disk_prob = sum(v for k, v in counts.items() if len(k) > 2 and k[-3] == "1") / total

    metrics = [
        ("cpu_usage",  cpu,  cpu_prob),
        ("ram_usage",  ram,  ram_prob),
        ("disk_usage", disk, disk_prob),
    ]

    for metric, value, prob in sorted(metrics, key=lambda x: x[2], reverse=True):
        priorities.append({
            "metric":           metric,
            "current_value":    value,
            "quantum_priority": round(prob, 3),
            "action_needed":    prob > 0.5,
        })

    return priorities


def _classical_fallback(cpu: float, ram: float, disk: float) -> dict:
    """Simple classical fallback when Qiskit is not available."""
    metrics = [
        ("cpu_usage",  cpu),
        ("ram_usage",  ram),
        ("disk_usage", disk),
    ]
    return {
        "priority": [
            {"metric": m, "value": v, "priority_score": round(v / 100, 3)}
            for m, v in sorted(metrics, key=lambda x: x[1], reverse=True)
        ]
    }
