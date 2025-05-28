"""
Prompt Mutator Agent for Industriverse Generative Layer

This module implements the prompt mutator agent that refines prompts based on
failures, corrections, and latency feedback to enable adaptive prompt engineering
for human-AI co-creation.
"""

import json
import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptMutatorAgent:
    """
    Implements adaptive prompt engineering for the Generative Layer.
    Refines prompts based on feedback, failures, and performance metrics.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the prompt mutator agent.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.prompt_history = {}
        self.success_patterns = {}
        self.failure_patterns = {}
        self.latency_metrics = {}
        self.mutation_strategies = self._init_mutation_strategies()
        
        logger.info("Prompt Mutator Agent initialized")
    
    def _init_mutation_strategies(self) -> Dict[str, Any]:
        """
        Initialize mutation strategies.
        
        Returns:
            Dictionary of mutation strategies
        """
        return {
            "clarify": self._clarify_prompt,
            "structure": self._add_structure,
            "simplify": self._simplify_prompt,
            "expand": self._expand_prompt,
            "add_examples": self._add_examples,
            "add_constraints": self._add_constraints,
            "industry_adapt": self._adapt_to_industry,
            "offer_specialize": self._specialize_for_offer
        }
    
    def register_prompt_attempt(self, prompt_id: str, prompt: str, 
                               context: Dict[str, Any]) -> None:
        """
        Register a prompt attempt for later analysis.
        
        Args:
            prompt_id: Unique identifier for the prompt
            prompt: The prompt text
            context: Additional context about the prompt
        """
        timestamp = time.time()
        
        if prompt_id not in self.prompt_history:
            self.prompt_history[prompt_id] = []
        
        self.prompt_history[prompt_id].append({
            "prompt": prompt,
            "context": context,
            "timestamp": timestamp,
            "status": "pending",
            "latency": None,
            "feedback": None
        })
        
        logger.debug(f"Registered prompt attempt for {prompt_id}")
    
    def register_prompt_result(self, prompt_id: str, status: str, 
                              latency: float, feedback: Optional[Dict[str, Any]] = None) -> None:
        """
        Register the result of a prompt attempt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            status: Status of the attempt ("success", "failure", "partial")
            latency: Latency in milliseconds
            feedback: Additional feedback (optional)
        """
        if prompt_id not in self.prompt_history or not self.prompt_history[prompt_id]:
            logger.warning(f"No prompt history found for {prompt_id}")
            return
        
        # Update the latest attempt
        latest = self.prompt_history[prompt_id][-1]
        latest["status"] = status
        latest["latency"] = latency
        latest["feedback"] = feedback
        
        # Update metrics
        self._update_metrics(prompt_id, status, latency, feedback)
        
        logger.debug(f"Registered prompt result for {prompt_id}: {status}")
    
    def _update_metrics(self, prompt_id: str, status: str, 
                       latency: float, feedback: Optional[Dict[str, Any]]) -> None:
        """
        Update metrics based on prompt result.
        
        Args:
            prompt_id: Unique identifier for the prompt
            status: Status of the attempt
            latency: Latency in milliseconds
            feedback: Additional feedback
        """
        # Get the prompt
        prompt = self.prompt_history[prompt_id][-1]["prompt"]
        
        # Update latency metrics
        if prompt not in self.latency_metrics:
            self.latency_metrics[prompt] = []
        
        self.latency_metrics[prompt].append(latency)
        
        # Update success/failure patterns
        if status == "success":
            self._update_pattern_dict(self.success_patterns, prompt, feedback)
        elif status == "failure":
            self._update_pattern_dict(self.failure_patterns, prompt, feedback)
    
    def _update_pattern_dict(self, pattern_dict: Dict[str, int], 
                            prompt: str, feedback: Optional[Dict[str, Any]]) -> None:
        """
        Update a pattern dictionary with a prompt.
        
        Args:
            pattern_dict: The pattern dictionary to update
            prompt: The prompt text
            feedback: Additional feedback
        """
        # Extract key phrases (simplified implementation)
        phrases = self._extract_key_phrases(prompt)
        
        # Update pattern counts
        for phrase in phrases:
            if phrase not in pattern_dict:
                pattern_dict[phrase] = 0
            
            pattern_dict[phrase] += 1
    
    def _extract_key_phrases(self, prompt: str) -> List[str]:
        """
        Extract key phrases from a prompt (simplified implementation).
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of key phrases
        """
        # This is a simplified implementation
        # In a real system, this would use NLP techniques
        
        # Split by common delimiters
        words = prompt.lower().split()
        phrases = []
        
        # Extract 1-3 word phrases
        for i in range(len(words)):
            if i < len(words):
                phrases.append(words[i])
            if i < len(words) - 1:
                phrases.append(f"{words[i]} {words[i+1]}")
            if i < len(words) - 2:
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return phrases
    
    def mutate_prompt(self, prompt: str, context: Dict[str, Any], 
                     feedback: Optional[Dict[str, Any]] = None) -> str:
        """
        Mutate a prompt based on context and feedback.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts (optional)
            
        Returns:
            The mutated prompt
        """
        logger.info("Mutating prompt based on context and feedback")
        
        # Determine which mutation strategies to apply
        strategies = self._select_mutation_strategies(prompt, context, feedback)
        
        # Apply selected strategies
        mutated_prompt = prompt
        for strategy_name in strategies:
            strategy_func = self.mutation_strategies.get(strategy_name)
            if strategy_func:
                mutated_prompt = strategy_func(mutated_prompt, context, feedback)
                logger.debug(f"Applied mutation strategy: {strategy_name}")
        
        # Register the mutated prompt
        prompt_id = context.get("prompt_id", str(time.time()))
        self.register_prompt_attempt(prompt_id, mutated_prompt, context)
        
        return mutated_prompt
    
    def _select_mutation_strategies(self, prompt: str, context: Dict[str, Any], 
                                  feedback: Optional[Dict[str, Any]]) -> List[str]:
        """
        Select mutation strategies based on context and feedback.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            List of selected strategy names
        """
        selected_strategies = []
        
        # If we have feedback, use it to guide strategy selection
        if feedback:
            if feedback.get("too_complex", False):
                selected_strategies.append("simplify")
            
            if feedback.get("too_vague", False):
                selected_strategies.append("clarify")
            
            if feedback.get("needs_structure", False):
                selected_strategies.append("structure")
            
            if feedback.get("needs_examples", False):
                selected_strategies.append("add_examples")
            
            if feedback.get("needs_constraints", False):
                selected_strategies.append("add_constraints")
        
        # Use context to guide strategy selection
        offer_type = context.get("offer_type", "")
        industry = context.get("industry", "")
        
        if offer_type:
            selected_strategies.append("offer_specialize")
        
        if industry:
            selected_strategies.append("industry_adapt")
        
        # If no strategies were selected, choose a default
        if not selected_strategies:
            # Choose a random strategy as default
            selected_strategies.append(random.choice(list(self.mutation_strategies.keys())))
        
        return selected_strategies
    
    def _clarify_prompt(self, prompt: str, context: Dict[str, Any], 
                       feedback: Optional[Dict[str, Any]]) -> str:
        """
        Clarify a prompt by adding more specific instructions.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The clarified prompt
        """
        # Add clarifying instructions based on the offer type
        offer_type = context.get("offer_type", "")
        
        clarifications = {
            "dashboard": "Create an industrial dashboard with real-time monitoring capabilities, clear data visualization, and actionable insights.",
            "report": "Generate a comprehensive report with executive summary, detailed analysis, and actionable recommendations.",
            "workflow": "Design a step-by-step workflow with clear inputs, outputs, decision points, and error handling.",
            "integration": "Develop an integration solution with clear API specifications, data mapping, and error handling.",
            "visualization": "Create a data visualization that clearly communicates key insights, trends, and anomalies.",
            "model": "Develop a predictive model with clear input features, output predictions, and performance metrics."
        }
        
        clarification = clarifications.get(offer_type, "Please be specific, detailed, and clear in your requirements.")
        
        # Add the clarification if it's not already in the prompt
        if clarification not in prompt:
            return f"{prompt}\n\nClarification: {clarification}"
        
        return prompt
    
    def _add_structure(self, prompt: str, context: Dict[str, Any], 
                      feedback: Optional[Dict[str, Any]]) -> str:
        """
        Add structure to a prompt.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The structured prompt
        """
        # If the prompt already has structure, return it as is
        if "## " in prompt or "1. " in prompt:
            return prompt
        
        # Add structure based on the offer type
        offer_type = context.get("offer_type", "")
        
        structures = {
            "dashboard": "## Dashboard Requirements\n\n## Data Sources\n\n## Visualization Components\n\n## User Interactions\n\n## Performance Requirements",
            "report": "## Executive Summary\n\n## Problem Statement\n\n## Analysis\n\n## Recommendations\n\n## Implementation Plan",
            "workflow": "## Workflow Overview\n\n## Inputs and Outputs\n\n## Process Steps\n\n## Decision Points\n\n## Error Handling",
            "integration": "## Integration Requirements\n\n## API Specifications\n\n## Data Mapping\n\n## Error Handling\n\n## Testing Approach",
            "visualization": "## Visualization Purpose\n\n## Data Sources\n\n## Visual Elements\n\n## Interactivity\n\n## Insights to Highlight",
            "model": "## Model Purpose\n\n## Input Features\n\n## Output Predictions\n\n## Training Data\n\n## Performance Metrics"
        }
        
        structure = structures.get(offer_type, "## Requirements\n\n## Specifications\n\n## Deliverables")
        
        # Combine the original prompt with the structure
        return f"{prompt}\n\nPlease structure your response as follows:\n\n{structure}"
    
    def _simplify_prompt(self, prompt: str, context: Dict[str, Any], 
                        feedback: Optional[Dict[str, Any]]) -> str:
        """
        Simplify a complex prompt.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The simplified prompt
        """
        # If the prompt is already short, return it as is
        if len(prompt.split()) < 50:
            return prompt
        
        # Split the prompt into sentences
        sentences = prompt.split(". ")
        
        # Keep only the most important sentences (first, last, and any with key terms)
        important_sentences = [sentences[0]]
        
        key_terms = ["important", "critical", "essential", "must", "should", "require", "need"]
        
        for sentence in sentences[1:-1]:
            if any(term in sentence.lower() for term in key_terms):
                important_sentences.append(sentence)
        
        if len(sentences) > 1:
            important_sentences.append(sentences[-1])
        
        # Combine the important sentences
        simplified = ". ".join(important_sentences)
        
        # Add a simplification note
        return f"{simplified}\n\nNote: This is a simplified version of the original request. Focus on the core requirements."
    
    def _expand_prompt(self, prompt: str, context: Dict[str, Any], 
                      feedback: Optional[Dict[str, Any]]) -> str:
        """
        Expand a prompt with additional details.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The expanded prompt
        """
        # Add details based on the offer type and industry
        offer_type = context.get("offer_type", "")
        industry = context.get("industry", "")
        
        expansions = {
            "dashboard": {
                "manufacturing": "Include OEE metrics, production throughput, quality metrics, and maintenance alerts.",
                "energy": "Include power generation metrics, consumption patterns, efficiency metrics, and anomaly detection.",
                "aerospace": "Include safety metrics, component performance, maintenance schedules, and compliance status."
            },
            "report": {
                "manufacturing": "Include production efficiency analysis, quality trends, cost optimization, and capacity planning.",
                "energy": "Include energy production analysis, consumption patterns, efficiency improvements, and regulatory compliance.",
                "aerospace": "Include safety analysis, component reliability, maintenance optimization, and compliance verification."
            },
            "workflow": {
                "manufacturing": "Include production planning, quality control, inventory management, and maintenance scheduling.",
                "energy": "Include energy dispatch, grid management, maintenance scheduling, and regulatory reporting.",
                "aerospace": "Include safety checks, component testing, maintenance procedures, and compliance verification."
            }
        }
        
        expansion = expansions.get(offer_type, {}).get(industry, "")
        
        if expansion:
            return f"{prompt}\n\nAdditional details: {expansion}"
        
        return prompt
    
    def _add_examples(self, prompt: str, context: Dict[str, Any], 
                     feedback: Optional[Dict[str, Any]]) -> str:
        """
        Add examples to a prompt.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The prompt with examples
        """
        # If the prompt already has examples, return it as is
        if "Example:" in prompt or "For example:" in prompt:
            return prompt
        
        # Add examples based on the offer type
        offer_type = context.get("offer_type", "")
        
        examples = {
            "dashboard": "Example: A manufacturing dashboard showing real-time OEE, production counts, quality metrics, and maintenance alerts with drill-down capabilities.",
            "report": "Example: A monthly production efficiency report with executive summary, trend analysis, root cause identification, and improvement recommendations.",
            "workflow": "Example: A predictive maintenance workflow that monitors equipment health, predicts failures, schedules maintenance, and tracks resolution.",
            "integration": "Example: An integration between the MES and ERP systems that synchronizes production orders, inventory levels, and quality data.",
            "visualization": "Example: A heat map showing machine utilization across the factory floor with color coding for efficiency levels and interactive filters.",
            "model": "Example: A predictive maintenance model that uses vibration, temperature, and operational data to predict equipment failures 24-48 hours in advance."
        }
        
        example = examples.get(offer_type, "")
        
        if example:
            return f"{prompt}\n\n{example}"
        
        return prompt
    
    def _add_constraints(self, prompt: str, context: Dict[str, Any], 
                        feedback: Optional[Dict[str, Any]]) -> str:
        """
        Add constraints to a prompt.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The prompt with constraints
        """
        # If the prompt already has constraints, return it as is
        if "Constraints:" in prompt or "Requirements:" in prompt:
            return prompt
        
        # Add constraints based on the offer type and industry
        offer_type = context.get("offer_type", "")
        industry = context.get("industry", "")
        
        constraints = {
            "dashboard": {
                "manufacturing": "Constraints: Must support real-time updates (< 5s latency), mobile responsiveness, role-based access control, and offline operation.",
                "energy": "Constraints: Must comply with IEC 61850, support high-frequency data (100ms intervals), and implement role-based security.",
                "aerospace": "Constraints: Must comply with DO-178C, support audit trails, and implement multi-factor authentication."
            },
            "report": {
                "manufacturing": "Constraints: Must include executive summary (< 2 pages), detailed analysis (< 10 pages), and actionable recommendations.",
                "energy": "Constraints: Must comply with regulatory reporting requirements, include data quality assessment, and provide confidence intervals.",
                "aerospace": "Constraints: Must comply with AS9100 documentation standards, include traceability to requirements, and provide verification evidence."
            }
        }
        
        constraint = constraints.get(offer_type, {}).get(industry, "")
        
        if constraint:
            return f"{prompt}\n\n{constraint}"
        
        return prompt
    
    def _adapt_to_industry(self, prompt: str, context: Dict[str, Any], 
                          feedback: Optional[Dict[str, Any]]) -> str:
        """
        Adapt a prompt to a specific industry.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The industry-adapted prompt
        """
        industry = context.get("industry", "")
        
        if not industry:
            return prompt
        
        # Add industry-specific terminology and requirements
        industry_adaptations = {
            "manufacturing": "Ensure compatibility with manufacturing systems (MES, ERP, SCADA) and industry standards (ISA-95, OPC UA). Focus on OEE, quality, throughput, and cost optimization.",
            "energy": "Ensure compatibility with energy management systems (EMS, SCADA, DCS) and industry standards (IEC 61850, IEC 61970). Focus on efficiency, reliability, demand response, and regulatory compliance.",
            "aerospace": "Ensure compatibility with aerospace systems (PLM, MRO, QMS) and industry standards (AS9100, DO-178C). Focus on safety, reliability, traceability, and compliance.",
            "automotive": "Ensure compatibility with automotive systems (PLM, MES, QMS) and industry standards (IATF 16949, ISO 26262). Focus on quality, efficiency, safety, and supply chain integration.",
            "healthcare": "Ensure compatibility with healthcare systems (EHR, PACS, LIS) and industry standards (HL7, DICOM, HIPAA). Focus on patient safety, data security, regulatory compliance, and interoperability.",
            "logistics": "Ensure compatibility with logistics systems (WMS, TMS, ERP) and industry standards (GS1, EDI). Focus on efficiency, visibility, traceability, and cost optimization."
        }
        
        adaptation = industry_adaptations.get(industry, "")
        
        if adaptation and adaptation not in prompt:
            return f"{prompt}\n\nIndustry-specific requirements: {adaptation}"
        
        return prompt
    
    def _specialize_for_offer(self, prompt: str, context: Dict[str, Any], 
                             feedback: Optional[Dict[str, Any]]) -> str:
        """
        Specialize a prompt for a specific offer type.
        
        Args:
            prompt: The original prompt
            context: Context about the generation task
            feedback: Feedback on previous attempts
            
        Returns:
            The offer-specialized prompt
        """
        offer_type = context.get("offer_type", "")
        offer_id = context.get("offer_id", "")
        
        if not offer_type and not offer_id:
            return prompt
        
        # Add offer-specific requirements
        offer_specializations = {
            "dashboard": "Ensure the dashboard includes real-time data visualization, KPI tracking, anomaly detection, and actionable insights. Support filtering, drill-down, and customizable views.",
            "report": "Ensure the report includes executive summary, detailed analysis, data visualization, and actionable recommendations. Support PDF export, scheduled generation, and distribution.",
            "workflow": "Ensure the workflow includes clear steps, decision points, error handling, and integration points. Support manual and automated execution, tracking, and reporting.",
            "integration": "Ensure the integration includes clear API specifications, data mapping, transformation rules, and error handling. Support batch and real-time processing, monitoring, and alerting.",
            "visualization": "Ensure the visualization includes clear data representation, interactive elements, filtering, and insights. Support multiple chart types, responsive design, and export capabilities.",
            "model": "Ensure the model includes clear input/output specifications, performance metrics, and deployment options. Support training, validation, monitoring, and retraining."
        }
        
        specialization = offer_specializations.get(offer_type, "")
        
        # If we have an offer ID, add specific requirements for that offer
        if offer_id and offer_id.isdigit():
            offer_num = int(offer_id)
            if 1 <= offer_num <= 500:  # Assuming 500 offers as per the PDF
                specialization += f"\n\nThis is for Offer #{offer_id} in the Industriverse catalog."
        
        if specialization and specialization not in prompt:
            return f"{prompt}\n\nOffer-specific requirements: {specialization}"
        
        return prompt
    
    def analyze_prompt_history(self, prompt_id: str) -> Dict[str, Any]:
        """
        Analyze the history of a prompt to identify patterns.
        
        Args:
            prompt_id: The prompt ID to analyze
            
        Returns:
            Analysis results
        """
        if prompt_id not in self.prompt_history:
            logger.warning(f"No prompt history found for {prompt_id}")
            return {"error": "No prompt history found"}
        
        history = self.prompt_history[prompt_id]
        
        # Calculate success rate
        attempts = len(history)
        successes = sum(1 for attempt in history if attempt["status"] == "success")
        success_rate = successes / attempts if attempts > 0 else 0
        
        # Calculate average latency
        latencies = [attempt["latency"] for attempt in history if attempt["latency"] is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else None
        
        # Identify patterns in successful prompts
        successful_prompts = [attempt["prompt"] for attempt in history if attempt["status"] == "success"]
        successful_patterns = self._identify_patterns(successful_prompts)
        
        # Identify patterns in failed prompts
        failed_prompts = [attempt["prompt"] for attempt in history if attempt["status"] == "failure"]
        failed_patterns = self._identify_patterns(failed_prompts)
        
        return {
            "prompt_id": prompt_id,
            "attempts": attempts,
            "success_rate": success_rate,
            "avg_latency": avg_latency,
            "successful_patterns": successful_patterns,
            "failed_patterns": failed_patterns
        }
    
    def _identify_patterns(self, prompts: List[str]) -> List[str]:
        """
        Identify common patterns in a list of prompts.
        
        Args:
            prompts: List of prompts to analyze
            
        Returns:
            List of common patterns
        """
        if not prompts:
            return []
        
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP techniques
        
        # Extract phrases from all prompts
        all_phrases = []
        for prompt in prompts:
            all_phrases.extend(self._extract_key_phrases(prompt))
        
        # Count phrase frequencies
        phrase_counts = {}
        for phrase in all_phrases:
            if phrase not in phrase_counts:
                phrase_counts[phrase] = 0
            phrase_counts[phrase] += 1
        
        # Sort by frequency
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return the top 10 phrases
        return [phrase for phrase, count in sorted_phrases[:10]]
    
    def get_prompt_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get prompt recommendations based on context.
        
        Args:
            context: Context about the generation task
            
        Returns:
            List of recommended prompts
        """
        offer_type = context.get("offer_type", "")
        industry = context.get("industry", "")
        
        # Base recommendations
        recommendations = [
            "Create a detailed specification for {offer_type} that meets industry standards and best practices.",
            "Design a {offer_type} solution that addresses key challenges in the {industry} industry.",
            "Develop a comprehensive {offer_type} that integrates with existing systems and workflows."
        ]
        
        # Offer-specific recommendations
        offer_recommendations = {
            "dashboard": [
                "Create an industrial dashboard that provides real-time visibility into {industry} operations with KPIs for efficiency, quality, and performance.",
                "Design a responsive dashboard for {industry} that supports both strategic decision-making and operational monitoring.",
                "Develop a customizable dashboard that visualizes critical {industry} metrics with drill-down capabilities and anomaly detection."
            ],
            "report": [
                "Create a comprehensive report template for {industry} that includes executive summary, detailed analysis, and actionable recommendations.",
                "Design an automated reporting solution that generates periodic insights into {industry} performance metrics.",
                "Develop a dynamic reporting system that combines data from multiple sources to provide holistic {industry} insights."
            ],
            "workflow": [
                "Create a streamlined workflow for {industry} that optimizes process efficiency and ensures compliance.",
                "Design an intelligent workflow that automates routine tasks and highlights exceptions requiring human intervention.",
                "Develop an integrated workflow that connects disparate systems and provides end-to-end visibility for {industry} processes."
            ]
        }
        
        # Add offer-specific recommendations if available
        if offer_type in offer_recommendations:
            recommendations.extend(offer_recommendations[offer_type])
        
        # Format recommendations with context
        formatted_recommendations = []
        for rec in recommendations:
            try:
                formatted_rec = rec.format(offer_type=offer_type or "solution", industry=industry or "industrial")
                formatted_recommendations.append(formatted_rec)
            except KeyError:
                # Skip recommendations that require missing context
                continue
        
        return formatted_recommendations
    
    def export_learning(self) -> Dict[str, Any]:
        """
        Export the agent's learning for persistence.
        
        Returns:
            The agent's learning data
        """
        return {
            "success_patterns": self.success_patterns,
            "failure_patterns": self.failure_patterns,
            "latency_metrics": self.latency_metrics
        }
    
    def import_learning(self, learning_data: Dict[str, Any]) -> None:
        """
        Import learning data from persistence.
        
        Args:
            learning_data: The learning data to import
        """
        if "success_patterns" in learning_data:
            self.success_patterns = learning_data["success_patterns"]
        
        if "failure_patterns" in learning_data:
            self.failure_patterns = learning_data["failure_patterns"]
        
        if "latency_metrics" in learning_data:
            self.latency_metrics = learning_data["latency_metrics"]
        
        logger.info("Imported learning data")
