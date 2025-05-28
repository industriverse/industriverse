# Industriverse Core AI Layer Guide

## Introduction

The Core AI Layer provides the foundational artificial intelligence capabilities for the Industriverse Framework. It includes components for representation learning (VQ-VAE), large language models (LLM), and other core AI functionalities that power intelligent applications across the framework. This guide details the architecture, components, integration points, and usage of the Core AI Layer.

## Architecture Overview

The Core AI Layer is structured around several key components:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             CORE AI LAYER                               │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │             │  │             │  │             │  │             │     │
│  │   VQ-VAE    │  │     LLM     │  │   Model     │  │   Inference │     │
│  │  Component  │  │  Component  │  │  Registry   │  │   Engine    │     │
│  │             │  │             │  │             │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │             │  │             │  │             │  │             │     │
│  │   Training  │  │  Evaluation │  │   AI Agent  │  │ AI Protocols│     │
│  │   Service   │  │   Service   │  │  Framework  │  │             │     │
│  │             │  │             │  │             │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **VQ-VAE Component**: Vector Quantized Variational Autoencoder for efficient data representation and generation.
2. **LLM Component**: Large Language Model for natural language understanding, generation, and reasoning.
3. **Model Registry**: Central repository for managing trained AI models.
4. **Inference Engine**: Service for deploying and running AI models for predictions.
5. **Training Service**: Manages the training and fine-tuning of AI models.
6. **Evaluation Service**: Assesses the performance and quality of AI models.
7. **AI Agent Framework**: Provides tools for building and managing AI agents.
8. **AI Protocols**: Implements MCP and A2A for communication with AI components.

## Component Details

### VQ-VAE Component

The VQ-VAE component provides capabilities for:

- **Data Compression**: Learning compact representations of high-dimensional data.
- **Feature Extraction**: Extracting meaningful features from data.
- **Anomaly Detection**: Identifying unusual patterns or outliers.
- **Data Generation**: Generating synthetic data similar to the training data.

#### Code Example: Training and Using a VQ-VAE Model

```python
from industriverse.core_ai.vqvae import VQVAEModel, VQVAETrainer
from industriverse.data.access import DataAccessService

# Access training data from the Data Layer
data_access = DataAccessService()
training_data = data_access.query(
    storage="analytics-db",
    query="SELECT feature1, feature2, feature3 FROM sensor_features WHERE timestamp BETWEEN :start AND :end",
    parameters={
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-04-01T00:00:00Z"
    }
)

# Convert data to appropriate format (e.g., numpy array)
import numpy as np
training_array = np.array([[rec["feature1"], rec["feature2"], rec["feature3"]] for rec in training_data])

# Define VQ-VAE model configuration
model_config = {
    "input_dim": 3,
    "embedding_dim": 64,
    "num_embeddings": 512,
    "hidden_dims": [128, 256],
    "commitment_cost": 0.25
}

# Initialize VQ-VAE model
model = VQVAEModel(config=model_config)

# Initialize trainer
trainer = VQVAETrainer(
    model=model,
    config={
        "epochs": 50,
        "batch_size": 128,
        "learning_rate": 0.001,
        "optimizer": "adam"
    }
)

# Train the model
trained_model, history = trainer.train(training_array)
print("VQ-VAE model training completed.")
print(f"Final Reconstruction Loss: {history['reconstruction_loss'][-1]}")
print(f"Final Quantization Loss: {history['vq_loss'][-1]}")

# Register the trained model
from industriverse.core_ai.registry import ModelRegistry
registry = ModelRegistry()
model_id = registry.register_model(
    model=trained_model,
    name="sensor-feature-vqvae",
    version="1.0.0",
    description="VQ-VAE model for sensor feature representation",
    model_type="vqvae",
    metrics={
        "reconstruction_loss": history["reconstruction_loss"][-1],
        "vq_loss": history["vq_loss"][-1]
    }
)
print(f"Model registered with ID: {model_id}")

# Use the model for encoding (feature extraction)
from industriverse.core_ai.inference import InferenceEngine
inference_engine = InferenceEngine()
inference_engine.load_model(model_id)

# Get new data for encoding
new_data = data_access.query(
    storage="analytics-db",
    query="SELECT feature1, feature2, feature3 FROM sensor_features WHERE timestamp > :start",
    parameters={"start": "2025-04-01T00:00:00Z"}
)
new_array = np.array([[rec["feature1"], rec["feature2"], rec["feature3"]] for rec in new_data])

# Encode the data
encoded_vectors = inference_engine.predict(model_id, new_array, mode="encode")
print(f"Encoded {len(new_array)} data points into vectors of shape: {encoded_vectors.shape}")

# Use the model for reconstruction (anomaly detection)
reconstructed_data = inference_engine.predict(model_id, new_array, mode="reconstruct")
reconstruction_error = np.mean(np.square(new_array - reconstructed_data), axis=1)

# Identify anomalies (high reconstruction error)
anomaly_threshold = np.percentile(reconstruction_error, 95) # Example threshold
anomalies = new_array[reconstruction_error > anomaly_threshold]
print(f"Detected {len(anomalies)} anomalies.")
```

### LLM Component

The LLM component provides functionalities for:

- **Natural Language Understanding (NLU)**: Parsing and interpreting text.
- **Natural Language Generation (NLG)**: Creating human-like text.
- **Question Answering**: Answering questions based on provided context.
- **Summarization**: Condensing large amounts of text.
- **Text Classification**: Categorizing text into predefined classes.
- **Reasoning**: Performing logical deductions based on text.

#### Code Example: Using the LLM for Summarization and Q&A

