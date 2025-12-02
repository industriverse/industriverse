from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time
import random

@dataclass
class LogEntry:
    term: int
    command: str

class RaftNode:
    """
    A Consensus Node implementing the Raft Protocol.
    """
    
    def __init__(self, node_id: str, peers: List['RaftNode']):
        self.id = node_id
        self.peers = peers
        
        # Persistent State
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        
        # Volatile State
        self.state = "FOLLOWER" # FOLLOWER, CANDIDATE, LEADER
        self.commit_index = 0
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(0.15, 0.30)
        
        print(f"   🗳️ [RAFT] Node {self.id} Initialized.")
        
    def tick(self):
        """
        Main loop for the node.
        """
        now = time.time()
        
        if self.state == "FOLLOWER":
            if now - self.last_heartbeat > self.election_timeout:
                self.start_election()
                
        elif self.state == "LEADER":
            self.send_heartbeats()
            
    def start_election(self):
        print(f"     -> 📣 [ELECTION] Node {self.id} starting election (Term {self.current_term + 1})")
        self.state = "CANDIDATE"
        self.current_term += 1
        self.voted_for = self.id
        self.votes_received = 1
        self.last_heartbeat = time.time()
        
        # Request Votes
        for peer in self.peers:
            if peer.request_vote(self.current_term, self.id):
                self.votes_received += 1
                
        # Check Victory
        if self.votes_received > len(self.peers) / 2:
            self.become_leader()
            
    def request_vote(self, term: int, candidate_id: str) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.voted_for = None
            
        if (self.voted_for is None or self.voted_for == candidate_id) and term >= self.current_term:
            self.voted_for = candidate_id
            self.last_heartbeat = time.time() # Reset timeout
            return True
        return False
        
    def become_leader(self):
        print(f"     -> 👑 [LEADER] Node {self.id} elected Leader for Term {self.current_term}")
        self.state = "LEADER"
        self.send_heartbeats()
        
    def send_heartbeats(self):
        # In a real implementation, this would send AppendEntries RPCs
        # print(f"       [HEARTBEAT] Leader {self.id} pinging peers...")
        for peer in self.peers:
            peer.receive_heartbeat(self.current_term)
            
    def receive_heartbeat(self, term: int):
        if term >= self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.last_heartbeat = time.time()

# --- Verification ---
if __name__ == "__main__":
    # Create Cluster
    n1 = RaftNode("N1", [])
    n2 = RaftNode("N2", [])
    n3 = RaftNode("N3", [])
    
    # Link Peers
    n1.peers = [n2, n3]
    n2.peers = [n1, n3]
    n3.peers = [n1, n2]
    
    # Simulate
    print("\n--- Simulation Start ---")
    time.sleep(0.2)
    n1.tick() # Should trigger election
