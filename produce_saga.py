import sys
import os
import time
import subprocess

# Add project root to path
sys.path.append(os.getcwd())

def type_writer(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def print_header(text):
    print("\n" + "="*80)
    print(f"🎬 {text.upper()}")
    print("="*80 + "\n")

def play_demo(path, description):
    print(f"\n>>> [VISUAL INSERT] {description}")
    print(f">>> Running {path}...\n")
    time.sleep(1)
    
    try:
        # Run the demo and capture output
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Print a snippet of the output to simulate the visual
        output_lines = result.stdout.splitlines()
        
        # Filter for interesting lines (skip headers/footers usually)
        snippet = []
        for line in output_lines:
            if "DEMO" not in line and "=" not in line and line.strip() != "":
                snippet.append(line)
        
        # Show first 5 and last 5 lines of interesting content
        display_lines = snippet[:5]
        if len(snippet) > 10:
            display_lines.append("... [DATA STREAM ACCELERATING] ...")
            display_lines.extend(snippet[-5:])
        elif len(snippet) > 5:
            display_lines.extend(snippet[5:])
            
        print("    " + "\n    ".join(display_lines))
        print(f"\n>>> [CUT TO BLACK]\n")
        
    except Exception as e:
        print(f"    [ERROR: SIGNAL LOST - {e}]")

def run_saga():
    print_header("THE INDUSTRIVERSE SAGA: ENTROPY & ORDER")
    time.sleep(1)

    # --- ACT I ---
    print("\n\n")
    print("--- ACT I: THE AWAKENING (Order from Chaos) ---")
    print("EXT. INDUSTRIAL WASTELAND - NIGHT. Sparks flying. Chaos.\n")
    
    type_writer("VOICEOVER: 'In the beginning... there was only noise. A billion sensors screaming into the void.'")
    time.sleep(1)
    
    play_demo("demos/02_telemetry_ingestion/run_demo.py", "Raw Telemetry Streams Stabilizing")
    
    type_writer("VOICEOVER: 'We didn't just listen. We taught the machine to speak the language of the universe.'")
    
    play_demo("demos/22_power_trace/run_demo.py", "Power Trace converting to Energy Vector E(t)")
    play_demo("demos/23_conservation_enforcer/run_demo.py", "Conservation Laws crushing anomalies")
    play_demo("demos/25_manifold_viz/run_demo.py", "Data organizing into a perfect Manifold")

    # --- ACT II ---
    print("\n\n")
    print("--- ACT II: THE INTELLIGENCE (Understanding the World) ---")
    print("INT. OPS ROOM. Screens flashing.\n")
    
    type_writer("VOICEOVER: 'Thermodynamics. The only law that cannot be broken.'")
    
    play_demo("demos/24_translator_rules/run_demo.py", "Translating Physics to Semantics")
    play_demo("demos/27_narrative_gen/run_demo.py", "The Machine generating Incident Reports")
    play_demo("demos/28_flow_field/run_demo.py", "Predicting Future Energy Flows")
    play_demo("demos/30_phase_diagram/run_demo.py", "Mapping the Boundaries of Safety")

    # --- ACT III ---
    print("\n\n")
    print("--- ACT III: THE AGENCY (The System Acts) ---")
    print("MONTAGE. Code rewriting itself.\n")
    
    type_writer("VOICEOVER: 'It didn't just watch. It learned to protect itself. Autonomous. Resilient. Sovereign.'")
    
    play_demo("demos/06_srean_optimization/run_demo.py", "Agents Negotiating Resources")
    play_demo("demos/36_gpu_throttle/run_demo.py", "Deciding to Throttle GPU based on Cost")
    play_demo("demos/10_self_healing/run_demo.py", "Self-Healing after a crash")
    play_demo("demos/13_remix_lab/run_demo.py", "Evolution: Merging Capabilities")

    # --- ACT IV ---
    print("\n\n")
    print("--- ACT IV: THE EXPANSION (Universal Application) ---")
    print("EXT. CITYSCAPE. Factory -> Hospital -> Market.\n")
    
    type_writer("VOICEOVER: 'From the forge... to the cell... to the market. One physics. One platform.'")
    
    play_demo("demos/26_universal_normalizer/run_demo.py", "Normalizing Bio and Finance Data")
    play_demo("demos/39_shadow_twin/run_demo.py", "Creating a Digital Twin")
    play_demo("demos/12_partner_portal/run_demo.py", "Scaling to Partners")
    play_demo("demos/15_god_view/run_demo.py", "Total Situational Awareness")

    # --- FINALE ---
    print("\n\n")
    print("--- FINALE: THE GRAND UNIFICATION (Sovereignty) ---")
    print("INT. THE GOD VIEW. A single operator.\n")
    
    type_writer("VOICEOVER: 'The Grand Unification is here.'")
    
    play_demo("demos/18_utid_auth/run_demo.py", "Verifying Identity")
    play_demo("demos/19_secure_update/run_demo.py", "Evolving Firmware")
    play_demo("demos/17_zkp_verification/run_demo.py", "Proving without Revealing")
    play_demo("demos/21_full_stack/run_demo.py", "THE FULL STACK JOURNEY")

    print("\n\n")
    print("FADE TO LOGO: INDUSTRIVERSE")
    print("TEXT: Thermodynamic Sovereignty.")
    print("\n[END]")

if __name__ == "__main__":
    run_saga()