```python
from industriverse.core_ai.llm import LLMService

# Initialize LLM service
llm_service = LLMService(
    config={
        "provider": "openai", # or "huggingface", "local"
        "model_name": "gpt-4",
        "api_key": "YOUR_API_KEY"
    }
)

# Example text (e.g., maintenance report)
report_text = """
Maintenance Report - Pump-101 - 2025-05-20

Performed routine maintenance on Pump-101. Checked fluid levels, which were within normal ranges. 
Inspected seals and gaskets; minor wear detected on the primary seal, but replacement not yet required. 
Lubricated bearings. Vibration analysis showed a slight increase in the 2x frequency component, 
indicating potential misalignment. Recommend monitoring vibration levels closely over the next month. 
Pressure readings were stable at 31.5 PSI. Temperature readings averaged 88°F. 
Overall, the pump is in good operational condition, but the potential misalignment warrants attention. 
Next scheduled maintenance: 2025-08-20.
"""

# Summarize the report
summary = llm_service.summarize(
    text=report_text,
    max_length=50 # Target summary length in words
)
print("Report Summary:")
print(summary)

# Ask questions about the report
question1 = "Was the primary seal replaced?"
answer1 = llm_service.answer_question(
    context=report_text,
    question=question1
)
print(f"\nQ: {question1}")
print(f"A: {answer1}")

question2 = "What was the main concern identified?"
answer2 = llm_service.answer_question(
    context=report_text,
    question=question2
)
print(f"\nQ: {question2}")
print(f"A: {answer2}")

# Classify the report sentiment
sentiment = llm_service.classify_text(
    text=report_text,
    classes=["positive", "neutral", "negative"]
)
print(f"\nReport Sentiment: {sentiment}")

# Generate a follow-up task description
task_prompt = f"Based on the following maintenance report, generate a brief task description for monitoring the potential misalignment:\n\n{report_text}"
task_description = llm_service.generate_text(
    prompt=task_prompt,
    max_tokens=100
)
print("\nGenerated Task Description:")
print(task_description)
```

### Model Registry

The Model Registry stores and manages trained AI models:

- **Model Versioning**: Tracks different versions of models.
- **Metadata Storage**: Stores information about models (parameters, metrics, etc.).
- **Model Discovery**: Allows searching and retrieving models.
- **Access Control**: Manages permissions for accessing models.
- **Lifecycle Management**: Handles model promotion (dev, staging, prod) and retirement.

#### Code Example: Interacting with the Model Registry

```python
from industriverse.core_ai.registry import ModelRegistry

# Initialize registry
registry = ModelRegistry()

# Register a new version of a model
# Assume `new_trained_model` is a newly trained model object
# Assume `new_history` contains training metrics
new_model_id = registry.register_model(
    model=new_trained_model,
    name="sensor-feature-vqvae", # Same name as previous version
    version="1.1.0",
    description="Updated VQ-VAE model with more training data",
    model_type="vqvae",
    metrics={
        "reconstruction_loss": new_history["reconstruction_loss"][-1],
        "vq_loss": new_history["vq_loss"][-1]
    },
    parent_model_id=model_id # Link to previous version
)
print(f"Registered new model version with ID: {new_model_id}")

# List all versions of a model
versions = registry.list_model_versions(name="sensor-feature-vqvae")
print("\nAvailable versions for sensor-feature-vqvae:")
for version in versions:
    print(f"- Version: {version['version']}")
    print(f"  ID: {version['id']}")
    print(f"  Status: {version['status']}")
    print(f"  Created At: {version['created_at']}")

# Get details of a specific model version
model_details = registry.get_model_details(model_id=new_model_id)
print("\nDetails for model version 1.1.0:")
print(f"Name: {model_details['name']}")
print(f"Version: {model_details['version']}")
print(f"Description: {model_details['description']}")
print(f"Metrics: {model_details['metrics']}")

# Promote a model to production
registry.update_model_status(model_id=new_model_id, status="production")
print(f"\nPromoted model {new_model_id} to production.")

# Retrieve the production model
production_model_info = registry.get_production_model(name="sensor-feature-vqvae")
print(f"\nCurrent production model ID: {production_model_info['id']}")

# Load the production model for inference
production_model = registry.load_model(model_id=production_model_info["id"])
print("Production model loaded successfully.")

# Retire an old model version
registry.update_model_status(model_id=model_id, status="retired") # Retiring version 1.0.0
print(f"\nRetired model {model_id}.")
```

### Inference Engine

The Inference Engine deploys and serves models for real-time predictions:

- **Model Deployment**: Loads models from the registry and makes them available.
- **Scalability**: Handles varying inference loads.
- **Performance Optimization**: Optimizes models for fast inference.
- **Monitoring**: Tracks inference latency, throughput, and error rates.
- **A/B Testing**: Supports deploying multiple model versions for comparison.

#### Code Example: Deploying and Using Models via Inference Engine

```python
from industriverse.core_ai.inference import InferenceEngine

# Initialize inference engine
inference_engine = InferenceEngine(
    config={
        "deployment_strategy": "kubernetes", # or "local", "serverless"
        "autoscaling": {
            "min_replicas": 1,
            "max_replicas": 5,
            "cpu_threshold": 70
        },
        "monitoring": {
            "enabled": True,
            "prometheus_endpoint": "http://prometheus:9090"
        }
    }
)

# Deploy a model from the registry
deployment_id = inference_engine.deploy_model(
    model_id=new_model_id, # Deploying version 1.1.0
    deployment_name="sensor-vqvae-prod",
    resources={
        "requests": {"cpu": "500m", "memory": "1Gi"},
        "limits": {"cpu": "1", "memory": "2Gi"}
    }
)
print(f"Model {new_model_id} deployed with deployment ID: {deployment_id}")

# Get deployment status
status = inference_engine.get_deployment_status(deployment_id)
print(f"Deployment status: {status['state']}")

# Send prediction request (assuming deployment is ready)
# Prepare input data (e.g., new_array from previous example)
prediction_request = {
    "deployment_id": deployment_id,
    "inputs": new_array.tolist(), # Convert numpy array to list for JSON serialization
    "parameters": {
        "mode": "encode" # Specify prediction mode if needed
    }
}

# Use the inference engine client to send request
# (Actual client implementation depends on deployment strategy)
# Example using a hypothetical client:
# client = InferenceClient(inference_engine.get_endpoint(deployment_id))
# predictions = client.predict(prediction_request)

# Example direct call (if running locally or for testing)
predictions = inference_engine.predict(
    deployment_id=deployment_id,
    inputs=new_array,
    parameters={"mode": "encode"}
)
print(f"Received {len(predictions)} predictions from deployment {deployment_id}.")

# Update a deployment (e.g., roll out a new version)
# Assume `newer_model_id` is the ID of version 1.2.0
update_status = inference_engine.update_deployment(
    deployment_id=deployment_id,
    model_id=newer_model_id,
    strategy="canary", # or "blue-green"
    canary_percentage=10
)
print(f"Deployment update initiated: {update_status}")

# Undeploy a model
inference_engine.undeploy_model(deployment_id)
print(f"Undeployed model with deployment ID: {deployment_id}")
```

