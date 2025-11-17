# Industriverse Python SDK

Official Python SDK for Industriverse - Deploy Anywhere Capsules (DACs) with thermodynamic computing.

## Features

- ✅ **Thermal Sampler**: Energy-based optimization
- ✅ **World Model**: Physics-based simulation using JAX
- ✅ **Simulated Snapshot**: Sim/real calibration
- ✅ **MicroAdapt Edge**: Self-evolutionary adaptive modeling
- ✅ **DAC Management**: Deploy Anywhere Capsule lifecycle
- ✅ **Async/await**: Full async support with httpx
- ✅ **Type hints**: Complete type annotations
- ✅ **Pydantic models**: Type-safe data validation

## Installation

```bash
pip install industriverse-sdk
```

## Quick Start

```python
import asyncio
from industriverse_sdk import IndustriverseClient

async def main():
    async with IndustriverseClient(api_key="your-api-key") as client:
        # Thermal optimization
        result = await client.thermal.sample(
            problem_type="tsp",
            variables=10,
            num_samples=100
        )
        print(f"Best energy: {result.best_energy}")
        
        # MicroAdapt forecasting
        await client.micro_adapt.update(
            timestamp=1234567890.0,
            value=42.5
        )
        
        forecast = await client.micro_adapt.forecast(horizon=24)
        print(f"Predictions: {forecast.predictions}")

asyncio.run(main())
```

## Examples

### Thermal Sampler

```python
from industriverse_sdk import IndustriverseClient, Constraint

async with IndustriverseClient(api_key="your-api-key") as client:
    result = await client.thermal.sample(
        problem_type="tsp",
        variables=20,
        constraints=[
            Constraint(type="distance", expression="total < 1000")
        ],
        num_samples=500,
        temperature=0.5
    )
    
    print(f"Best route: {result.best_sample}")
    print(f"Best energy: {result.best_energy}")
```

### World Model

```python
async with IndustriverseClient(api_key="your-api-key") as client:
    # Simulation
    sim_result = await client.world_model.simulate(
        domain="resist",
        initial_state=[1.0, 0.0, 0.0],
        parameters={"diffusion_coeff": 0.1},
        time_steps=100
    )
    
    print(f"Final state: {sim_result.final_state}")
    
    # Rollout
    rollout = await client.world_model.rollout(
        domain="plasma",
        initial_state=[1.0, 0.0],
        actions=[[0.1], [0.2], [0.15]],
        horizon=50
    )
    
    print(f"Predictions: {rollout.predictions}")
```

### MicroAdapt Edge

```python
import time

async with IndustriverseClient(api_key="your-api-key") as client:
    # Stream updates
    for i in range(100):
        await client.micro_adapt.update(
            timestamp=time.time(),
            value=42.5 + i * 0.1
        )
    
    # Forecast
    forecast = await client.micro_adapt.forecast(horizon=24)
    print(f"24-hour forecast: {forecast.predictions}")
    
    # Regime info
    regime = await client.micro_adapt.regime()
    print(f"Current regime: {regime.current_regime}")
```

## Documentation

Full API documentation: https://docs.industriverse.io/python

## License

MIT License
