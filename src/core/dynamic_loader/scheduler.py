import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass, field
import uuid

@dataclass
class InferenceRequest:
    request_id: str
    model_name: str
    prompt: str
    priority: int = 1
    created_at: float = 0.0

class TokenScheduler:
    """
    Prototype Token-Level Scheduler.
    Slices inference into micro-batches to allow preemption.
    """
    def __init__(self, time_slice_ms: int = 50):
        self.time_slice_ms = time_slice_ms
        self.queue: List[InferenceRequest] = []
        self.running = False

    async def submit_request(self, model_name: str, prompt: str, priority: int = 1) -> str:
        req_id = str(uuid.uuid4())
        req = InferenceRequest(
            request_id=req_id,
            model_name=model_name,
            prompt=prompt,
            priority=priority
        )
        self.queue.append(req)
        # Sort by priority (higher is better)
        self.queue.sort(key=lambda x: x.priority, reverse=True)
        print(f"Scheduler: Request {req_id} queued for {model_name}. Queue size: {len(self.queue)}")
        return req_id

    async def start_loop(self):
        self.running = True
        print("Scheduler: Loop started.")
        while self.running:
            if self.queue:
                # Round-robin or Priority processing
                # For prototype, pick top priority
                req = self.queue[0] # Peek
                
                # Simulate processing a "slice" of tokens
                print(f"Scheduler: Processing slice for {req.request_id} ({req.model_name})...")
                await asyncio.sleep(self.time_slice_ms / 1000.0)
                
                # Simulate completion chance
                import random
                if random.random() > 0.7:
                    print(f"Scheduler: Request {req.request_id} completed.")
                    self.queue.pop(0)
                else:
                    print(f"Scheduler: Request {req.request_id} preempted/yielded.")
                    # Rotate to back if equal priority (simple RR)
                    # self.queue.append(self.queue.pop(0)) 
            
            await asyncio.sleep(0.01)

    def stop(self):
        self.running = False
        print("Scheduler: Stopped.")