### Training Service

The Training Service orchestrates the model training process:

- **Data Preparation**: Integrates with the Data Layer to fetch and prepare data.
- **Distributed Training**: Supports training models across multiple nodes.
- **Hyperparameter Tuning**: Automates the search for optimal model parameters.
- **Experiment Tracking**: Logs training parameters, metrics, and artifacts.
- **Resource Management**: Allocates compute resources for training jobs.

#### Code Example: Using the Training Service

```python
from industriverse.core_ai.training import TrainingService, TrainingJob, HyperparameterTuning

# Initialize training service
training_service = TrainingService(
    config={
        "resource_pool": "gpu-cluster",
        "experiment_tracking": "mlflow",
        "mlflow_uri": "http://mlflow:5000"
    }
)

# Define a training job for a VQ-VAE model
job_config = {
    "name": "sensor-vqvae-training",
    "description": "Training VQ-VAE model for sensor data",
    "model_type": "vqvae",
    "model_config": {
        "input_dim": 3,
        "embedding_dim": 64,
        "num_embeddings": 512,
        "hidden_dims": [128, 256],
        "commitment_cost": 0.25
    },
    "training_config": {
        "epochs": 50,
        "batch_size": 128,
        "learning_rate": 0.001,
        "optimizer": "adam"
    },
    "data_config": {
        "source": {
            "type": "database",
            "connection": "analytics-db",
            "query": "SELECT feature1, feature2, feature3 FROM sensor_features WHERE timestamp BETWEEN :start AND :end",
            "parameters": {
                "start": "2025-01-01T00:00:00Z",
                "end": "2025-04-01T00:00:00Z"
            }
        },
        "preprocessing": [
            {"type": "normalize", "fields": ["feature1", "feature2", "feature3"]},
            {"type": "filter_outliers", "fields": ["feature1", "feature2", "feature3"], "method": "iqr"}
        ],
        "validation_split": 0.2
    },
    "resources": {
        "cpu": 4,
        "memory": "16Gi",
        "gpu": 1
    }
}

# Create and submit the training job
training_job = TrainingJob(config=job_config)
job_id = training_service.submit_job(training_job)
print(f"Submitted training job with ID: {job_id}")

# Monitor job status
status = training_service.get_job_status(job_id)
print(f"Job status: {status['state']}")

# Wait for job completion (in a real application, this would be asynchronous)
import time
while status['state'] not in ['completed', 'failed', 'cancelled']:
    time.sleep(30)
    status = training_service.get_job_status(job_id)
    print(f"Job status: {status['state']}, Progress: {status.get('progress', 'N/A')}")

# Get job results
if status['state'] == 'completed':
    results = training_service.get_job_results(job_id)
    print(f"Job completed successfully. Model ID: {results['model_id']}")
    print(f"Final metrics: {results['metrics']}")
    
    # Register the model in the registry
    from industriverse.core_ai.registry import ModelRegistry
    registry = ModelRegistry()
    registry.update_model_metadata(
        model_id=results['model_id'],
        metadata={
            "training_job_id": job_id,
            "training_duration": status['duration'],
            "resource_usage": status['resource_usage']
        }
    )
else:
    print(f"Job failed with error: {status.get('error', 'Unknown error')}")

# Hyperparameter tuning example
tuning_config = {
    "name": "vqvae-hyperparameter-tuning",
    "description": "Tuning hyperparameters for VQ-VAE model",
    "base_job_config": job_config,
    "parameter_space": {
        "model_config.embedding_dim": [32, 64, 128],
        "model_config.num_embeddings": [256, 512, 1024],
        "model_config.commitment_cost": [0.1, 0.25, 0.5],
        "training_config.learning_rate": [0.0001, 0.001, 0.01]
    },
    "optimization_metric": "reconstruction_loss",
    "optimization_goal": "minimize",
    "max_trials": 10,
    "algorithm": "bayesian"
}

# Create and submit the hyperparameter tuning job
tuning_job = HyperparameterTuning(config=tuning_config)
tuning_id = training_service.submit_tuning_job(tuning_job)
print(f"Submitted hyperparameter tuning job with ID: {tuning_id}")

# Get tuning results (assuming job completion)
tuning_results = training_service.get_tuning_results(tuning_id)
print("Best hyperparameters:")
for param, value in tuning_results['best_parameters'].items():
    print(f"  {param}: {value}")
print(f"Best metric value: {tuning_results['best_metric_value']}")
print(f"Best model ID: {tuning_results['best_model_id']}")
```

### Evaluation Service

The Evaluation Service assesses model performance:

- **Metric Calculation**: Computes standard and custom evaluation metrics.
- **Dataset Management**: Uses predefined evaluation datasets.
- **Model Comparison**: Compares the performance of different models or versions.
- **Bias Detection**: Checks for fairness and bias in model predictions.
- **Reporting**: Generates detailed evaluation reports.

#### Code Example: Evaluating and Comparing Models

