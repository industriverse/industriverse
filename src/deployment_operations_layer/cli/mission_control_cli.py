"""
Mission Control CLI for the Deployment Operations Layer.

This module provides a command-line interface for controlling deployment missions,
allowing operators to submit, monitor, and manage deployment operations.
"""

import os
import sys
import json
import logging
import argparse
import time
import uuid
import yaml
import tabulate
import colorama
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Initialize colorama
colorama.init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import mission execution engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from execution.mission_execution_engine import MissionExecutionEngine, MissionStatus

class MissionControlCLI:
    """
    Mission Control CLI for the Deployment Operations Layer.
    
    This class provides a command-line interface for controlling deployment missions,
    allowing operators to submit, monitor, and manage deployment operations.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Mission Control CLI.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize mission execution engine
        self.engine = MissionExecutionEngine(self.config.get("engine", {}))
        
        # Start engine if auto_start is enabled
        if self.config.get("auto_start", True):
            self.engine.start()
        
        # Set up color scheme
        self.colors = {
            "header": colorama.Fore.CYAN,
            "success": colorama.Fore.GREEN,
            "error": colorama.Fore.RED,
            "warning": colorama.Fore.YELLOW,
            "info": colorama.Fore.WHITE,
            "reset": colorama.Style.RESET_ALL
        }
        
        # Set up status colors
        self.status_colors = {
            MissionStatus.PENDING.value: colorama.Fore.BLUE,
            MissionStatus.PLANNING.value: colorama.Fore.CYAN,
            MissionStatus.SIMULATING.value: colorama.Fore.MAGENTA,
            MissionStatus.EXECUTING.value: colorama.Fore.YELLOW,
            MissionStatus.PAUSED.value: colorama.Fore.YELLOW,
            MissionStatus.SUCCEEDED.value: colorama.Fore.GREEN,
            MissionStatus.FAILED.value: colorama.Fore.RED,
            MissionStatus.CANCELED.value: colorama.Fore.RED,
            MissionStatus.ROLLING_BACK.value: colorama.Fore.MAGENTA,
            MissionStatus.ROLLED_BACK.value: colorama.Fore.BLUE
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict: Configuration dictionary
        """
        # Default configuration
        default_config = {
            "engine": {
                "max_concurrent_missions": 5,
                "simulation_required": True,
                "auto_rollback": True
            },
            "auto_start": True,
            "output_format": "table",
            "verbose": False
        }
        
        # If no config path provided, return default
        if not config_path:
            return default_config
        
        try:
            # Check if file exists
            if not os.path.exists(config_path):
                logger.warning(f"Configuration file not found: {config_path}")
                return default_config
            
            # Load configuration from file
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    config = json.load(f)
                elif config_path.endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f)
                else:
                    logger.warning(f"Unsupported configuration file format: {config_path}")
                    return default_config
            
            # Merge with default configuration
            merged_config = default_config.copy()
            self._deep_update(merged_config, config)
            
            return merged_config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return default_config
    
    def _deep_update(self, d: Dict, u: Dict) -> Dict:
        """
        Deep update dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with updates
            
        Returns:
            Dict: Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    def run(self) -> None:
        """
        Run the Mission Control CLI.
        """
        # Set up argument parser
        parser = argparse.ArgumentParser(
            description="Mission Control CLI for the Deployment Operations Layer",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start the mission execution engine
  mission-control start-engine
  
  # Submit a mission from a file
  mission-control submit -f mission.yaml
  
  # List all missions
  mission-control list
  
  # Get mission details
  mission-control get <mission_id>
  
  # Cancel a mission
  mission-control cancel <mission_id>
  
  # Rollback a mission
  mission-control rollback <mission_id>
  
  # Get engine status
  mission-control status
"""
        )
        
        # Add subparsers
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # Start engine command
        start_parser = subparsers.add_parser("start-engine", help="Start the mission execution engine")
        
        # Stop engine command
        stop_parser = subparsers.add_parser("stop-engine", help="Stop the mission execution engine")
        
        # Submit mission command
        submit_parser = subparsers.add_parser("submit", help="Submit a mission")
        submit_parser.add_argument("-f", "--file", help="Path to mission file (JSON or YAML)")
        submit_parser.add_argument("-p", "--priority", type=int, default=1, help="Mission priority (lower value = higher priority)")
        
        # List missions command
        list_parser = subparsers.add_parser("list", help="List missions")
        list_parser.add_argument("-s", "--status", help="Filter by status")
        list_parser.add_argument("-l", "--limit", type=int, default=10, help="Maximum number of missions to return")
        list_parser.add_argument("-o", "--offset", type=int, default=0, help="Offset for pagination")
        list_parser.add_argument("-f", "--format", choices=["table", "json", "yaml"], help="Output format")
        
        # Get mission command
        get_parser = subparsers.add_parser("get", help="Get mission details")
        get_parser.add_argument("mission_id", help="Mission ID")
        get_parser.add_argument("-f", "--format", choices=["table", "json", "yaml"], help="Output format")
        
        # Cancel mission command
        cancel_parser = subparsers.add_parser("cancel", help="Cancel a mission")
        cancel_parser.add_argument("mission_id", help="Mission ID")
        
        # Pause mission command
        pause_parser = subparsers.add_parser("pause", help="Pause a mission")
        pause_parser.add_argument("mission_id", help="Mission ID")
        
        # Resume mission command
        resume_parser = subparsers.add_parser("resume", help="Resume a paused mission")
        resume_parser.add_argument("mission_id", help="Mission ID")
        
        # Rollback mission command
        rollback_parser = subparsers.add_parser("rollback", help="Rollback a mission")
        rollback_parser.add_argument("mission_id", help="Mission ID")
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Get engine status")
        status_parser.add_argument("-f", "--format", choices=["table", "json", "yaml"], help="Output format")
        
        # Configure command
        configure_parser = subparsers.add_parser("configure", help="Configure the engine")
        configure_parser.add_argument("-f", "--file", help="Path to configuration file (JSON or YAML)")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Execute command
        if args.command == "start-engine":
            self._start_engine()
        elif args.command == "stop-engine":
            self._stop_engine()
        elif args.command == "submit":
            self._submit_mission(args)
        elif args.command == "list":
            self._list_missions(args)
        elif args.command == "get":
            self._get_mission(args)
        elif args.command == "cancel":
            self._cancel_mission(args)
        elif args.command == "pause":
            self._pause_mission(args)
        elif args.command == "resume":
            self._resume_mission(args)
        elif args.command == "rollback":
            self._rollback_mission(args)
        elif args.command == "status":
            self._get_status(args)
        elif args.command == "configure":
            self._configure_engine(args)
        else:
            parser.print_help()
    
    def _start_engine(self) -> None:
        """
        Start the mission execution engine.
        """
        print(f"{self.colors['header']}Starting mission execution engine...{self.colors['reset']}")
        
        result = self.engine.start()
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Engine started successfully{self.colors['reset']}")
            print(f"Engine ID: {result.get('engine_id')}")
            print(f"Worker count: {result.get('worker_count')}")
        else:
            print(f"{self.colors['error']}Error starting engine: {result.get('message')}{self.colors['reset']}")
    
    def _stop_engine(self) -> None:
        """
        Stop the mission execution engine.
        """
        print(f"{self.colors['header']}Stopping mission execution engine...{self.colors['reset']}")
        
        result = self.engine.stop()
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Engine stopped successfully{self.colors['reset']}")
        else:
            print(f"{self.colors['error']}Error stopping engine: {result.get('message')}{self.colors['reset']}")
    
    def _submit_mission(self, args) -> None:
        """
        Submit a mission.
        
        Args:
            args: Command-line arguments
        """
        # Check if file is provided
        if not args.file:
            print(f"{self.colors['error']}Error: Mission file is required{self.colors['reset']}")
            return
        
        # Check if file exists
        if not os.path.exists(args.file):
            print(f"{self.colors['error']}Error: Mission file not found: {args.file}{self.colors['reset']}")
            return
        
        try:
            # Load mission from file
            with open(args.file, 'r') as f:
                if args.file.endswith('.json'):
                    mission = json.load(f)
                elif args.file.endswith(('.yaml', '.yml')):
                    mission = yaml.safe_load(f)
                else:
                    print(f"{self.colors['error']}Error: Unsupported file format: {args.file}{self.colors['reset']}")
                    return
            
            print(f"{self.colors['header']}Submitting mission...{self.colors['reset']}")
            
            # Submit mission
            result = self.engine.submit_mission(mission, args.priority)
            
            if result.get("status") == "success":
                print(f"{self.colors['success']}Mission submitted successfully{self.colors['reset']}")
                print(f"Mission ID: {result.get('mission_id')}")
                print(f"Priority: {result.get('priority')}")
            else:
                print(f"{self.colors['error']}Error submitting mission: {result.get('message')}{self.colors['reset']}")
        except Exception as e:
            print(f"{self.colors['error']}Error: {str(e)}{self.colors['reset']}")
    
    def _list_missions(self, args) -> None:
        """
        List missions.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Listing missions...{self.colors['reset']}")
        
        # Get output format
        output_format = args.format or self.config.get("output_format", "table")
        
        # List missions
        result = self.engine.list_missions(args.status, args.limit, args.offset)
        
        if result.get("status") == "success":
            missions = result.get("missions", [])
            
            if not missions:
                print(f"{self.colors['info']}No missions found{self.colors['reset']}")
                return
            
            # Output based on format
            if output_format == "json":
                print(json.dumps(missions, indent=2))
            elif output_format == "yaml":
                print(yaml.dump(missions, default_flow_style=False))
            else:  # table format
                # Prepare table data
                headers = ["Mission ID", "Type", "Status", "Timestamp", "Priority"]
                rows = []
                
                for mission in missions:
                    mission_id = mission.get("mission_id", "")
                    mission_type = mission.get("type", "generic")
                    status = mission.get("status", "")
                    timestamp = mission.get("timestamp", "")
                    priority = mission.get("priority", "")
                    
                    # Add color to status
                    status_color = self.status_colors.get(status, self.colors["info"])
                    colored_status = f"{status_color}{status}{self.colors['reset']}"
                    
                    rows.append([mission_id, mission_type, colored_status, timestamp, priority])
                
                # Print table
                print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))
                
                # Print summary
                print(f"\nTotal missions: {result.get('total_missions')}")
                print(f"Showing {len(missions)} of {result.get('total_missions')} missions")
        else:
            print(f"{self.colors['error']}Error listing missions: {result.get('message')}{self.colors['reset']}")
    
    def _get_mission(self, args) -> None:
        """
        Get mission details.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Getting mission details...{self.colors['reset']}")
        
        # Get output format
        output_format = args.format or self.config.get("output_format", "table")
        
        # Get mission
        result = self.engine.get_mission(args.mission_id)
        
        if result.get("status") == "success":
            mission = result.get("mission", {})
            
            # Output based on format
            if output_format == "json":
                print(json.dumps(mission, indent=2))
            elif output_format == "yaml":
                print(yaml.dump(mission, default_flow_style=False))
            else:  # table format
                # Print mission details
                print(f"Mission ID: {mission.get('mission_id')}")
                
                status = mission.get("status", "")
                status_color = self.status_colors.get(status, self.colors["info"])
                print(f"Status: {status_color}{status}{self.colors['reset']}")
                
                print(f"Type: {mission.get('type', 'generic')}")
                print(f"Priority: {mission.get('priority', '')}")
                print(f"Timestamp: {mission.get('timestamp', '')}")
                
                # Print timestamps
                if "planning_started_at" in mission:
                    print(f"Planning started: {mission.get('planning_started_at')}")
                
                if "planning_completed_at" in mission:
                    print(f"Planning completed: {mission.get('planning_completed_at')}")
                
                if "simulation_started_at" in mission:
                    print(f"Simulation started: {mission.get('simulation_started_at')}")
                
                if "simulation_completed_at" in mission:
                    print(f"Simulation completed: {mission.get('simulation_completed_at')}")
                
                if "execution_started_at" in mission:
                    print(f"Execution started: {mission.get('execution_started_at')}")
                
                if "execution_completed_at" in mission:
                    print(f"Execution completed: {mission.get('execution_completed_at')}")
                
                if "succeeded_at" in mission:
                    print(f"Succeeded at: {mission.get('succeeded_at')}")
                
                if "failed_at" in mission:
                    print(f"Failed at: {mission.get('failed_at')}")
                    print(f"Error: {mission.get('error', 'Unknown error')}")
                
                if "canceled_at" in mission:
                    print(f"Canceled at: {mission.get('canceled_at')}")
                
                if "paused_at" in mission:
                    print(f"Paused at: {mission.get('paused_at')}")
                
                if "resumed_at" in mission:
                    print(f"Resumed at: {mission.get('resumed_at')}")
                
                if "rollback_started_at" in mission:
                    print(f"Rollback started: {mission.get('rollback_started_at')}")
                
                if "rollback_completed_at" in mission:
                    print(f"Rollback completed: {mission.get('rollback_completed_at')}")
                
                if "rollback_failed_at" in mission:
                    print(f"Rollback failed: {mission.get('rollback_failed_at')}")
                    print(f"Rollback error: {mission.get('rollback_error', 'Unknown error')}")
                
                # Print plan summary if available
                if "plan_summary" in mission:
                    print("\nPlan Summary:")
                    print(mission.get("plan_summary"))
                
                # Print simulation summary if available
                if "simulation_summary" in mission:
                    print("\nSimulation Summary:")
                    print(mission.get("simulation_summary"))
                
                # Print execution summary if available
                if "execution_summary" in mission:
                    print("\nExecution Summary:")
                    print(mission.get("execution_summary"))
        else:
            print(f"{self.colors['error']}Error getting mission: {result.get('message')}{self.colors['reset']}")
    
    def _cancel_mission(self, args) -> None:
        """
        Cancel a mission.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Canceling mission...{self.colors['reset']}")
        
        # Cancel mission
        result = self.engine.cancel_mission(args.mission_id)
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Mission canceled successfully{self.colors['reset']}")
            print(f"Mission ID: {result.get('mission_id')}")
            print(f"Previous status: {result.get('previous_status')}")
        else:
            print(f"{self.colors['error']}Error canceling mission: {result.get('message')}{self.colors['reset']}")
    
    def _pause_mission(self, args) -> None:
        """
        Pause a mission.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Pausing mission...{self.colors['reset']}")
        
        # Pause mission
        result = self.engine.pause_mission(args.mission_id)
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Mission paused successfully{self.colors['reset']}")
            print(f"Mission ID: {result.get('mission_id')}")
            print(f"Previous status: {result.get('previous_status')}")
        else:
            print(f"{self.colors['error']}Error pausing mission: {result.get('message')}{self.colors['reset']}")
    
    def _resume_mission(self, args) -> None:
        """
        Resume a paused mission.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Resuming mission...{self.colors['reset']}")
        
        # Resume mission
        result = self.engine.resume_mission(args.mission_id)
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Mission resumed successfully{self.colors['reset']}")
            print(f"Mission ID: {result.get('mission_id')}")
            print(f"Resumed status: {result.get('resumed_status')}")
        else:
            print(f"{self.colors['error']}Error resuming mission: {result.get('message')}{self.colors['reset']}")
    
    def _rollback_mission(self, args) -> None:
        """
        Rollback a mission.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Rolling back mission...{self.colors['reset']}")
        
        # Rollback mission
        result = self.engine.rollback_mission(args.mission_id)
        
        if result.get("status") == "success":
            print(f"{self.colors['success']}Mission rolled back successfully{self.colors['reset']}")
            print(f"Mission ID: {result.get('mission_id')}")
        else:
            print(f"{self.colors['error']}Error rolling back mission: {result.get('message')}{self.colors['reset']}")
    
    def _get_status(self, args) -> None:
        """
        Get engine status.
        
        Args:
            args: Command-line arguments
        """
        print(f"{self.colors['header']}Getting engine status...{self.colors['reset']}")
        
        # Get output format
        output_format = args.format or self.config.get("output_format", "table")
        
        # Get status
        result = self.engine.get_engine_status()
        
        if result.get("status") == "success":
            status = {
                "engine_id": result.get("engine_id"),
                "is_running": result.get("is_running"),
                "queue_size": result.get("queue_size"),
                "active_mission_count": result.get("active_mission_count"),
                "worker_count": result.get("worker_count"),
                "active_worker_count": result.get("active_worker_count"),
                "max_concurrent_missions": result.get("max_concurrent_missions"),
                "simulation_required": result.get("simulation_required"),
                "auto_rollback": result.get("auto_rollback")
            }
            
            # Output based on format
            if output_format == "json":
                print(json.dumps(status, indent=2))
            elif output_format == "yaml":
                print(yaml.dump(status, default_flow_style=False))
            else:  # table format
                # Print status
                print(f"Engine ID: {status['engine_id']}")
                
                is_running = status["is_running"]
                running_color = self.colors["success"] if is_running else self.colors["error"]
                print(f"Running: {running_color}{is_running}{self.colors['reset']}")
                
                print(f"Queue size: {status['queue_size']}")
                print(f"Active missions: {status['active_mission_count']}")
                print(f"Worker count: {status['worker_count']}")
                print(f"Active workers: {status['active_worker_count']}")
                print(f"Max concurrent missions: {status['max_concurrent_missions']}")
                print(f"Simulation required: {status['simulation_required']}")
                print(f"Auto rollback: {status['auto_rollback']}")
        else:
            print(f"{self.colors['error']}Error getting engine status: {result.get('message')}{self.colors['reset']}")
    
    def _configure_engine(self, args) -> None:
        """
        Configure the engine.
        
        Args:
            args: Command-line arguments
        """
        # Check if file is provided
        if not args.file:
            print(f"{self.colors['error']}Error: Configuration file is required{self.colors['reset']}")
            return
        
        # Check if file exists
        if not os.path.exists(args.file):
            print(f"{self.colors['error']}Error: Configuration file not found: {args.file}{self.colors['reset']}")
            return
        
        try:
            # Load configuration from file
            with open(args.file, 'r') as f:
                if args.file.endswith('.json'):
                    config = json.load(f)
                elif args.file.endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f)
                else:
                    print(f"{self.colors['error']}Error: Unsupported file format: {args.file}{self.colors['reset']}")
                    return
            
            print(f"{self.colors['header']}Configuring engine...{self.colors['reset']}")
            
            # Configure engine
            result = self.engine.configure(config)
            
            if result.get("status") == "success":
                print(f"{self.colors['success']}Engine configured successfully{self.colors['reset']}")
                print(f"Engine ID: {result.get('engine_id')}")
                print(f"Max concurrent missions: {result.get('max_concurrent_missions')}")
                print(f"Simulation required: {result.get('simulation_required')}")
                print(f"Auto rollback: {result.get('auto_rollback')}")
            else:
                print(f"{self.colors['error']}Error configuring engine: {result.get('message')}{self.colors['reset']}")
        except Exception as e:
            print(f"{self.colors['error']}Error: {str(e)}{self.colors['reset']}")

def main():
    """
    Main entry point.
    """
    # Get configuration path from environment variable
    config_path = os.environ.get("MISSION_CONTROL_CONFIG")
    
    # Initialize CLI
    cli = MissionControlCLI(config_path)
    
    # Run CLI
    cli.run()

if __name__ == "__main__":
    main()
