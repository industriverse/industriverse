import kopf
import logging


@kopf.on.create("proofscores")
def create_proofscore(spec, name, namespace, **kwargs):
    utid = spec.get("utid")
    proof_hash = spec.get("proofHash")
    proof_score = spec.get("proofScore", 0)
    logging.info(f"ProofScore created {name} ns={namespace} utid={utid} proof_hash={proof_hash} score={proof_score}")
    return {"status": "observed"}


@kopf.on.update("proofscores")
def update_proofscore(spec, name, namespace, **kwargs):
    utid = spec.get("utid")
    proof_hash = spec.get("proofHash")
    proof_score = spec.get("proofScore", 0)
    logging.info(f"ProofScore updated {name} ns={namespace} utid={utid} proof_hash={proof_hash} score={proof_score}")
    return {"status": "updated"}
