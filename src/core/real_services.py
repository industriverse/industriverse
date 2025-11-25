import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RealOBMIClient:
    """
    Client for the real OBMI service at 34.118.237.8:9900.
    """
    def __init__(self, base_url: str = "http://34.118.237.8:9900"):
        self.base_url = base_url

    async def validate_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send hypothesis to OBMI for validation (PRIN score).
        """
        url = f"{self.base_url}/v1/obmi/validate"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=hypothesis, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"OBMI Error: {resp.status} - {await resp.text()}")
                        return {"prin_score": 0.0, "status": "error"}
        except Exception as e:
            logger.error(f"OBMI Connection Failed: {e}")
            return {"prin_score": 0.0, "status": "connection_error"}

class RealUserLMClient:
    """
    Client for the real UserLM service at localhost:8000.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate response from UserLM.
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": "userlm-8b",
            "messages": [
                {"role": "system", "content": json.dumps(context)},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"UserLM Error: {resp.status} - {await resp.text()}")
                        return " [UserLM Error]"
        except Exception as e:
            logger.error(f"UserLM Connection Failed: {e}")
            return " [UserLM Connection Failed]"
