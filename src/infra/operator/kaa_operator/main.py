import kopf
import asyncio
# Import controllers to register handlers
import src.infra.operator.kaa_operator.controllers.deployment_controller
import src.infra.operator.kaa_operator.controllers.proofscore_controller
import src.infra.operator.kaa_operator.controllers.admission_controller

if __name__ == "__main__":
    # This entry point allows running the operator via `python -m src.infra.operator.kaa_operator.main`
    # But typically kopf is run via `kopf run ...`
    kopf.run()
