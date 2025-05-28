"""
Workflow Evolution Agent Module for the Workflow Automation Layer.

This agent enables workflows to evolve over time through genetic algorithms,
reinforcement learning, and pattern recognition. It analyzes workflow performance,
identifies optimization opportunities, and generates improved workflow variants.
"""

import asyncio
import json
import logging
import uuid
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowEvolutionAgent:
    """Agent for evolving workflows through genetic algorithms and reinforcement learning."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow evolution agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-evolution-agent"
        self.agent_capabilities = ["workflow_evolution", "genetic_algorithms", "reinforcement_learning", "pattern_recognition"]
        self.supported_protocols = ["MCP", "A2A"]
        
        # Evolution configuration
        self.population_size = 10  # Number of workflow variants to maintain
        self.mutation_rate = 0.1   # Probability of mutation
        self.crossover_rate = 0.7  # Probability of crossover
        self.generation_limit = 10 # Maximum number of generations
        
        # Storage for evolution data
        self.evolution_sessions = {}  # Active evolution sessions
        self.evolution_history = {}   # Historical evolution data
        
        logger.info("Workflow Evolution Agent initialized")

    async def start_evolution_session(self, evolution_request: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow evolution session.

        Args:
            evolution_request: Request data including workflow_id, optimization_goals, etc.

        Returns:
            Dict containing session start status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "optimization_goals"]
            for field in required_fields:
                if field not in evolution_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = evolution_request["workflow_id"]
            optimization_goals = evolution_request["optimization_goals"]
            
            # Validate optimization goals
            valid_goals = ["performance", "reliability", "resource_efficiency", "adaptability"]
            for goal in optimization_goals:
                if goal not in valid_goals:
                    return {
                        "success": False,
                        "error": f"Invalid optimization goal: {goal}. Must be one of {valid_goals}"
                    }
            
            # Get workflow manifest
            workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
            if not workflow_manifest:
                return {
                    "success": False,
                    "error": f"Workflow manifest not found for {workflow_id}"
                }
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create initial population
            initial_population = await self._create_initial_population(workflow_manifest, evolution_request)
            
            # Store session details
            self.evolution_sessions[session_id] = {
                "workflow_id": workflow_id,
                "optimization_goals": optimization_goals,
                "parameters": evolution_request.get("parameters", {}),
                "start_time": datetime.utcnow().isoformat(),
                "status": "initializing",
                "current_generation": 0,
                "population": initial_population,
                "best_fitness": None,
                "best_variant": None,
                "fitness_history": []
            }
            
            # Start evolution process in the background
            asyncio.create_task(self._run_evolution(session_id))
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "start_evolution_session",
                "reason": f"Started evolution session for workflow {workflow_id} with goals {optimization_goals}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Started evolution session {session_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "workflow_id": workflow_id,
                "status": "initializing"
            }
            
        except Exception as e:
            logger.error(f"Error starting evolution session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_initial_population(self, workflow_manifest: Dict[str, Any], evolution_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create initial population of workflow variants.

        Args:
            workflow_manifest: Original workflow manifest.
            evolution_request: Evolution request parameters.

        Returns:
            List of workflow variants.
        """
        population = []
        
        # Add the original workflow as the first variant
        original_variant = {
            "variant_id": str(uuid.uuid4()),
            "manifest": workflow_manifest,
            "parent_ids": [],
            "generation": 0,
            "fitness": None,
            "mutation_history": []
        }
        population.append(original_variant)
        
        # Create additional variants through mutation
        for i in range(self.population_size - 1):
            variant = await self._create_mutated_variant(original_variant, 0)
            population.append(variant)
        
        return population

    async def _create_mutated_variant(self, parent_variant: Dict[str, Any], generation: int) -> Dict[str, Any]:
        """Create a mutated variant of a workflow.

        Args:
            parent_variant: Parent workflow variant.
            generation: Current generation number.

        Returns:
            Mutated workflow variant.
        """
        # Deep copy the parent manifest
        manifest_copy = json.loads(json.dumps(parent_variant["manifest"]))
        
        # Apply mutations
        mutations = []
        
        # Mutation 1: Task parameter adjustment
        if "tasks" in manifest_copy:
            for task in manifest_copy["tasks"]:
                if "parameters" in task and random.random() < self.mutation_rate:
                    param_key = random.choice(list(task["parameters"].keys())) if task["parameters"] else None
                    if param_key:
                        # Simple numeric parameter mutation
                        if isinstance(task["parameters"][param_key], (int, float)):
                            original_value = task["parameters"][param_key]
                            # Adjust by up to ±20%
                            adjustment = random.uniform(-0.2, 0.2)
                            task["parameters"][param_key] = original_value * (1 + adjustment)
                            
                            mutations.append({
                                "type": "parameter_adjustment",
                                "task_id": task.get("task_id"),
                                "parameter": param_key,
                                "original_value": original_value,
                                "new_value": task["parameters"][param_key]
                            })
        
        # Mutation 2: Task reordering (for parallel tasks)
        if "execution_graph" in manifest_copy and random.random() < self.mutation_rate:
            for node_id, node in manifest_copy["execution_graph"].items():
                if "parallel_tasks" in node and len(node["parallel_tasks"]) > 1:
                    # Shuffle the parallel tasks
                    original_order = node["parallel_tasks"].copy()
                    random.shuffle(node["parallel_tasks"])
                    
                    if original_order != node["parallel_tasks"]:
                        mutations.append({
                            "type": "task_reordering",
                            "node_id": node_id,
                            "original_order": original_order,
                            "new_order": node["parallel_tasks"]
                        })
        
        # Mutation 3: Timeout adjustment
        if "task_timeouts" in manifest_copy and random.random() < self.mutation_rate:
            for task_id, timeout in manifest_copy["task_timeouts"].items():
                if random.random() < self.mutation_rate:
                    original_timeout = timeout
                    # Adjust timeout by up to ±30%
                    adjustment = random.uniform(-0.3, 0.3)
                    manifest_copy["task_timeouts"][task_id] = int(timeout * (1 + adjustment))
                    
                    mutations.append({
                        "type": "timeout_adjustment",
                        "task_id": task_id,
                        "original_timeout": original_timeout,
                        "new_timeout": manifest_copy["task_timeouts"][task_id]
                    })
        
        # Mutation 4: Retry strategy adjustment
        if "retry_strategies" in manifest_copy and random.random() < self.mutation_rate:
            for task_id, strategy in manifest_copy["retry_strategies"].items():
                if random.random() < self.mutation_rate and "max_retries" in strategy:
                    original_max_retries = strategy["max_retries"]
                    # Adjust max retries by ±1-2
                    adjustment = random.randint(-1, 2)
                    strategy["max_retries"] = max(1, original_max_retries + adjustment)
                    
                    mutations.append({
                        "type": "retry_adjustment",
                        "task_id": task_id,
                        "original_max_retries": original_max_retries,
                        "new_max_retries": strategy["max_retries"]
                    })
        
        # Create the new variant
        variant = {
            "variant_id": str(uuid.uuid4()),
            "manifest": manifest_copy,
            "parent_ids": [parent_variant["variant_id"]],
            "generation": generation + 1,
            "fitness": None,
            "mutation_history": mutations
        }
        
        return variant

    async def _create_crossover_variant(self, parent1: Dict[str, Any], parent2: Dict[str, Any], generation: int) -> Dict[str, Any]:
        """Create a new variant by crossing over two parent variants.

        Args:
            parent1: First parent workflow variant.
            parent2: Second parent workflow variant.
            generation: Current generation number.

        Returns:
            New workflow variant created through crossover.
        """
        # Deep copy the parent manifests
        manifest1 = json.loads(json.dumps(parent1["manifest"]))
        manifest2 = json.loads(json.dumps(parent2["manifest"]))
        
        # Create a new manifest for the child
        child_manifest = json.loads(json.dumps(manifest1))
        crossovers = []
        
        # Crossover 1: Task parameters
        if "tasks" in manifest1 and "tasks" in manifest2:
            # Create task ID mapping
            tasks1 = {task.get("task_id"): task for task in manifest1["tasks"]}
            tasks2 = {task.get("task_id"): task for task in manifest2["tasks"]}
            
            # Find common task IDs
            common_task_ids = set(tasks1.keys()) & set(tasks2.keys())
            
            for task_id in common_task_ids:
                if random.random() < self.crossover_rate and "parameters" in tasks1[task_id] and "parameters" in tasks2[task_id]:
                    # Get parameters from both parents
                    params1 = tasks1[task_id]["parameters"]
                    params2 = tasks2[task_id]["parameters"]
                    
                    # Find common parameter keys
                    common_params = set(params1.keys()) & set(params2.keys())
                    
                    for param_key in common_params:
                        # Randomly choose parameter from either parent
                        if random.random() < 0.5:
                            # Find the task in the child manifest
                            for task in child_manifest["tasks"]:
                                if task.get("task_id") == task_id:
                                    original_value = task["parameters"][param_key]
                                    task["parameters"][param_key] = params2[param_key]
                                    
                                    crossovers.append({
                                        "type": "parameter_crossover",
                                        "task_id": task_id,
                                        "parameter": param_key,
                                        "original_value": original_value,
                                        "new_value": params2[param_key],
                                        "source": "parent2"
                                    })
        
        # Crossover 2: Timeout values
        if "task_timeouts" in manifest1 and "task_timeouts" in manifest2:
            timeouts1 = manifest1["task_timeouts"]
            timeouts2 = manifest2["task_timeouts"]
            
            # Find common task IDs
            common_task_ids = set(timeouts1.keys()) & set(timeouts2.keys())
            
            for task_id in common_task_ids:
                if random.random() < self.crossover_rate:
                    # Randomly choose timeout from either parent
                    if random.random() < 0.5:
                        original_timeout = child_manifest["task_timeouts"][task_id]
                        child_manifest["task_timeouts"][task_id] = timeouts2[task_id]
                        
                        crossovers.append({
                            "type": "timeout_crossover",
                            "task_id": task_id,
                            "original_timeout": original_timeout,
                            "new_timeout": timeouts2[task_id],
                            "source": "parent2"
                        })
        
        # Create the new variant
        variant = {
            "variant_id": str(uuid.uuid4()),
            "manifest": child_manifest,
            "parent_ids": [parent1["variant_id"], parent2["variant_id"]],
            "generation": generation + 1,
            "fitness": None,
            "crossover_history": crossovers
        }
        
        return variant

    async def _run_evolution(self, session_id: str):
        """Run the evolution process in the background.

        Args:
            session_id: ID of the evolution session.
        """
        if session_id not in self.evolution_sessions:
            logger.error(f"Evolution session {session_id} not found")
            return
        
        session = self.evolution_sessions[session_id]
        workflow_id = session["workflow_id"]
        
        logger.info(f"Running evolution for session {session_id} (workflow {workflow_id})")
        
        try:
            # Update status
            session["status"] = "running"
            
            # Run for specified number of generations
            for generation in range(self.generation_limit):
                session["current_generation"] = generation + 1
                
                # Evaluate fitness of current population
                await self._evaluate_population_fitness(session)
                
                # Sort population by fitness
                session["population"].sort(key=lambda x: x["fitness"] if x["fitness"] is not None else float('-inf'), reverse=True)
                
                # Update best variant
                if session["population"][0]["fitness"] is not None:
                    if session["best_fitness"] is None or session["population"][0]["fitness"] > session["best_fitness"]:
                        session["best_fitness"] = session["population"][0]["fitness"]
                        session["best_variant"] = session["population"][0]
                
                # Record fitness history
                session["fitness_history"].append({
                    "generation": generation + 1,
                    "best_fitness": session["best_fitness"],
                    "avg_fitness": sum(v["fitness"] for v in session["population"] if v["fitness"] is not None) / 
                                  len([v for v in session["population"] if v["fitness"] is not None])
                })
                
                # Check if we've reached the target fitness
                target_fitness = session["parameters"].get("target_fitness")
                if target_fitness and session["best_fitness"] and session["best_fitness"] >= target_fitness:
                    logger.info(f"Evolution session {session_id} reached target fitness")
                    break
                
                # Create next generation
                if generation < self.generation_limit - 1:
                    await self._create_next_generation(session)
            
            # Update status
            session["status"] = "completed"
            session["end_time"] = datetime.utcnow().isoformat()
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "evolution_completed",
                "reason": f"Completed evolution session for workflow {workflow_id} with best fitness {session['best_fitness']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Evolution session {session_id} completed")
            
            # Move to history
            self.evolution_history[session_id] = session
            
        except Exception as e:
            logger.error(f"Error during evolution session {session_id}: {str(e)}")
            session["status"] = "failed"
            session["end_time"] = datetime.utcnow().isoformat()
            session["error"] = str(e)

    async def _evaluate_population_fitness(self, session: Dict[str, Any]):
        """Evaluate fitness of all variants in the population.

        Args:
            session: Evolution session data.
        """
        optimization_goals = session["optimization_goals"]
        
        for variant in session["population"]:
            if variant["fitness"] is None:  # Only evaluate if not already evaluated
                # In a real implementation, this would involve:
                # 1. Creating a test workflow instance with the variant manifest
                # 2. Running the workflow with test data
                # 3. Collecting performance metrics
                # 4. Calculating fitness based on optimization goals
                
                # Placeholder implementation - simulate fitness evaluation
                fitness = await self._simulate_fitness_evaluation(variant, optimization_goals)
                variant["fitness"] = fitness
                
                logger.info(f"Evaluated variant {variant['variant_id']} with fitness {fitness}")

    async def _simulate_fitness_evaluation(self, variant: Dict[str, Any], optimization_goals: List[str]) -> float:
        """Simulate fitness evaluation for a workflow variant.

        Args:
            variant: Workflow variant to evaluate.
            optimization_goals: List of optimization goals.

        Returns:
            Simulated fitness score.
        """
        # This is a placeholder for actual fitness evaluation
        # In a real implementation, this would run the workflow and measure metrics
        
        base_fitness = 0.5  # Base fitness
        
        # Adjust based on mutation history
        mutation_bonus = 0
        for mutation in variant.get("mutation_history", []):
            if mutation["type"] == "parameter_adjustment":
                # Simulate some mutations being beneficial
                mutation_bonus += random.uniform(-0.1, 0.2)
            elif mutation["type"] == "task_reordering":
                mutation_bonus += random.uniform(-0.05, 0.15)
            elif mutation["type"] == "timeout_adjustment":
                mutation_bonus += random.uniform(-0.05, 0.1)
            elif mutation["type"] == "retry_adjustment":
                mutation_bonus += random.uniform(-0.05, 0.1)
        
        # Adjust based on crossover history
        crossover_bonus = 0
        for crossover in variant.get("crossover_history", []):
            crossover_bonus += random.uniform(-0.05, 0.15)
        
        # Combine and normalize fitness
        fitness = base_fitness + mutation_bonus + crossover_bonus
        fitness = max(0.0, min(1.0, fitness))  # Clamp between 0 and 1
        
        return fitness

    async def _create_next_generation(self, session: Dict[str, Any]):
        """Create the next generation of workflow variants.

        Args:
            session: Evolution session data.
        """
        current_population = session["population"]
        next_generation = []
        
        # Elitism: Keep the best variants
        elitism_count = max(1, int(self.population_size * 0.2))
        for i in range(elitism_count):
            if i < len(current_population):
                next_generation.append(current_population[i])
        
        # Fill the rest with new variants
        while len(next_generation) < self.population_size:
            # Selection: Tournament selection
            parent1 = self._tournament_selection(current_population)
            
            # Decide between mutation and crossover
            if random.random() < self.crossover_rate and len(current_population) > 1:
                # Crossover
                parent2 = self._tournament_selection(current_population)
                while parent2["variant_id"] == parent1["variant_id"]:
                    parent2 = self._tournament_selection(current_population)
                
                new_variant = await self._create_crossover_variant(
                    parent1, parent2, session["current_generation"]
                )
            else:
                # Mutation
                new_variant = await self._create_mutated_variant(
                    parent1, session["current_generation"]
                )
            
            next_generation.append(new_variant)
        
        # Update population
        session["population"] = next_generation

    def _tournament_selection(self, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select a variant using tournament selection.

        Args:
            population: List of variants to select from.

        Returns:
            Selected variant.
        """
        # Select random candidates
        tournament_size = max(2, int(len(population) * 0.3))
        candidates = random.sample(population, min(tournament_size, len(population)))
        
        # Find the best candidate
        best_candidate = max(candidates, key=lambda x: x["fitness"] if x["fitness"] is not None else float('-inf'))
        
        return best_candidate

    async def get_evolution_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of an evolution session.

        Args:
            session_id: ID of the evolution session.

        Returns:
            Dict containing evolution status.
        """
        if session_id in self.evolution_sessions:
            session = self.evolution_sessions[session_id]
            return {
                "success": True,
                "session_id": session_id,
                "workflow_id": session["workflow_id"],
                "status": session["status"],
                "current_generation": session["current_generation"],
                "total_generations": self.generation_limit,
                "best_fitness": session["best_fitness"],
                "start_time": session["start_time"]
            }
        elif session_id in self.evolution_history:
            session = self.evolution_history[session_id]
            return {
                "success": True,
                "session_id": session_id,
                "workflow_id": session["workflow_id"],
                "status": session["status"],
                "current_generation": session["current_generation"],
                "total_generations": self.generation_limit,
                "best_fitness": session["best_fitness"],
                "start_time": session["start_time"],
                "end_time": session.get("end_time"),
                "error": session.get("error")
            }
        else:
            return {
                "success": False,
                "error": f"Evolution session {session_id} not found"
            }

    async def get_best_variant(self, session_id: str) -> Dict[str, Any]:
        """Get the best workflow variant from an evolution session.

        Args:
            session_id: ID of the evolution session.

        Returns:
            Dict containing the best variant or error.
        """
        session = None
        if session_id in self.evolution_sessions:
            session = self.evolution_sessions[session_id]
        elif session_id in self.evolution_history:
            session = self.evolution_history[session_id]
        
        if not session:
            return {
                "success": False,
                "error": f"Evolution session {session_id} not found"
            }
        
        if session["status"] == "initializing":
            return {
                "success": False,
                "error": f"Evolution session {session_id} is still initializing"
            }
        
        if not session["best_variant"]:
            return {
                "success": False,
                "error": f"No best variant found for session {session_id}"
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_id": session["workflow_id"],
            "variant_id": session["best_variant"]["variant_id"],
            "fitness": session["best_variant"]["fitness"],
            "generation": session["best_variant"]["generation"],
            "manifest": session["best_variant"]["manifest"]
        }

    async def apply_best_variant(self, session_id: str) -> Dict[str, Any]:
        """Apply the best workflow variant from an evolution session.

        Args:
            session_id: ID of the evolution session.

        Returns:
            Dict containing application status.
        """
        # Get the best variant
        best_variant_result = await self.get_best_variant(session_id)
        if not best_variant_result["success"]:
            return best_variant_result
        
        session = None
        if session_id in self.evolution_sessions:
            session = self.evolution_sessions[session_id]
        elif session_id in self.evolution_history:
            session = self.evolution_history[session_id]
        
        workflow_id = session["workflow_id"]
        best_variant = session["best_variant"]
        
        try:
            # Create a new workflow version with the evolved manifest
            new_workflow_id = await self.workflow_runtime.create_workflow_version(
                workflow_id, best_variant["manifest"]
            )
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "apply_best_variant",
                "reason": f"Applied best variant from evolution session {session_id} to create new workflow version {new_workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Applied best variant from session {session_id} to create workflow {new_workflow_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "original_workflow_id": workflow_id,
                "new_workflow_id": new_workflow_id,
                "variant_id": best_variant["variant_id"],
                "fitness": best_variant["fitness"]
            }
            
        except Exception as e:
            logger.error(f"Error applying best variant from session {session_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_fitness_history(self, session_id: str) -> Dict[str, Any]:
        """Get the fitness history of an evolution session.

        Args:
            session_id: ID of the evolution session.

        Returns:
            Dict containing fitness history or error.
        """
        session = None
        if session_id in self.evolution_sessions:
            session = self.evolution_sessions[session_id]
        elif session_id in self.evolution_history:
            session = self.evolution_history[session_id]
        
        if not session:
            return {
                "success": False,
                "error": f"Evolution session {session_id} not found"
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_id": session["workflow_id"],
            "fitness_history": session["fitness_history"]
        }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols],
            "resilience_mode": "adaptive",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["evolution_control_node", "fitness_visualization_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            payload = message.get("payload", {})
            
            if message_type == "start_evolution_session":
                return await self.start_evolution_session(payload)
            elif message_type == "get_evolution_status":
                session_id = payload.get("session_id")
                return await self.get_evolution_status(session_id)
            elif message_type == "get_best_variant":
                session_id = payload.get("session_id")
                return await self.get_best_variant(session_id)
            elif message_type == "apply_best_variant":
                session_id = payload.get("session_id")
                return await self.apply_best_variant(session_id)
            elif message_type == "get_fitness_history":
                session_id = payload.get("session_id")
                return await self.get_fitness_history(session_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
