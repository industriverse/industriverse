import argparse
import json
import os
import sys
import time
import subprocess
import signal

# Paths
CONTROL_DIR = "data/datahub"
HEARTBEAT_FILE = os.path.join(CONTROL_DIR, "heartbeat.json")
CONTROL_FILE = os.path.join(CONTROL_DIR, "control.json")
DAEMON_SCRIPT = "src/datahub/collector_daemon.py"
LOG_FILE = "data/datahub/collector.log"

def get_status():
    if not os.path.exists(HEARTBEAT_FILE):
        return "STOPPED", None
    
    try:
        with open(HEARTBEAT_FILE, 'r') as f:
            data = json.load(f)
        
        # Check if process is actually alive
        pid = data.get("pid")
        try:
            os.kill(pid, 0) # Check if PID exists
            # Check for staleness (heartbeat older than 5s)
            if time.time() - data.get("timestamp", 0) > 5:
                return "STALE", data
            return data.get("status", "UNKNOWN"), data
        except OSError:
            return "CRASHED", data
            
    except Exception:
        return "ERROR", None

def send_command(cmd, payload=None):
    command_data = {"command": cmd, "payload": payload or {}}
    with open(CONTROL_FILE, 'w') as f:
        json.dump(command_data, f)
    print(f"Sent command: {cmd}")

def start_daemon():
    status, _ = get_status()
    if status in ["RUNNING", "PAUSED"]:
        print("Daemon is already running.")
        return

    print("Starting Data Hub Collector Daemon...")
    os.makedirs(CONTROL_DIR, exist_ok=True)
    
    # Run in background
    with open(LOG_FILE, "a") as log:
        subprocess.Popen(
            ["python3", DAEMON_SCRIPT],
            stdout=log,
            stderr=log,
            preexec_fn=os.setpgrp # Detach from terminal
        )
    
    # Wait for heartbeat
    for _ in range(10):
        time.sleep(0.5)
        s, _ = get_status()
        if s == "RUNNING":
            print("✅ Daemon Started Successfully.")
            return
    print("❌ Daemon failed to start (check logs).")

def stop_daemon():
    status, data = get_status()
    if status == "STOPPED":
        print("Daemon is already stopped.")
        return

    print("Stopping Daemon...")
    send_command("STOP")
    
    # Wait for shutdown
    for _ in range(10):
        time.sleep(0.5)
        s, _ = get_status()
        if s == "STOPPED":
            print("✅ Daemon Stopped.")
            return
            
    # Force Kill if needed
    if data and "pid" in data:
        print("⚠️ Force killing process...")
        try:
            os.kill(data["pid"], signal.SIGKILL)
            if os.path.exists(HEARTBEAT_FILE):
                os.remove(HEARTBEAT_FILE)
            print("💀 Daemon Killed.")
        except:
            pass

def show_status():
    status, data = get_status()
    print(f"Status: {status}")
    if data:
        print(f"PID: {data.get('pid')}")
        print(f"Shards Collected: {data.get('shards_collected')}")
        print(f"Last Heartbeat: {time.time() - data.get('timestamp', 0):.1f}s ago")
        print(f"Config: {json.dumps(data.get('config'), indent=2)}")

def main():
    parser = argparse.ArgumentParser(description="Industriverse Data Hub Controller")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    subparsers.add_parser("start", help="Start the daemon")
    subparsers.add_parser("stop", help="Stop the daemon")
    subparsers.add_parser("status", help="Show daemon status")
    subparsers.add_parser("pause", help="Pause collection")
    subparsers.add_parser("resume", help="Resume collection")
    
    config_parser = subparsers.add_parser("config", help="Update configuration")
    config_parser.add_argument("key", help="Config key")
    config_parser.add_argument("value", help="Config value")

    args = parser.parse_args()

    if args.action == "start":
        start_daemon()
    elif args.action == "stop":
        stop_daemon()
    elif args.action == "status":
        show_status()
    elif args.action == "pause":
        send_command("PAUSE")
    elif args.action == "resume":
        send_command("RESUME")
    elif args.action == "config":
        # Try to parse value as number if possible
        val = args.value
        try:
            if "." in val:
                val = float(val)
            else:
                val = int(val)
        except:
            pass
        send_command("UPDATE_CONFIG", {args.key: val})
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
