from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Certification:
    id: str
    name: str
    level: int # 1-3
    required_capsules: List[str]

@dataclass
class UserProfile:
    user_id: str
    avatar_tier: str # 'NOVICE', 'OPERATOR', 'ARCHITECT', 'LITHOGRAPHER'
    completed_certs: List[str] = field(default_factory=list)

class CertificationEngine:
    """
    Manages Industriverse Academy Certifications and Avatar Progression.
    Supports Checklist Item III.A.
    """
    
    def __init__(self):
        # Define Tracks
        self.tracks = {
            "ICDE": Certification("ICDE", "Capsule Design & Engineering", 1, ["CAP_BUILDER_101"]),
            "ICCD": Certification("ICCD", "DeploymentOps", 1, ["K8S_DEPLOY_101"]),
            "ICSS": Certification("ICSS", "Simulation & Strategy", 2, ["SIM_THEORY_201"])
        }
        
    def complete_certification(self, user: UserProfile, cert_id: str):
        """
        Marks a cert as complete and checks for Avatar Upgrade.
        """
        if cert_id not in self.tracks:
            print(f"❌ Unknown Certification: {cert_id}")
            return
            
        if cert_id in user.completed_certs:
            print(f"⚠️ Certification {cert_id} already completed.")
            return

        print(f"🎓 User {user.user_id} completed {self.tracks[cert_id].name}!")
        user.completed_certs.append(cert_id)
        self._update_avatar_tier(user)
        
    def _update_avatar_tier(self, user: UserProfile):
        """
        Upgrades Avatar based on completed certs.
        """
        count = len(user.completed_certs)
        old_tier = user.avatar_tier
        
        if count >= 3:
            user.avatar_tier = "LITHOGRAPHER"
        elif count >= 2:
            user.avatar_tier = "ARCHITECT"
        elif count >= 1:
            user.avatar_tier = "OPERATOR"
        else:
            user.avatar_tier = "NOVICE"
            
        if user.avatar_tier != old_tier:
            print(f"✨ AVATAR UPGRADE: {old_tier} -> {user.avatar_tier}")

# --- Verification ---
if __name__ == "__main__":
    engine = CertificationEngine()
    user = UserProfile("USER_123", "NOVICE")
    
    print("📚 Starting Academy Journey...")
    engine.complete_certification(user, "ICDE")
    engine.complete_certification(user, "ICCD")
    engine.complete_certification(user, "ICSS")
    
    print(f"\n👤 Final Profile: {user.avatar_tier}")
    print(f"📜 Certs: {user.completed_certs}")