```python
from industriverse.core_ai.evaluation import EvaluationService, EvaluationJob, ModelComparison

# Initialize evaluation service
evaluation_service = EvaluationService(
    config={
        "default_metrics": ["accuracy", "precision", "recall", "f1", "mse", "mae"],
        "bias_detection": {
            "enabled": True,
            "sensitive_features": ["location", "equipment_type"]
        }
    }
)

# Define an evaluation job for a VQ-VAE model
eval_config = {
    "name": "sensor-vqvae-evaluation",
    "description": "Evaluating VQ-VAE model for sensor data",
    "model_id": new_model_id,  # From previous examples
    "data_config": {
        "source": {
            "type": "database",
            "connection": "analytics-db",
            "query": "SELECT feature1, feature2, feature3, label FROM sensor_features WHERE timestamp > :start",
            "parameters": {
                "start": "2025-04-01T00:00:00Z"
            }
        },
        "preprocessing": [
            {"type": "normalize", "fields": ["feature1", "feature2", "feature3"]},
        ],
        "features": ["feature1", "feature2", "feature3"],
        "target": "label"
    },
    "metrics": [
        {"name": "reconstruction_error", "type": "mse"},
        {"name": "encoding_quality", "type": "custom", "function": "evaluate_encoding_quality"}
    ],
    "resources": {
        "cpu": 2,
        "memory": "8Gi"
    }
}

# Create and submit the evaluation job
evaluation_job = EvaluationJob(config=eval_config)
job_id = evaluation_service.submit_job(evaluation_job)
print(f"Submitted evaluation job with ID: {job_id}")

# Get evaluation results (assuming job completion)
eval_results = evaluation_service.get_job_results(job_id)
print("Evaluation Results:")
for metric, value in eval_results['metrics'].items():
    print(f"  {metric}: {value}")

# Compare multiple model versions
comparison_config = {
    "name": "vqvae-version-comparison",
    "description": "Comparing different versions of VQ-VAE model",
    "models": [
        {"id": model_id, "name": "Version 1.0.0"},
        {"id": new_model_id, "name": "Version 1.1.0"}
    ],
    "data_config": eval_config["data_config"],
    "metrics": eval_config["metrics"]
}

# Create and submit the comparison job
comparison_job = ModelComparison(config=comparison_config)
comparison_id = evaluation_service.submit_comparison_job(comparison_job)
print(f"Submitted model comparison job with ID: {comparison_id}")

# Get comparison results (assuming job completion)
comparison_results = evaluation_service.get_comparison_results(comparison_id)
print("\nModel Comparison Results:")
for model in comparison_results['models']:
    print(f"Model: {model['name']} (ID: {model['id']})")
    for metric, value in model['metrics'].items():
        print(f"  {metric}: {value}")

# Generate a detailed evaluation report
report_config = {
    "title": "VQ-VAE Model Evaluation Report",
    "description": "Comprehensive evaluation of VQ-VAE model versions",
    "evaluation_ids": [job_id],
    "comparison_ids": [comparison_id],
    "format": "pdf",
    "sections": ["summary", "metrics", "visualizations", "recommendations"]
}

report = evaluation_service.generate_report(report_config)
print(f"\nGenerated evaluation report: {report['path']}")

# Perform bias detection
bias_config = {
    "model_id": new_model_id,
    "data_config": {
        "source": {
            "type": "database",
            "connection": "analytics-db",
            "query": "SELECT feature1, feature2, feature3, location, equipment_type FROM sensor_features WHERE timestamp > :start",
            "parameters": {
                "start": "2025-04-01T00:00:00Z"
            }
        }
    },
    "sensitive_features": ["location", "equipment_type"],
    "metrics": ["statistical_parity", "equal_opportunity", "disparate_impact"]
}

bias_results = evaluation_service.detect_bias(bias_config)
print("\nBias Detection Results:")
for feature in bias_results['sensitive_features']:
    print(f"Feature: {feature['name']}")
    for metric, value in feature['metrics'].items():
        print(f"  {metric}: {value}")
    if feature['has_bias']:
        print(f"  Bias detected: {feature['bias_description']}")
```

### AI Agent Framework

The AI Agent Framework enables the creation of autonomous agents:

- **Agent Definition**: Tools for defining agent goals, capabilities, and behaviors.
- **State Management**: Tracks agent state and context.
- **Planning**: Implements planning algorithms for task execution.
- **Tool Usage**: Allows agents to interact with other Industriverse components and external tools.
- **Communication**: Facilitates agent-to-agent communication (A2A).

#### Code Example: Creating and Deploying an AI Agent

```python
from industriverse.core_ai.agent import AgentFramework, Agent, Tool, Plan

# Initialize agent framework
agent_framework = AgentFramework(
    config={
        "default_planner": "hierarchical",
        "max_concurrent_agents": 50
    }
)

# Define tools that the agent can use
tools = [
    Tool(
        name="query_data",
        description="Query data from the Data Layer",
        function="query_data_function",
        parameters=[
            {"name": "query", "type": "string", "description": "SQL query to execute"},
            {"name": "parameters", "type": "object", "description": "Query parameters"}
        ],
        returns={"type": "array", "description": "Query results"}
    ),
    Tool(
        name="analyze_telemetry",
        description="Analyze equipment telemetry data",
        function="analyze_telemetry_function",
        parameters=[
            {"name": "equipment_id", "type": "string", "description": "Equipment ID"},
            {"name": "time_range", "type": "object", "description": "Time range for analysis"}
        ],
        returns={"type": "object", "description": "Analysis results"}
    ),
    Tool(
        name="generate_report",
        description="Generate a report based on analysis",
        function="generate_report_function",
        parameters=[
            {"name": "analysis_results", "type": "object", "description": "Analysis results"},
            {"name": "report_type", "type": "string", "description": "Type of report to generate"}
        ],
        returns={"type": "string", "description": "Report content"}
    )
]

# Register tool implementations
def query_data_function(query, parameters):
    from industriverse.data.access import DataAccessService
    data_access = DataAccessService()
    return data_access.query(
        storage="analytics-db",
        query=query,
        parameters=parameters
    )

def analyze_telemetry_function(equipment_id, time_range):
    # Implementation of telemetry analysis
    # ...
    return {"status": "normal", "anomalies": [], "metrics": {"efficiency": 0.92}}

def generate_report_function(analysis_results, report_type):
    # Implementation of report generation
    # ...
    return f"Report for equipment {analysis_results['equipment_id']}: Status {analysis_results['status']}"

# Register the tools with the framework
for tool in tools:
    if tool.name == "query_data":
        agent_framework.register_tool(tool, query_data_function)
    elif tool.name == "analyze_telemetry":
        agent_framework.register_tool(tool, analyze_telemetry_function)
    elif tool.name == "generate_report":
        agent_framework.register_tool(tool, generate_report_function)

# Define an agent
agent_config = {
    "name": "equipment-monitoring-agent",
    "description": "Agent for monitoring equipment health and generating reports",
    "version": "1.0.0",
    "tools": ["query_data", "analyze_telemetry", "generate_report"],
    "capabilities": [
        {
            "name": "monitor_equipment",
            "description": "Monitor equipment health and generate reports",
            "parameters": [
                {"name": "equipment_id", "type": "string", "description": "Equipment ID"},
                {"name": "report_type", "type": "string", "description": "Type of report to generate"}
            ],
            "returns": {"type": "string", "description": "Report content"}
        }
    ],
    "planning": {
        "type": "hierarchical",
        "max_steps": 10
    },
    "state": {
        "persistence": True,
        "ttl": 3600 # Time to live in seconds
    }
}

# Create the agent
agent = Agent(config=agent_config)

# Register the agent with the framework
agent_id = agent_framework.register_agent(agent)
print(f"Registered agent with ID: {agent_id}")

# Define the agent's behavior for the monitor_equipment capability
@agent.capability("monitor_equipment")
def monitor_equipment(equipment_id, report_type):
    # Create a plan
    plan = Plan()
    
    # Step 1: Query equipment data
    plan.add_step(
        name="query_equipment_data",
        tool="query_data",
        parameters={
            "query": "SELECT timestamp, temperature, pressure, vibration FROM equipment_telemetry WHERE equipment_id = :equipment_id AND timestamp > :start",
            "parameters": {
                "equipment_id": equipment_id,
                "start": "NOW() - INTERVAL '24 HOURS'"
            }
        }
    )
    
    # Step 2: Analyze telemetry
    plan.add_step(
        name="analyze_equipment_telemetry",
        tool="analyze_telemetry",
        parameters={
            "equipment_id": equipment_id,
            "time_range": {"start": "NOW() - INTERVAL '24 HOURS'", "end": "NOW()"}
        },
        depends_on=["query_equipment_data"]
    )
    
    # Step 3: Generate report
    plan.add_step(
        name="generate_equipment_report",
        tool="generate_report",
        parameters={
            "analysis_results": {"$ref": "analyze_equipment_telemetry.result"},
            "report_type": report_type
        },
        depends_on=["analyze_equipment_telemetry"]
    )
    
    # Execute the plan
    result = plan.execute()
    
    # Return the final result
    return result["generate_equipment_report"]

# Deploy the agent
deployment_id = agent_framework.deploy_agent(agent_id)
print(f"Deployed agent with deployment ID: {deployment_id}")

# Invoke the agent's capability
result = agent_framework.invoke_capability(
    agent_id=agent_id,
    capability="monitor_equipment",
    parameters={
        "equipment_id": "pump-101",
        "report_type": "health"
    }
)
print(f"Agent result: {result}")
```

