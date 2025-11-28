from src.demo_framework.scenario import DemoScenario

ECON_LIFE_SCENARIOS = [
    DemoScenario(
        id="ECON-001", name="Capsule Minting", domain="Economy",
        description="Mint a new Capsule as an NFT.",
        hypothesis="Register capsule://demo/v1 on XRPL.",
        expected_outcome={"tx_status": "Success", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="ECON-002", name="Token Swap", domain="Economy",
        description="Swap Entropy Tokens for Compute Credits.",
        hypothesis="Execute atomic swap on ledger.",
        expected_outcome={"swap_status": "Complete", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="ECON-003", name="Capsule Auction", domain="Economy",
        description="Auction a high-value optimization capsule.",
        hypothesis="Highest bidder wins rights.",
        expected_outcome={"winner": "Determined", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="ECON-004", name="Royalty Distribution", domain="Economy",
        description="Distribute royalties to capsule contributors.",
        hypothesis="Split payment based on contribution graph.",
        expected_outcome={"distribution": "Fair", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-001", name="NCA Morphogenesis", domain="ALife",
        description="Grow a pattern from a single seed.",
        hypothesis="Apply local update rules iteratively.",
        expected_outcome={"pattern": "Stable", "energy": "<0.5"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-002", name="Self-Repair", domain="ALife",
        description="Regenerate damaged region of pattern.",
        hypothesis="NCA agents detect and fill void.",
        expected_outcome={"integrity": "Restored", "energy": "<0.4"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-003", name="Colony Growth", domain="ALife",
        description="Expand colony while avoiding obstacles.",
        hypothesis="Agents follow nutrient gradient.",
        expected_outcome={"colony_size": "Increased", "energy": "<0.6"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-004", name="Predatory Behavior", domain="ALife",
        description="Simulate predator-prey dynamics.",
        hypothesis="Predators chase prey agents.",
        expected_outcome={"population": "Balanced", "energy": "<0.7"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-005", name="Symbiosis", domain="ALife",
        description="Two agent types cooperate for survival.",
        hypothesis="Type A provides defense, Type B provides energy.",
        expected_outcome={"survival_rate": "High", "energy": "<0.3"},
        required_priors=[]
    ),
    DemoScenario(
        id="LIFE-006", name="Ecosystem Balance", domain="ALife",
        description="Maintain diversity in multi-species dish.",
        hypothesis="Resource competition limits dominance.",
        expected_outcome={"diversity": "High", "energy": "<0.5"},
        required_priors=[]
    )
]
