from typing import List, Dict
from pydantic import BaseModel

class Skill(BaseModel):
    name: str
    version: str
    description: str
    requirements: List[str]  # e.g., ["5-axis", "high-temp"]
    parameters: Dict[str, str]  # e.g., {"speed": "high", "precision": "low"}

class SkillTree(BaseModel):
    """
    Represents the evolvable capabilities of a Capsule.
    Capsules can 'unlock' new skills through learning or sharing.
    """
    capsule_id: str
    unlocked_skills: List[Skill] = []
    potential_skills: List[Skill] = []
    experience_points: int = 0

    def unlock_skill(self, skill_name: str):
        """Unlocks a skill if XP is sufficient (Mock logic)."""
        for skill in self.potential_skills:
            if skill.name == skill_name:
                self.unlocked_skills.append(skill)
                self.potential_skills.remove(skill)
                return True
        return False

    def share_skill(self) -> dict:
        """Exports the latest skill for other Capsules."""
        if not self.unlocked_skills:
            return {}
        return self.unlocked_skills[-1].dict()