### AI Protocols

Implements MCP and A2A for seamless communication:

- **MCP Adapter**: Handles internal communication between AI components.
- **A2A Adapter**: Manages external communication with other agents and systems.
- **Standardized Payloads**: Defines common message formats.

#### Code Example: Implementing Protocol Integration

```python
from industriverse.core_ai.protocols import MCPAdapter, A2AAdapter, EventBus

# Initialize protocol adapters
mcp_adapter = MCPAdapter(
    config={
        "service_name": "core-ai",
        "service_version": "1.0.0",
        "endpoint": "http://mcp-broker:8080"
    }
)

a2a_adapter = A2AAdapter(
    config={
        "agent_name": "core-ai-agent",
        "agent_version": "1.0.0",
        "endpoint": "http://a2a-broker:8080"
    }
)

# Initialize event bus
event_bus = EventBus()

# Register event handlers
@event_bus.subscribe("core-ai.model.trained")
def handle_model_trained(event):
    print(f"Model trained: {event['model_id']} at {event['timestamp']}")
    print(f"Metrics: {event['metrics']}")
    
    # Publish event to MCP
    mcp_adapter.publish_event(
        event_type="core-ai.model.trained",
        payload={
            "model_id": event["model_id"],
            "timestamp": event["timestamp"],
            "metrics": event["metrics"]
        }
    )
    
    # Publish capability to A2A
    a2a_adapter.publish_capability(
        capability={
            "name": "core-ai.inference",
            "description": "Run inference using trained AI model",
            "parameters": {
                "model_id": {
                    "type": "string",
                    "description": "Model ID"
                },
                "inputs": {
                    "type": "array",
                    "description": "Input data for inference"
                }
            },
            "returns": {
                "type": "array",
                "description": "Inference results"
            }
        }
    )

@event_bus.subscribe("core-ai.inference.completed")
def handle_inference_completed(event):
    print(f"Inference completed: {event['request_id']}")
    print(f"Model: {event['model_id']}")
    print(f"Duration: {event['duration']} ms")
    
    # Publish event to MCP
    mcp_adapter.publish_event(
        event_type="core-ai.inference.completed",
        payload={
            "request_id": event["request_id"],
            "model_id": event["model_id"],
            "duration": event["duration"],
            "timestamp": event["timestamp"]
        }
    )

# Register MCP handlers
@mcp_adapter.handle("core-ai.model.request")
def handle_model_request(request):
    print(f"Received model request via MCP: {request}")
    
    # Process the request
    from industriverse.core_ai.registry import ModelRegistry
    
    registry = ModelRegistry()
    model = registry.load_model(model_id=request["model_id"])
    
    # Return the model metadata
    return {
        "status": "success",
        "model_metadata": registry.get_model_details(model_id=request["model_id"])
    }

# Register A2A handlers
@a2a_adapter.handle("core-ai.inference")
def handle_a2a_inference(request):
    print(f"Received inference request via A2A: {request}")
    
    # Process the inference request
    from industriverse.core_ai.inference import InferenceEngine
    
    inference_engine = InferenceEngine()
    result = inference_engine.predict(
        model_id=request["model_id"],
        inputs=request["inputs"],
        parameters=request.get("parameters", {})
    )
    
    # Return the result
    return {
        "status": "success",
        "result": result
    }

# Start the adapters
mcp_adapter.start()
a2a_adapter.start()

# Publish an event
event_bus.publish(
    event_type="core-ai.model.trained",
    payload={
        "model_id": "model-123",
        "timestamp": "2025-05-26T15:00:00Z",
        "metrics": {
            "accuracy": 0.95,
            "loss": 0.05
        }
    }
)
```

## Integration with Other Layers

### Data Layer Integration

- Fetches training, evaluation, and inference data.
- Stores trained models, metadata, and evaluation results.
- Provides data features required by AI models.

