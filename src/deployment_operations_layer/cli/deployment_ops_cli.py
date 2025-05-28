"""
Deployment Operations Layer Command Line Interface

This module provides a comprehensive CLI for controlling and monitoring
deployment operations across the Industriverse ecosystem.
"""

import os
import sys
import json
import logging
import argparse
import datetime
import time
import uuid
import textwrap
import tabulate
import colorama
from typing import Dict, List, Optional, Any, Union

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deployment_ops_cli')

# Import execution engine components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from execution.execution_engine import (
    ExecutionEngine, Mission, MissionStatus, MissionType,
    create_execution_engine
)

# Import other required components
from agent.mission_planner import MissionPlanner
from agent.mission_executor import MissionExecutor
from agent.error_handler import ErrorHandler
from agent.recovery_manager import RecoveryManager
from simulation.simulation_engine import SimulationEngine
from integration.layer_integration_manager import LayerIntegrationManager
from integration.cross_layer_integration_manager import CrossLayerIntegrationManager
from templates.template_registry import TemplateRegistry

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DeploymentOpsCLI:
    """
    Command Line Interface for the Deployment Operations Layer.
    """
    def __init__(self):
        self.execution_engine = None
        self.layer_integration_manager = None
        self.cross_layer_integration_manager = None
        self.template_registry = None
        
        # Initialize components
        self._initialize_components()
        
        # Create parser
        self.parser = self._create_parser()
    
    def _initialize_components(self):
        """Initialize all required components"""
        # Initialize components
        mission_planner = MissionPlanner()
        simulation_engine = SimulationEngine()
        mission_executor = MissionExecutor()
        error_handler = ErrorHandler()
        recovery_manager = RecoveryManager()
        
        # Create execution engine
        self.execution_engine = create_execution_engine(
            mission_planner,
            simulation_engine,
            mission_executor,
            error_handler,
            recovery_manager,
            worker_count=5
        )
        
        # Initialize other components
        self.layer_integration_manager = LayerIntegrationManager()
        self.cross_layer_integration_manager = CrossLayerIntegrationManager()
        self.template_registry = TemplateRegistry()
    
    def _create_parser(self):
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='Deployment Operations Layer CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent('''
                Examples:
                  deployment_ops_cli start                     # Start the execution engine
                  deployment_ops_cli status                    # Show engine status
                  deployment_ops_cli missions list             # List all missions
                  deployment_ops_cli missions get <mission_id> # Get mission details
                  deployment_ops_cli missions create           # Create a new mission (interactive)
                  deployment_ops_cli layers list               # List all layers
                  deployment_ops_cli capsules list             # List all capsules
                  deployment_ops_cli templates list            # List all templates
            ''')
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Engine commands
        parser_start = subparsers.add_parser('start', help='Start the execution engine')
        parser_stop = subparsers.add_parser('stop', help='Stop the execution engine')
        parser_status = subparsers.add_parser('status', help='Show engine status')
        
        # Mission commands
        parser_missions = subparsers.add_parser('missions', help='Mission management')
        mission_subparsers = parser_missions.add_subparsers(dest='subcommand', help='Mission subcommand')
        
        # Mission list
        parser_missions_list = mission_subparsers.add_parser('list', help='List missions')
        parser_missions_list.add_argument('--status', help='Filter by status')
        parser_missions_list.add_argument('--limit', type=int, default=10, help='Number of missions to show')
        parser_missions_list.add_argument('--offset', type=int, default=0, help='Offset for pagination')
        
        # Mission get
        parser_missions_get = mission_subparsers.add_parser('get', help='Get mission details')
        parser_missions_get.add_argument('mission_id', help='Mission ID')
        
        # Mission create
        parser_missions_create = mission_subparsers.add_parser('create', help='Create a new mission')
        parser_missions_create.add_argument('--type', help='Mission type')
        parser_missions_create.add_argument('--priority', type=int, help='Mission priority (1-10, 1 being highest)')
        parser_missions_create.add_argument('--layers', help='Target layers (comma-separated)')
        parser_missions_create.add_argument('--config', help='Configuration JSON file')
        parser_missions_create.add_argument('--description', help='Mission description')
        parser_missions_create.add_argument('--no-simulation', action='store_true', help='Skip simulation')
        parser_missions_create.add_argument('--no-rollback', action='store_true', help='Disable automatic rollback')
        parser_missions_create.add_argument('--timeout', type=int, help='Timeout in seconds')
        parser_missions_create.add_argument('--template', help='Use template')
        
        # Mission cancel
        parser_missions_cancel = mission_subparsers.add_parser('cancel', help='Cancel a mission')
        parser_missions_cancel.add_argument('mission_id', help='Mission ID')
        
        # Mission pause
        parser_missions_pause = mission_subparsers.add_parser('pause', help='Pause a mission')
        parser_missions_pause.add_argument('mission_id', help='Mission ID')
        
        # Mission resume
        parser_missions_resume = mission_subparsers.add_parser('resume', help='Resume a paused mission')
        parser_missions_resume.add_argument('mission_id', help='Mission ID')
        
        # Mission rollback
        parser_missions_rollback = mission_subparsers.add_parser('rollback', help='Rollback a mission')
        parser_missions_rollback.add_argument('mission_id', help='Mission ID')
        
        # Layer commands
        parser_layers = subparsers.add_parser('layers', help='Layer management')
        layer_subparsers = parser_layers.add_subparsers(dest='subcommand', help='Layer subcommand')
        
        # Layer list
        parser_layers_list = layer_subparsers.add_parser('list', help='List layers')
        
        # Layer get
        parser_layers_get = layer_subparsers.add_parser('get', help='Get layer details')
        parser_layers_get.add_argument('layer_id', help='Layer ID')
        
        # Layer capsules
        parser_layers_capsules = layer_subparsers.add_parser('capsules', help='List capsules for a layer')
        parser_layers_capsules.add_argument('layer_id', help='Layer ID')
        
        # Capsule commands
        parser_capsules = subparsers.add_parser('capsules', help='Capsule management')
        capsule_subparsers = parser_capsules.add_subparsers(dest='subcommand', help='Capsule subcommand')
        
        # Capsule list
        parser_capsules_list = capsule_subparsers.add_parser('list', help='List capsules')
        parser_capsules_list.add_argument('--layer', help='Filter by layer')
        parser_capsules_list.add_argument('--status', help='Filter by status')
        
        # Capsule get
        parser_capsules_get = capsule_subparsers.add_parser('get', help='Get capsule details')
        parser_capsules_get.add_argument('capsule_id', help='Capsule ID')
        
        # Template commands
        parser_templates = subparsers.add_parser('templates', help='Template management')
        template_subparsers = parser_templates.add_subparsers(dest='subcommand', help='Template subcommand')
        
        # Template list
        parser_templates_list = template_subparsers.add_parser('list', help='List templates')
        
        # Template get
        parser_templates_get = template_subparsers.add_parser('get', help='Get template details')
        parser_templates_get.add_argument('template_id', help='Template ID')
        
        return parser
    
    def run(self, args=None):
        """Run the CLI with the given arguments"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return
        
        # Start the execution engine if needed
        if args.command != 'start' and not self.execution_engine.running:
            print(f"{Colors.YELLOW}Starting execution engine...{Colors.ENDC}")
            self.execution_engine.start()
        
        # Handle commands
        if args.command == 'start':
            self._handle_start()
        elif args.command == 'stop':
            self._handle_stop()
        elif args.command == 'status':
            self._handle_status()
        elif args.command == 'missions':
            self._handle_missions(args)
        elif args.command == 'layers':
            self._handle_layers(args)
        elif args.command == 'capsules':
            self._handle_capsules(args)
        elif args.command == 'templates':
            self._handle_templates(args)
    
    def _handle_start(self):
        """Handle start command"""
        if self.execution_engine.running:
            print(f"{Colors.YELLOW}Execution engine is already running{Colors.ENDC}")
            return
        
        print(f"{Colors.GREEN}Starting execution engine...{Colors.ENDC}")
        self.execution_engine.start()
        print(f"{Colors.GREEN}Execution engine started{Colors.ENDC}")
    
    def _handle_stop(self):
        """Handle stop command"""
        if not self.execution_engine.running:
            print(f"{Colors.YELLOW}Execution engine is not running{Colors.ENDC}")
            return
        
        print(f"{Colors.YELLOW}Stopping execution engine...{Colors.ENDC}")
        self.execution_engine.stop()
        print(f"{Colors.GREEN}Execution engine stopped{Colors.ENDC}")
    
    def _handle_status(self):
        """Handle status command"""
        status = self.execution_engine.get_status()
        
        print(f"{Colors.HEADER}{Colors.BOLD}Execution Engine Status{Colors.ENDC}")
        print(f"Running: {Colors.GREEN if status['is_running'] else Colors.RED}{status['is_running']}{Colors.ENDC}")
        print(f"Queue Size: {status['queue_size']}")
        print(f"Active Missions: {status['active_mission_count']}")
        print(f"Workers: {status['active_worker_count']}/{status['worker_count']}")
        
        if status['uptime_seconds'] is not None:
            uptime = datetime.timedelta(seconds=status['uptime_seconds'])
            print(f"Uptime: {uptime}")
        
        print(f"Version: {status['version']}")
    
    def _handle_missions(self, args):
        """Handle missions command"""
        if not args.subcommand:
            print("Missing subcommand. Use 'missions list', 'missions get', etc.")
            return
        
        if args.subcommand == 'list':
            self._handle_missions_list(args)
        elif args.subcommand == 'get':
            self._handle_missions_get(args)
        elif args.subcommand == 'create':
            self._handle_missions_create(args)
        elif args.subcommand == 'cancel':
            self._handle_missions_cancel(args)
        elif args.subcommand == 'pause':
            self._handle_missions_pause(args)
        elif args.subcommand == 'resume':
            self._handle_missions_resume(args)
        elif args.subcommand == 'rollback':
            self._handle_missions_rollback(args)
    
    def _handle_missions_list(self, args):
        """Handle missions list command"""
        missions, total = self.execution_engine.get_missions(args.status, args.limit, args.offset)
        
        if not missions:
            print(f"{Colors.YELLOW}No missions found{Colors.ENDC}")
            return
        
        # Prepare table data
        headers = ["ID", "Type", "Status", "Priority", "Target Layers", "Timestamp"]
        table_data = []
        
        for mission in missions:
            # Format target layers
            target_layers = ", ".join(mission["target_layers"])
            if len(target_layers) > 30:
                target_layers = target_layers[:27] + "..."
            
            # Format timestamp
            timestamp = datetime.datetime.fromisoformat(mission["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            
            # Add row
            table_data.append([
                mission["mission_id"],
                mission["type"],
                self._colorize_status(mission["status"]),
                mission["priority"],
                target_layers,
                timestamp
            ])
        
        # Print table
        print(f"{Colors.HEADER}{Colors.BOLD}Missions ({len(missions)}/{total}){Colors.ENDC}")
        print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Print pagination info
        if total > args.limit:
            print(f"Showing {args.offset+1}-{min(args.offset+args.limit, total)} of {total} missions")
            
            if args.offset > 0:
                prev_offset = max(0, args.offset - args.limit)
                print(f"Previous page: deployment_ops_cli missions list --limit {args.limit} --offset {prev_offset}")
            
            if args.offset + args.limit < total:
                next_offset = args.offset + args.limit
                print(f"Next page: deployment_ops_cli missions list --limit {args.limit} --offset {next_offset}")
    
    def _handle_missions_get(self, args):
        """Handle missions get command"""
        mission = self.execution_engine.get_mission(args.mission_id)
        
        if not mission:
            print(f"{Colors.RED}Mission {args.mission_id} not found{Colors.ENDC}")
            return
        
        # Print mission details
        print(f"{Colors.HEADER}{Colors.BOLD}Mission Details{Colors.ENDC}")
        print(f"ID: {mission['mission_id']}")
        print(f"Type: {mission['type']}")
        print(f"Status: {self._colorize_status(mission['status'])}")
        print(f"Priority: {mission['priority']}")
        print(f"Description: {mission['description'] or 'N/A'}")
        print(f"Target Layers: {', '.join(mission['target_layers'])}")
        print(f"Timestamp: {datetime.datetime.fromisoformat(mission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print timeline
        print(f"\n{Colors.HEADER}{Colors.BOLD}Timeline{Colors.ENDC}")
        for event in mission['timeline']:
            timestamp = datetime.datetime.fromisoformat(event['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            status_color = Colors.BLUE
            if event['status'] == 'success':
                status_color = Colors.GREEN
            elif event['status'] == 'error':
                status_color = Colors.RED
            elif event['status'] == 'warning':
                status_color = Colors.YELLOW
            
            print(f"{timestamp} - {status_color}{event['event']}{Colors.ENDC}: {event['details']}")
        
        # Print capsules
        if mission['capsules']:
            print(f"\n{Colors.HEADER}{Colors.BOLD}Capsules{Colors.ENDC}")
            headers = ["ID", "Name", "Type", "Layer", "Status"]
            table_data = []
            
            for capsule in mission['capsules']:
                table_data.append([
                    capsule['id'],
                    capsule['name'],
                    capsule['type'],
                    capsule['layer'],
                    self._colorize_status(capsule['status'])
                ])
            
            print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _handle_missions_create(self, args):
        """Handle missions create command"""
        # Interactive mode if no arguments provided
        if not (args.type or args.config or args.template):
            return self._interactive_mission_create()
        
        # Get mission type
        mission_type = args.type
        if not mission_type:
            valid_types = [
                MissionType.DEPLOY, MissionType.UPDATE, MissionType.ROLLBACK,
                MissionType.SCALE, MissionType.MIGRATE, MissionType.BACKUP,
                MissionType.RESTORE, MissionType.HEALTH_CHECK, MissionType.SECURITY_SCAN,
                MissionType.COMPLIANCE_CHECK
            ]
            print(f"{Colors.YELLOW}Missing mission type. Valid types: {', '.join(valid_types)}{Colors.ENDC}")
            return
        
        # Get target layers
        target_layers = []
        if args.layers:
            target_layers = [layer.strip() for layer in args.layers.split(',')]
        
        if not target_layers:
            print(f"{Colors.YELLOW}Missing target layers{Colors.ENDC}")
            return
        
        # Get configuration
        configuration = {}
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    configuration = json.load(f)
            except Exception as e:
                print(f"{Colors.RED}Error loading configuration file: {str(e)}{Colors.ENDC}")
                return
        
        # Use template if specified
        if args.template:
            template = self.template_registry.get_template(args.template)
            if not template:
                print(f"{Colors.RED}Template {args.template} not found{Colors.ENDC}")
                return
            
            # Merge template configuration with provided configuration
            template_config = template.get('configuration', {})
            template_config.update(configuration)
            configuration = template_config
        
        # Create mission
        mission = Mission(
            mission_id=f"mission-{str(uuid.uuid4())[:8]}",
            mission_type=mission_type,
            priority=args.priority or 5,
            target_layers=target_layers,
            configuration=configuration,
            simulation_required=not args.no_simulation,
            rollback_on_failure=not args.no_rollback,
            timeout_seconds=args.timeout,
            description=args.description
        )
        
        # Submit mission
        try:
            mission_id = self.execution_engine.submit_mission(mission)
            print(f"{Colors.GREEN}Mission {mission_id} submitted successfully{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error submitting mission: {str(e)}{Colors.ENDC}")
    
    def _interactive_mission_create(self):
        """Interactive mission creation"""
        print(f"{Colors.HEADER}{Colors.BOLD}Create New Mission{Colors.ENDC}")
        
        # Get mission type
        valid_types = [
            MissionType.DEPLOY, MissionType.UPDATE, MissionType.ROLLBACK,
            MissionType.SCALE, MissionType.MIGRATE, MissionType.BACKUP,
            MissionType.RESTORE, MissionType.HEALTH_CHECK, MissionType.SECURITY_SCAN,
            MissionType.COMPLIANCE_CHECK
        ]
        
        print(f"\n{Colors.BOLD}Available mission types:{Colors.ENDC}")
        for i, mission_type in enumerate(valid_types):
            print(f"{i+1}. {mission_type}")
        
        while True:
            try:
                type_choice = int(input("\nEnter mission type number: "))
                if 1 <= type_choice <= len(valid_types):
                    mission_type = valid_types[type_choice - 1]
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and {len(valid_types)}{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.ENDC}")
        
        # Get priority
        while True:
            try:
                priority = int(input("\nEnter mission priority (1-10, 1 being highest): "))
                if 1 <= priority <= 10:
                    break
                else:
                    print(f"{Colors.RED}Invalid priority. Please enter a number between 1 and 10{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.ENDC}")
        
        # Get target layers
        valid_layers = [
            "data-layer", "core-ai-layer", "generative-layer", "application-layer",
            "protocol-layer", "workflow-layer", "ui-ux-layer", "security-compliance-layer",
            "deployment-ops-layer", "native-app-layer"
        ]
        
        print(f"\n{Colors.BOLD}Available layers:{Colors.ENDC}")
        for i, layer in enumerate(valid_layers):
            print(f"{i+1}. {layer}")
        
        selected_layers = []
        while True:
            try:
                layer_input = input("\nEnter layer numbers (comma-separated, or 'all' for all layers): ")
                
                if layer_input.lower() == 'all':
                    selected_layers = valid_layers
                    break
                
                layer_choices = [int(choice.strip()) for choice in layer_input.split(',')]
                selected_layers = [valid_layers[choice - 1] for choice in layer_choices if 1 <= choice <= len(valid_layers)]
                
                if selected_layers:
                    break
                else:
                    print(f"{Colors.RED}No valid layers selected{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Please enter numbers separated by commas.{Colors.ENDC}")
        
        # Get description
        description = input("\nEnter mission description (optional): ")
        
        # Get simulation and rollback preferences
        simulation_required = input("\nRequire simulation before execution? (y/n, default: y): ").lower() != 'n'
        rollback_on_failure = input("\nAutomatically rollback on failure? (y/n, default: y): ").lower() != 'n'
        
        # Get timeout
        timeout_seconds = None
        timeout_input = input("\nEnter timeout in seconds (optional): ")
        if timeout_input:
            try:
                timeout_seconds = int(timeout_input)
            except ValueError:
                print(f"{Colors.YELLOW}Invalid timeout. Using default (no timeout).{Colors.ENDC}")
        
        # Get configuration
        print(f"\n{Colors.BOLD}Mission Configuration:{Colors.ENDC}")
        print("Enter configuration as JSON, or leave empty for default configuration.")
        print("Press Enter twice to finish.")
        
        config_lines = []
        while True:
            line = input()
            if not line and not config_lines:
                # Empty configuration
                configuration = {}
                break
            elif not line:
                # End of configuration
                try:
                    configuration = json.loads('\n'.join(config_lines))
                    break
                except json.JSONDecodeError as e:
                    print(f"{Colors.RED}Invalid JSON: {str(e)}{Colors.ENDC}")
                    print("Please try again.")
                    config_lines = []
            else:
                config_lines.append(line)
        
        # Create mission
        mission = Mission(
            mission_id=f"mission-{str(uuid.uuid4())[:8]}",
            mission_type=mission_type,
            priority=priority,
            target_layers=selected_layers,
            configuration=configuration,
            simulation_required=simulation_required,
            rollback_on_failure=rollback_on_failure,
            timeout_seconds=timeout_seconds,
            description=description
        )
        
        # Confirm submission
        print(f"\n{Colors.BOLD}Mission Summary:{Colors.ENDC}")
        print(f"Type: {mission_type}")
        print(f"Priority: {priority}")
        print(f"Target Layers: {', '.join(selected_layers)}")
        print(f"Description: {description or 'N/A'}")
        print(f"Simulation Required: {simulation_required}")
        print(f"Rollback on Failure: {rollback_on_failure}")
        print(f"Timeout: {timeout_seconds or 'None'}")
        print(f"Configuration: {json.dumps(configuration, indent=2)}")
        
        confirm = input(f"\n{Colors.BOLD}Submit this mission? (y/n): {Colors.ENDC}").lower()
        if confirm != 'y':
            print(f"{Colors.YELLOW}Mission submission canceled{Colors.ENDC}")
            return
        
        # Submit mission
        try:
            mission_id = self.execution_engine.submit_mission(mission)
            print(f"{Colors.GREEN}Mission {mission_id} submitted successfully{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error submitting mission: {str(e)}{Colors.ENDC}")
    
    def _handle_missions_cancel(self, args):
        """Handle missions cancel command"""
        try:
            result = self.execution_engine.cancel_mission(args.mission_id)
            
            if result:
                print(f"{Colors.GREEN}Mission {args.mission_id} canceled successfully{Colors.ENDC}")
            else:
                print(f"{Colors.RED}Failed to cancel mission {args.mission_id}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error canceling mission: {str(e)}{Colors.ENDC}")
    
    def _handle_missions_pause(self, args):
        """Handle missions pause command"""
        try:
            result = self.execution_engine.pause_mission(args.mission_id)
            
            if result:
                print(f"{Colors.GREEN}Mission {args.mission_id} paused successfully{Colors.ENDC}")
            else:
                print(f"{Colors.RED}Failed to pause mission {args.mission_id}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error pausing mission: {str(e)}{Colors.ENDC}")
    
    def _handle_missions_resume(self, args):
        """Handle missions resume command"""
        try:
            result = self.execution_engine.resume_mission(args.mission_id)
            
            if result:
                print(f"{Colors.GREEN}Mission {args.mission_id} resumed successfully{Colors.ENDC}")
            else:
                print(f"{Colors.RED}Failed to resume mission {args.mission_id}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error resuming mission: {str(e)}{Colors.ENDC}")
    
    def _handle_missions_rollback(self, args):
        """Handle missions rollback command"""
        try:
            result = self.execution_engine.rollback_mission(args.mission_id)
            
            if result:
                print(f"{Colors.GREEN}Mission {args.mission_id} rollback initiated successfully{Colors.ENDC}")
            else:
                print(f"{Colors.RED}Failed to rollback mission {args.mission_id}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error rolling back mission: {str(e)}{Colors.ENDC}")
    
    def _handle_layers(self, args):
        """Handle layers command"""
        if not args.subcommand:
            print("Missing subcommand. Use 'layers list', 'layers get', etc.")
            return
        
        if args.subcommand == 'list':
            self._handle_layers_list()
        elif args.subcommand == 'get':
            self._handle_layers_get(args)
        elif args.subcommand == 'capsules':
            self._handle_layers_capsules(args)
    
    def _handle_layers_list(self):
        """Handle layers list command"""
        try:
            layers = self.layer_integration_manager.get_layers()
            
            if not layers:
                print(f"{Colors.YELLOW}No layers found{Colors.ENDC}")
                return
            
            # Prepare table data
            headers = ["ID", "Name", "Status", "Capsule Count"]
            table_data = []
            
            for layer in layers:
                table_data.append([
                    layer['id'],
                    layer['name'],
                    self._colorize_status(layer['status']),
                    layer['capsule_count']
                ])
            
            # Print table
            print(f"{Colors.HEADER}{Colors.BOLD}Layers ({len(layers)}){Colors.ENDC}")
            print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"{Colors.RED}Error listing layers: {str(e)}{Colors.ENDC}")
    
    def _handle_layers_get(self, args):
        """Handle layers get command"""
        try:
            layer = self.layer_integration_manager.get_layer(args.layer_id)
            
            if not layer:
                print(f"{Colors.RED}Layer {args.layer_id} not found{Colors.ENDC}")
                return
            
            # Print layer details
            print(f"{Colors.HEADER}{Colors.BOLD}Layer Details{Colors.ENDC}")
            print(f"ID: {layer['id']}")
            print(f"Name: {layer['name']}")
            print(f"Status: {self._colorize_status(layer['status'])}")
            print(f"Capsule Count: {layer['capsule_count']}")
            
            if 'description' in layer:
                print(f"Description: {layer['description']}")
            
            if 'metrics' in layer:
                print(f"\n{Colors.HEADER}{Colors.BOLD}Metrics{Colors.ENDC}")
                for key, value in layer['metrics'].items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"{Colors.RED}Error getting layer: {str(e)}{Colors.ENDC}")
    
    def _handle_layers_capsules(self, args):
        """Handle layers capsules command"""
        try:
            capsules = self.layer_integration_manager.get_layer_capsules(args.layer_id)
            
            if capsules is None:
                print(f"{Colors.RED}Layer {args.layer_id} not found{Colors.ENDC}")
                return
            
            if not capsules:
                print(f"{Colors.YELLOW}No capsules found for layer {args.layer_id}{Colors.ENDC}")
                return
            
            # Prepare table data
            headers = ["ID", "Name", "Type", "Status"]
            table_data = []
            
            for capsule in capsules:
                table_data.append([
                    capsule['id'],
                    capsule['name'],
                    capsule['type'],
                    self._colorize_status(capsule['status'])
                ])
            
            # Print table
            print(f"{Colors.HEADER}{Colors.BOLD}Capsules for Layer {args.layer_id} ({len(capsules)}){Colors.ENDC}")
            print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"{Colors.RED}Error listing capsules: {str(e)}{Colors.ENDC}")
    
    def _handle_capsules(self, args):
        """Handle capsules command"""
        if not args.subcommand:
            print("Missing subcommand. Use 'capsules list', 'capsules get', etc.")
            return
        
        if args.subcommand == 'list':
            self._handle_capsules_list(args)
        elif args.subcommand == 'get':
            self._handle_capsules_get(args)
    
    def _handle_capsules_list(self, args):
        """Handle capsules list command"""
        try:
            capsules = self.cross_layer_integration_manager.get_capsules(args.layer, args.status)
            
            if not capsules:
                print(f"{Colors.YELLOW}No capsules found{Colors.ENDC}")
                return
            
            # Prepare table data
            headers = ["ID", "Name", "Type", "Layer", "Status"]
            table_data = []
            
            for capsule in capsules:
                table_data.append([
                    capsule['id'],
                    capsule['name'],
                    capsule['type'],
                    capsule['layer'],
                    self._colorize_status(capsule['status'])
                ])
            
            # Print table
            print(f"{Colors.HEADER}{Colors.BOLD}Capsules ({len(capsules)}){Colors.ENDC}")
            print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"{Colors.RED}Error listing capsules: {str(e)}{Colors.ENDC}")
    
    def _handle_capsules_get(self, args):
        """Handle capsules get command"""
        try:
            capsule = self.cross_layer_integration_manager.get_capsule(args.capsule_id)
            
            if not capsule:
                print(f"{Colors.RED}Capsule {args.capsule_id} not found{Colors.ENDC}")
                return
            
            # Print capsule details
            print(f"{Colors.HEADER}{Colors.BOLD}Capsule Details{Colors.ENDC}")
            print(f"ID: {capsule['id']}")
            print(f"Name: {capsule['name']}")
            print(f"Type: {capsule['type']}")
            print(f"Layer: {capsule['layer']}")
            print(f"Status: {self._colorize_status(capsule['status'])}")
            
            if 'description' in capsule:
                print(f"Description: {capsule['description']}")
            
            if 'metrics' in capsule:
                print(f"\n{Colors.HEADER}{Colors.BOLD}Metrics{Colors.ENDC}")
                for key, value in capsule['metrics'].items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"{Colors.RED}Error getting capsule: {str(e)}{Colors.ENDC}")
    
    def _handle_templates(self, args):
        """Handle templates command"""
        if not args.subcommand:
            print("Missing subcommand. Use 'templates list', 'templates get', etc.")
            return
        
        if args.subcommand == 'list':
            self._handle_templates_list()
        elif args.subcommand == 'get':
            self._handle_templates_get(args)
    
    def _handle_templates_list(self):
        """Handle templates list command"""
        try:
            templates = self.template_registry.list_templates()
            
            if not templates:
                print(f"{Colors.YELLOW}No templates found{Colors.ENDC}")
                return
            
            # Prepare table data
            headers = ["ID", "Name", "Type", "Description"]
            table_data = []
            
            for template in templates:
                # Truncate description if too long
                description = template.get('description', '')
                if len(description) > 50:
                    description = description[:47] + "..."
                
                table_data.append([
                    template['id'],
                    template['name'],
                    template['type'],
                    description
                ])
            
            # Print table
            print(f"{Colors.HEADER}{Colors.BOLD}Templates ({len(templates)}){Colors.ENDC}")
            print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"{Colors.RED}Error listing templates: {str(e)}{Colors.ENDC}")
    
    def _handle_templates_get(self, args):
        """Handle templates get command"""
        try:
            template = self.template_registry.get_template(args.template_id)
            
            if not template:
                print(f"{Colors.RED}Template {args.template_id} not found{Colors.ENDC}")
                return
            
            # Print template details
            print(f"{Colors.HEADER}{Colors.BOLD}Template Details{Colors.ENDC}")
            print(f"ID: {template['id']}")
            print(f"Name: {template['name']}")
            print(f"Type: {template['type']}")
            
            if 'description' in template:
                print(f"Description: {template['description']}")
            
            if 'configuration' in template:
                print(f"\n{Colors.HEADER}{Colors.BOLD}Configuration{Colors.ENDC}")
                print(json.dumps(template['configuration'], indent=2))
        except Exception as e:
            print(f"{Colors.RED}Error getting template: {str(e)}{Colors.ENDC}")
    
    def _colorize_status(self, status):
        """Add color to status string"""
        if status in ['active', 'succeeded']:
            return f"{Colors.GREEN}{status}{Colors.ENDC}"
        elif status in ['failed', 'inactive']:
            return f"{Colors.RED}{status}{Colors.ENDC}"
        elif status in ['pending', 'paused', 'rolling_back', 'rolled_back']:
            return f"{Colors.YELLOW}{status}{Colors.ENDC}"
        elif status in ['planning', 'simulating', 'executing']:
            return f"{Colors.BLUE}{status}{Colors.ENDC}"
        else:
            return status

# Main entry point
if __name__ == "__main__":
    cli = DeploymentOpsCLI()
    cli.run()
