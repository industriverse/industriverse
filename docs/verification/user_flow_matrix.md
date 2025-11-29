# User Flow Verification Matrix (100 Scenarios)

This document defines the 100 scenarios required to verify the Industriverse system as a "single organism".

## Pack A: Energy Atlas (20 Scenarios)
| ID | Scenario | Expected Outcome |
|---|---|---|
| A01 | Query existing material (PLA) | Return cost/energy data |
| A02 | Query existing material (TPU) | Return cost/energy data |
| A03 | Query non-existent material | Return "Not Found" or suggestion |
| A04 | Query with typo (PLAA) | Fuzzy match or error |
| A05 | Filter by Max Cost ($0.10) | Return only cheap materials |
| A06 | Filter by Max Energy (150J) | Return only low-energy materials |
| A07 | Sort by Cost (Asc) | Correct order |
| A08 | Sort by Energy (Asc) | Correct order |
| A09 | Voxel Viz: Low Density | Render sparse grid |
| A10 | Voxel Viz: High Density | Render dense grid |
| A11 | G-Code Viz: Simple Cube | Parse 6 layers |
| A12 | G-Code Viz: Complex Gear | Parse 50+ layers |
| A13 | G-Code Viz: Corrupt File | Error handling |
| A14 | Heatmap: Uniform Temp | No hotspots |
| A15 | Heatmap: Overheating | Identify hotspots |
| A16 | Cost Map: Low Entropy | Low risk premium |
| A17 | Cost Map: High Entropy | High risk premium |
| A18 | Fusion: Compatible Materials | High bond strength |
| A19 | Fusion: Incompatible Materials | Low bond strength warning |
| A20 | Atlas API Latency Check | Response < 200ms |

## Pack B: Intent Layer (20 Scenarios)
| ID | Scenario | Expected Outcome |
|---|---|---|
| B01 | Simple Prompt: "Make a gear" | Generate Gear LCODE |
| B02 | Simple Prompt: "Make a bracket" | Generate Bracket LCODE |
| B03 | Modifier: "Lightweight" | Reduce infill |
| B04 | Modifier: "Strong" | Increase infill/walls |
| B05 | Modifier: "Fast" | Increase speed |
| B06 | Modifier: "Precision" | Decrease speed, check alignment |
| B07 | Ambiguous: "Make it good" | Ask for clarification or default |
| B08 | Conflict: "Fast and Precision" | Prioritize or warn |
| B09 | Chain: "Gear then Bracket" | Sequence of jobs |
| B10 | Grammar: Valid LCODE | Pass validation |
| B11 | Grammar: Invalid LCODE | Fail validation with error |
| B12 | Safety: "Melt it" (Unsafe) | Reject intent |
| B13 | Pricing: Low Budget | Suggest cheaper material |
| B14 | Pricing: High Budget | Suggest premium material |
| B15 | Feedback: "Too expensive" | Re-optimize for cost |
| B16 | Feedback: "Too slow" | Re-optimize for speed |
| B17 | Multi-lingual: "Hacer un engranaje" | Translate and generate |
| B18 | Context: "Like the last one" | Recall previous context |
| B19 | Noise: "asdfghjkl" | Error handling |
| B20 | Intent API Latency Check | Response < 1s |

## Pack C: AI Shield (20 Scenarios)
| ID | Scenario | Expected Outcome |
|---|---|---|
| C01 | Policy: Max Temp 240C | Allow 230C |
| C02 | Policy: Max Temp 240C | Block 250C |
| C03 | Policy: Max Speed 5000 | Allow 4000 |
| C04 | Policy: Max Speed 5000 | Block 6000 |
| C05 | Override: Authorized User | Allow violation with log |
| C06 | Override: Unauthorized User | Block violation |
| C07 | Vulnerability: Injection Attack | Sanitize input |
| C08 | Vulnerability: Buffer Overflow | Handle gracefully |
| C09 | Compliance: GDPR Check | Mask PII |
| C10 | Compliance: Audit Log | Log all actions |
| C11 | Real-time: Sudden Spike | Trigger E-STOP |
| C12 | Real-time: Gradual Drift | Trigger Warning |
| C13 | Protocol: Valid Signature | Accept command |
| C14 | Protocol: Invalid Signature | Reject command |
| C15 | Encryption: Encrypted Cmd | Decrypt successfully |
| C16 | Encryption: Plaintext Cmd | Reject (if strict) |
| C17 | Access: Read Only | Allow read, block write |
| C18 | Access: Admin | Allow all |
| C19 | Shield Latency Check | Overhead < 10ms |
| C20 | Recovery: Shield Crash | Fail safe (block all) |

## Pack D: Predictive Twin (20 Scenarios)
| ID | Scenario | Expected Outcome |
|---|---|---|
| D01 | Monitor: Steady State | Stable readings |
| D02 | Monitor: Fluctuation | Update graph |
| D03 | Predict: 1s Horizon | High confidence |
| D04 | Predict: 1m Horizon | Medium confidence |
| D05 | Predict: 1h Horizon | Low confidence |
| D06 | Drift: Thermal Runaway | Predict failure |
| D07 | Drift: Vibration | Predict bearing fault |
| D08 | What-If: +50% Speed | Predict vibration spike |
| D09 | What-If: Coolant Fail | Predict overheat |
| D10 | Replay: Normal Job | Match historical data |
| D11 | Replay: Failed Job | Reproduce failure |
| D12 | Comparison: Sim vs Real | Calculate delta |
| D13 | Calibration: Adjust Model | Reduce delta |
| D14 | Anomaly: Unknown Pattern | Flag as anomaly |
| D15 | Maintenance: Healthy | > 100h remaining |
| D16 | Maintenance: Critical | < 1h remaining |
| D17 | Viz: Confidence Interval | Show bounds |
| D18 | Viz: 3D Overlay | Sync with telemetry |
| D19 | Twin Latency Check | Update < 50ms |
| D20 | Data Gap | Interpolate missing data |

## Pack E: Grand Loop (20 Scenarios)
| ID | Scenario | Expected Outcome |
|---|---|---|
| E01 | Full Loop: Idea -> Product | End-to-end success |
| E02 | Full Loop: Optimization | Improve metric over iterations |
| E03 | Bidding: Low Bid | Lose auction |
| E04 | Bidding: High Bid | Win auction |
| E05 | Bidding: Optimal Bid | Win with margin |
| E06 | Scheduling: Empty Queue | Immediate start |
| E07 | Scheduling: Full Queue | Add to backlog |
| E08 | Scheduling: Priority | Bump to front |
| E09 | Resource: Sufficient | Proceed |
| E10 | Resource: Insufficient | Pause/Request |
| E11 | Error: Machine Offline | Re-route job |
| E12 | Error: Network Partition | Queue locally |
| E13 | Consensus: Unanimous | Commit block |
| E14 | Consensus: Split | Resolve fork |
| E15 | Upgrade: New Skill | Learn and apply |
| E16 | Upgrade: New Material | Update Atlas |
| E17 | Multi-Agent: Collaboration | Shared goal achievement |
| E18 | Multi-Agent: Competition | Market equilibrium |
| E19 | Loop Latency Check | Cycle time < target |
| E20 | System Restart | Resume state |