```python
from industriverse.core_ai.integration import DataLayerIntegration

# Initialize Data Layer integration
data_integration = DataLayerIntegration()

# Fetch training data
training_data = data_integration.fetch_training_data(
    source="equipment-telemetry",
    features=["temperature", "pressure", "vibration"],
    time_range={
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-04-01T00:00:00Z"
    },
    preprocessing=[
        {"type": "normalize", "fields": ["temperature", "pressure", "vibration"]},
        {"type": "filter_outliers", "fields": ["temperature", "pressure", "vibration"], "method": "iqr"}
    ]
)

# Train a model using the data
from industriverse.core_ai.vqvae import VQVAEModel, VQVAETrainer

model = VQVAEModel(config={
    "input_dim": len(training_data["features"]),
    "embedding_dim": 64,
    "num_embeddings": 512,
    "hidden_dims": [128, 256],
    "commitment_cost": 0.25
})

trainer = VQVAETrainer(
    model=model,
    config={
        "epochs": 50,
        "batch_size": 128,
        "learning_rate": 0.001,
        "optimizer": "adam"
    }
)

trained_model, history = trainer.train(training_data["data"])

# Store model metadata in Data Layer
model_metadata = {
    "name": "equipment-telemetry-vqvae",
    "version": "1.0.0",
    "description": "VQ-VAE model for equipment telemetry",
    "features": training_data["features"],
    "metrics": {
        "reconstruction_loss": history["reconstruction_loss"][-1],
        "vq_loss": history["vq_loss"][-1]
    },
    "training_parameters": {
        "epochs": 50,
        "batch_size": 128,
        "learning_rate": 0.001,
        "optimizer": "adam"
    },
    "created_at": "2025-05-26T15:00:00Z"
}

data_integration.store_model_metadata(model_metadata)

# Set up real-time data processing pipeline
pipeline_config = {
    "name": "telemetry-anomaly-detection",
    "description": "Real-time anomaly detection for equipment telemetry",
    "source": "equipment-telemetry-stream",
    "model_id": trained_model.id,
    "preprocessing": [
        {"type": "normalize", "fields": ["temperature", "pressure", "vibration"]}
    ],
    "postprocessing": [
        {"type": "threshold", "field": "reconstruction_error", "threshold": 0.1, "output_field": "is_anomaly"}
    ],
    "output": {
        "type": "stream",
        "name": "equipment-anomalies"
    }
}

data_integration.create_processing_pipeline(pipeline_config)
```

### Generative Layer Integration

- LLMs can be used to generate code, UI components, or documentation templates.
- VQ-VAE can provide embeddings for generative tasks.

```python
from industriverse.core_ai.integration import GenerativeLayerIntegration

# Initialize Generative Layer integration
generative_integration = GenerativeLayerIntegration()

# Use LLM to generate code template
code_template = generative_integration.generate_code_template(
    description="Data processing pipeline for equipment telemetry",
    language="python",
    framework="industriverse",
    parameters={
        "data_source": "equipment-telemetry",
        "processing_steps": ["normalization", "outlier_detection", "feature_extraction"],
        "output": "processed-telemetry"
    }
)

print("Generated Code Template:")
print(code_template)

# Use VQ-VAE for UI component generation
ui_component = generative_integration.generate_ui_component(
    component_type="dashboard-widget",
    data_source="equipment-telemetry",
    model_id=trained_model.id,
    parameters={
        "title": "Equipment Health Monitor",
        "metrics": ["temperature", "pressure", "vibration", "health_score"],
        "visualization": "gauge",
        "refresh_interval": 5
    }
)

print("\nGenerated UI Component:")
print(ui_component)

# Use LLM to generate documentation
documentation = generative_integration.generate_documentation(
    subject="Equipment Telemetry Analysis",
    content_type="user-guide",
    sections=["overview", "data-sources", "analysis-methods", "interpretation", "troubleshooting"],
    parameters={
        "audience": "operators",
        "technical_level": "intermediate",
        "include_examples": True
    }
)

print("\nGenerated Documentation:")
print(documentation[:500] + "...") # Truncated for brevity
```

### Application Layer Integration

- Provides AI models and inference capabilities to applications.
- AI agents can automate tasks within applications.
- LLMs can power conversational interfaces in applications.

```python
from industriverse.core_ai.integration import ApplicationLayerIntegration

# Initialize Application Layer integration
app_integration = ApplicationLayerIntegration()

# Register AI models with an application
app_integration.register_models(
    application_id="equipment-monitoring-app",
    models=[
        {
            "model_id": trained_model.id,
            "name": "equipment-telemetry-vqvae",
            "description": "VQ-VAE model for equipment telemetry analysis",
            "capabilities": ["anomaly-detection", "feature-extraction"],
            "access_level": "read"
        }
    ]
)

# Create an AI-powered feature for an application
feature_config = {
    "name": "predictive-maintenance",
    "description": "Predictive maintenance recommendations based on telemetry analysis",
    "models": [
        {"model_id": trained_model.id, "role": "anomaly-detection"},
        {"model_id": "maintenance-prediction-model", "role": "prediction"}
    ],
    "data_sources": [
        {"name": "equipment-telemetry", "access": "read"},
        {"name": "maintenance-history", "access": "read"},
        {"name": "maintenance-recommendations", "access": "write"}
    ],
    "ui_components": [
        {"type": "dashboard-widget", "name": "maintenance-forecast"},
        {"type": "alert-notification", "name": "maintenance-alert"}
    ],
    "workflow": {
        "trigger": "schedule",
        "schedule": "0 */6 * * *", # Every 6 hours
        "steps": [
            {"name": "fetch-telemetry", "type": "data-query"},
            {"name": "detect-anomalies", "type": "model-inference"},
            {"name": "predict-maintenance", "type": "model-inference"},
            {"name": "generate-recommendations", "type": "data-processing"},
            {"name": "store-recommendations", "type": "data-write"},
            {"name": "notify-users", "type": "notification", "condition": "has_critical_recommendations"}
        ]
    }
}

app_integration.create_ai_feature(
    application_id="equipment-monitoring-app",
    feature_config=feature_config
)

# Set up a conversational interface for an application
conversation_config = {
    "name": "maintenance-assistant",
    "description": "Conversational assistant for maintenance queries",
    "model_id": "maintenance-llm-model",
    "knowledge_sources": [
        {"name": "equipment-manuals", "type": "document"},
        {"name": "maintenance-procedures", "type": "document"},
        {"name": "equipment-telemetry", "type": "data-source"},
        {"name": "maintenance-history", "type": "data-source"}
    ],
    "capabilities": [
        {"name": "answer-questions", "description": "Answer questions about equipment and maintenance"},
        {"name": "explain-alerts", "description": "Explain maintenance alerts and recommendations"},
        {"name": "guide-procedures", "description": "Guide through maintenance procedures"}
    ],
    "ui_config": {
        "type": "chat-interface",
        "position": "sidebar",
        "default_greeting": "How can I help with equipment maintenance today?"
    }
}

app_integration.create_conversational_interface(
    application_id="equipment-monitoring-app",
    conversation_config=conversation_config
)
```

