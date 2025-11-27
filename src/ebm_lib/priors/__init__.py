from ebm_lib.registry import register

DOMAINS = [
    "fusion", "grid", "wafer", "apparel", "battery",
    "motor", "magnet", "cnc", "chassis", "microgrid",
    "casting", "heat", "chem", "polymer", "metal",
    "pipeline", "qctherm", "failure",
    "robotics", "matflow", "workforce", "schedule",
    "amrsafety", "conveyor", "assembly",
    "electronics", "pcbmfg", "sensorint",
    "surface", "lifecycle",
]

for d in DOMAINS:
    register(f"{d}_v1", f"ebm_lib.priors.{d}_v1")
