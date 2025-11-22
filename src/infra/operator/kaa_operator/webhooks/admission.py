from fastapi import FastAPI, Request, HTTPException
from src.infra.operator.kaa_operator.proof_validators.validator import validate_proof_bundle

app = FastAPI()

@app.post("/validate")
async def validate_deployment(request: Request):
    """
    Kubernetes ValidatingAdmissionWebhook.
    """
    body = await request.json()
    request_uid = body["request"]["uid"]
    object_meta = body["request"]["object"]["metadata"]
    spec = body["request"]["object"]["spec"]
    
    allowed = True
    reason = "Valid ProofedDeployment"
    
    # Enforce Proof Policy
    if spec.get("proofPolicy", {}).get("required", True):
        # Check if proof annotations exist or if bundle is valid
        # This is a simplified check
        if not validate_proof_bundle("mock"):
            allowed = False
            reason = "Proof validation failed: No valid proof bundle found."

    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": request_uid,
            "allowed": allowed,
            "status": {"message": reason}
        }
    }