### Protocol Layer Integration

- Uses MCP and A2A for communication.
- Registers AI capabilities and models with protocol registries.

```python
from industriverse.core_ai.integration import ProtocolLayerIntegration

# Initialize Protocol Layer integration
protocol_integration = ProtocolLayerIntegration()

# Register AI capabilities with the Protocol Layer
protocol_integration.register_capabilities(
    capabilities=[
        {
            "name": "core-ai.vqvae.encode",
            "description": "Encode data using VQ-VAE model",
            "parameters": {
                "model_id": {
                    "type": "string",
                    "description": "Model ID"
                },
                "data": {
                    "type": "array",
                    "description": "Data to encode"
                }
            },
            "returns": {
                "type": "array",
                "description": "Encoded vectors"
            }
        },
        {
            "name": "core-ai.vqvae.decode",
            "description": "Decode vectors using VQ-VAE model",
            "parameters": {
                "model_id": {
                    "type": "string",
                    "description": "Model ID"
                },
                "vectors": {
                    "type": "array",
                    "description": "Vectors to decode"
                }
            },
            "returns": {
                "type": "array",
                "description": "Decoded data"
            }
        },
        {
            "name": "core-ai.llm.generate",
            "description": "Generate text using LLM",
            "parameters": {
                "prompt": {
                    "type": "string",
                    "description": "Text prompt"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum number of tokens to generate"
                }
            },
            "returns": {
                "type": "string",
                "description": "Generated text"
            }
        }
    ]
)

# Set up protocol translation for external AI systems
protocol_integration.configure_translation(
    source_protocol="openai",
    target_protocol="mcp",
    mapping={
        "endpoint_mapping": {
            "/v1/completions": "core-ai.llm.generate",
            "/v1/embeddings": "core-ai.vqvae.encode"
        },
        "parameter_mapping": {
            "core-ai.llm.generate": {
                "prompt": "$.prompt",
                "max_tokens": "$.max_tokens"
            },
            "core-ai.vqvae.encode": {
                "model_id": "vqvae-default",
                "data": "$.input"
            }
        },
        "response_mapping": {
            "core-ai.llm.generate": {
                "id": "request-{uuid}",
                "object": "text_completion",
                "created": "{timestamp}",
                "model": "industriverse-llm",
                "choices": [
                    {
                        "text": "$.result",
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ]
            },
            "core-ai.vqvae.encode": {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": "$.result",
                        "index": 0
                    }
                ],
                "model": "industriverse-vqvae"
            }
        }
    }
)

# Register AI models with the A2A registry
protocol_integration.register_a2a_models(
    models=[
        {
            "model_id": trained_model.id,
            "name": "equipment-telemetry-vqvae",
            "description": "VQ-VAE model for equipment telemetry analysis",
            "capabilities": ["anomaly-detection", "feature-extraction"],
            "metadata": {
                "input_format": "json",
                "output_format": "json",
                "latency": "low",
                "industry_tags": ["manufacturing", "energy"]
            }
        }
    ]
)
```

### Overseer System Integration

- Provides AI-driven insights and predictions to the Overseer.
- AI agents can be managed and orchestrated by the Overseer.
- Models can analyze system-wide data for monitoring and optimization.

```python
from industriverse.core_ai.integration import OverseerIntegration

# Initialize Overseer integration
overseer_integration = OverseerIntegration()

# Register AI models with the Overseer
overseer_integration.register_models(
    models=[
        {
            "model_id": trained_model.id,
            "name": "equipment-telemetry-vqvae",
            "description": "VQ-VAE model for equipment telemetry analysis",
            "capabilities": ["anomaly-detection", "feature-extraction"],
            "monitoring_config": {
                "performance_metrics": ["latency", "throughput", "error_rate"],
                "quality_metrics": ["reconstruction_error", "anomaly_precision", "anomaly_recall"],
                "alerting": {
                    "error_rate_threshold": 0.01,
                    "latency_threshold": 100, # ms
                    "quality_degradation_threshold": 0.1
                }
            }
        }
    ]
)

# Create an AI-driven Overseer dashboard
dashboard_config = {
    "name": "ai-performance-dashboard",
    "description": "Dashboard for monitoring AI model performance",
    "refresh_interval": 60, # seconds
    "widgets": [
        {
            "name": "model-performance",
            "type": "line-chart",
            "title": "Model Performance Metrics",
            "data_source": "ai-metrics",
            "metrics": ["latency", "throughput", "error_rate"],
            "time_range": "last_24h"
        },
        {
            "name": "model-quality",
            "type": "line-chart",
            "title": "Model Quality Metrics",
            "data_source": "ai-metrics",
            "metrics": ["reconstruction_error", "anomaly_precision", "anomaly_recall"],
            "time_range": "last_24h"
        },
        {
            "name": "model-alerts",
            "type": "alert-list",
            "title": "Model Alerts",
            "data_source": "ai-alerts",
            "time_range": "last_24h"
        },
        {
            "name": "model-recommendations",
            "type": "recommendation-list",
            "title": "Model Optimization Recommendations",
            "data_source": "ai-recommendations",
            "time_range": "last_24h"
        }
    ]
}

overseer_integration.create_dashboard(dashboard_config)

# Set up AI-driven system optimization
optimization_config = {
    "name": "ai-system-optimization",
    "description": "AI-driven optimization of system resources",
    "optimization_targets": [
        {
            "name": "inference-latency",
            "description": "Optimize inference latency",
            "metrics": ["p95_latency", "p99_latency"],
            "goal": "minimize"
        },
        {
            "name": "resource-utilization",
            "description": "Optimize resource utilization",
            "metrics": ["cpu_utilization", "memory_utilization", "gpu_utilization"],
            "goal": "maximize"
        },
        {
            "name": "cost-efficiency",
            "description": "Optimize cost efficiency",
            "metrics": ["cost_per_inference", "cost_per_training"],
            "goal": "minimize"
        }
    ],
    "optimization_strategy": {
        "algorithm": "bayesian",
        "parameters": {
            "inference_engine.batch_size": {"min": 1, "max": 64},
            "inference_engine.num_workers": {"min": 1, "max": 8},
            "inference_engine.cache_size": {"min": 100, "max": 10000},
            "model.quantization": {"options": ["none", "int8", "fp16"]}
        },
        "constraints": [
            {"metric": "accuracy", "operator": ">=", "value": 0.95},
            {"metric": "p99_latency", "operator": "<=", "value": 100} # ms
        ]
    },
    "schedule": {
        "type": "cron",
        "expression": "0 0 * * 0" # Weekly on Sunday at midnight
    }
}

overseer_integration.create_optimization_job(optimization_config)
```

