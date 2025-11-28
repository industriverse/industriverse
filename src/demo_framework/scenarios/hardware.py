from src.demo_framework.scenario import DemoScenario

HARDWARE_SCENARIOS = [
    DemoScenario(
        id="HW-001", name="FPGA Blinky Synthesis", domain="Hardware",
        description="Synthesize LED blinker for Lattice IceStick.",
        hypothesis="Generate Verilog for 1Hz counter.",
        expected_outcome={"bitstream": "Generated", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-002", name="RISC-V Core Config", domain="Hardware",
        description="Configure VexRiscv for minimal area.",
        hypothesis="Disable FPU and caches.",
        expected_outcome={"lut_count": "<1000", "energy": "<0.2"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-003", name="ASM Matrix Multiplication", domain="Hardware",
        description="Optimize GEMM for AVX-512.",
        hypothesis="Unroll loops and use ZMM registers.",
        expected_outcome={"flops": "Maximized", "energy": "<0.5"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-004", name="Tensor Core Optimization", domain="Hardware",
        description="Map TNN ops to Tensor Cores.",
        hypothesis="Use FP16 mixed precision.",
        expected_outcome={"throughput": "High", "energy": "<0.4"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-005", name="Edge Inference Deployment", domain="Hardware",
        description="Deploy Capsule to edge device.",
        hypothesis="Quantize weights to INT8.",
        expected_outcome={"model_size": "Small", "energy": "<0.3"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-006", name="Bitstream Morphing", domain="Hardware",
        description="Dynamic partial reconfiguration of FPGA.",
        hypothesis="Swap accelerator module at runtime.",
        expected_outcome={"downtime": "<1ms", "energy": "<0.6"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-007", name="Cache Coherence Protocol", domain="Hardware",
        description="Verify MESI protocol implementation.",
        hypothesis="Check state transitions for correctness.",
        expected_outcome={"coherence": "Maintained", "energy": "<0.2"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-008", name="Memory Bandwidth Optimization", domain="Hardware",
        description="Maximize DRAM utilization.",
        hypothesis="Optimize bank interleaving.",
        expected_outcome={"bandwidth": ">90%", "energy": "<0.5"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-009", name="Power Gating Strategy", domain="Hardware",
        description="Reduce leakage power in idle blocks.",
        hypothesis="Implement fine-grained power gating.",
        expected_outcome={"leakage": "Reduced", "energy": "<0.1"},
        required_priors=[]
    ),
    DemoScenario(
        id="HW-010", name="NoC Routing Optimization", domain="Hardware",
        description="Optimize Network-on-Chip routing.",
        hypothesis="Use adaptive XY routing to avoid congestion.",
        expected_outcome={"latency": "Low", "energy": "<0.4"},
        required_priors=[]
    )
]
