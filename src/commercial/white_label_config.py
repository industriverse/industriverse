from dataclasses import dataclass
import json

@dataclass
class BrandConfig:
    platform_name: str
    logo_url: str
    primary_color: str
    support_email: str
    powered_by_visible: bool

class WhiteLabelManager:
    """
    Manages Dynamic Branding for Partners.
    Supports Offer #3: White-Labeled Intelligence Fabric.
    """
    
    def __init__(self):
        # Default Branding (Industriverse)
        self.current_config = BrandConfig(
            platform_name="Industriverse",
            logo_url="/assets/logo_main.png",
            primary_color="#00FF99", # Neon Green
            support_email="support@industriverse.ai",
            powered_by_visible=True
        )
        
    def load_partner_config(self, config_path: str):
        """
        Loads a partner's branding configuration.
        """
        # Mock loading from file
        print(f"🎨 Loading White-Label Config from {config_path}...")
        
        # Simulating a partner config (e.g., "Global Telco AI")
        self.current_config = BrandConfig(
            platform_name="GlobalTelco AI OS",
            logo_url="/assets/partners/telco_logo.png",
            primary_color="#0044FF", # Corporate Blue
            support_email="ai-support@globaltelco.com",
            powered_by_visible=False # Hidden attribution
        )
        
    def get_ui_context(self) -> dict:
        """
        Returns the context dictionary for the Frontend.
        """
        return {
            "app_title": self.current_config.platform_name,
            "theme": {
                "primary": self.current_config.primary_color
            },
            "assets": {
                "logo": self.current_config.logo_url
            },
            "footer": {
                "contact": self.current_config.support_email,
                "show_attribution": self.current_config.powered_by_visible
            }
        }

# --- Verification ---
if __name__ == "__main__":
    wl_manager = WhiteLabelManager()
    
    print("🔹 Default Config:")
    print(json.dumps(wl_manager.get_ui_context(), indent=2))
    
    print("\n🔄 Applying Partner Branding...")
    wl_manager.load_partner_config("configs/telco_partner.json")
    
    print("🔹 Partner Config:")
    print(json.dumps(wl_manager.get_ui_context(), indent=2))
