"""
UTID generation & lineage helper.
UTID contains:
 - uuid
 - domain tag
 - digest of hypothesis (sha256)
 - timestamp
 - optional signature (future)
"""

import hashlib
import time
import uuid

def make_utid(candidate: dict):
    uid = str(uuid.uuid4())
    ts = int(time.time())
    h = hashlib.sha256(candidate['text'].encode('utf-8')).hexdigest()[:16]
    domain = candidate.get('dataset', candidate.get('domain', 'unknown'))
    utid = f"utid:{domain}:{ts}:{h}:{uid}"
    return utid

def utid_digest(utid: str):
    return hashlib.sha256(utid.encode()).hexdigest()