## Deployment and Configuration

### Manifest Configuration

```yaml
apiVersion: industriverse.io/v1
kind: Layer
metadata:
  name: core-ai-layer
  version: 1.0.0
spec:
  type: core-ai
  enabled: true
  components:
    - name: vqvae-service
      version: 1.0.0
      enabled: true
      config:
        default_model: "sensor-feature-vqvae"
        supported_modes: ["encode", "decode", "reconstruct"]
    - name: llm-service
      version: 1.0.0
      enabled: true
      config:
        provider: "openai"
        model_name: "gpt-4"
        api_key_secret: "openai-api-key"
        rate_limit: 100 # requests per minute
    - name: model-registry
      version: 1.0.0
      enabled: true
      config:
        storage:
          type: "database"
          connection_ref: "core-ai-db"
        access_control:
          enabled: true
          policy_source: "security-layer"
    - name: inference-engine
      version: 1.0.0
      enabled: true
      config:
        deployment_strategy: "kubernetes"
        autoscaling:
          min_replicas: 1
          max_replicas: 5
          cpu_threshold: 70
    - name: training-service
      version: 1.0.0
      enabled: true
      config:
        resource_pool: "gpu-cluster"
        experiment_tracking: "mlflow"
        mlflow_uri: "http://mlflow:5000"
    - name: evaluation-service
      version: 1.0.0
      enabled: true
      config:
        default_metrics: ["accuracy", "precision", "recall", "f1", "mse", "mae"]
        bias_detection:
          enabled: true
          sensitive_features: ["location", "equipment_type"]
    - name: ai-agent-framework
      version: 1.0.0
      enabled: true
      config:
        default_planner: "hierarchical"
        max_concurrent_agents: 50
    - name: ai-protocols
      version: 1.0.0
      enabled: true
      config:
        mcp:
          enabled: true
          service_name: core-ai
          service_version: 1.0.0
          endpoint: http://mcp-broker:8080
        a2a:
          enabled: true
          agent_name: core-ai-agent
          agent_version: 1.0.0
          endpoint: http://a2a-broker:8080
  
  integrations:
    - layer: data
      enabled: true
      config:
        data_access:
          enabled: true
          mode: read-write
    - layer: protocol
      enabled: true
      config:
        capability_registry:
          enabled: true
    - layer: security
      enabled: true
      config:
        access_control:
          enabled: true
```

### Kubernetes Deployment

Deployment involves setting up services for each component (Registry, Inference, Training, etc.) often using dedicated Kubernetes operators or Helm charts.

```yaml
# Example Deployment for Inference Engine (Simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-ai-inference-engine
  namespace: industriverse
spec:
  replicas: 1 # Managed by HPA
  selector:
    matchLabels:
      app: core-ai-inference-engine
  template:
    metadata:
      labels:
        app: core-ai-inference-engine
    spec:
      containers:
      - name: inference-engine
        image: industriverse/core-ai-inference:1.0.0
        ports:
        - containerPort: 8080
          name: inference-api
        env:
        - name: MODEL_REGISTRY_URI
          value: "http://core-ai-model-registry:8080"
        - name: DEPLOYMENT_STRATEGY
          value: "kubernetes"
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: core-ai-inference-engine
  namespace: industriverse
spec:
  selector:
    app: core-ai-inference-engine
  ports:
  - name: inference-api
    port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-ai-inference-engine-hpa
  namespace: industriverse
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: core-ai-inference-engine
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Best Practices

1. **Model Versioning**: Always version your models and track their lineage.
2. **Experiment Tracking**: Log all training experiments, parameters, and results.
3. **Continuous Evaluation**: Regularly evaluate models in production against new data.
4. **Monitoring**: Monitor model performance (latency, throughput, accuracy) and resource usage.
5. **Responsible AI**: Implement fairness checks, explainability methods, and bias mitigation.
6. **Security**: Secure models, data, and API endpoints.
7. **Optimization**: Optimize models for inference speed and resource efficiency.
8. **Documentation**: Document model purpose, usage, limitations, and performance.

## Troubleshooting

- **Model Training Issues**: Check data quality, hyperparameters, resource allocation.
- **Inference Errors**: Verify model compatibility, input data format, deployment status.
- **Performance Degradation**: Monitor for data drift, concept drift; retrain or fine-tune models.
- **Integration Problems**: Check protocol configurations, network connectivity, API keys.

## Next Steps

- Explore the [Generative Layer Guide](04_generative_layer_guide.md) for using AI in generation tasks.
- See the [Application Layer Guide](05_application_layer_guide.md) for integrating AI into applications.
- Consult the [Overseer System Guide](11_overseer_system_guide.md) for AI-driven monitoring.

## Related Guides

- [Data Layer Guide](02_data_layer_guide.md)
- [Protocol Layer Guide](06_protocol_layer_guide.md)
- [Security & Compliance Layer Guide](09_security_compliance_layer_guide.md)
- [Integration Guide](12_integration_guide.md)
