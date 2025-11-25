#!/bin/bash

# 1. Status check
git status

# 2. Add all new files and changes
git add .

# 3. Commit with a descriptive message
git commit -m "feat: Grand Unification & JAX Strategy

- Implemented Portal Dashboard with 27 Sovereign Capsules
- Connected Dashboard 'Ignite' to BridgeAPI /v1/capsules/execute
- Ingested physics datasets (Chemistry, Polymer, Metallurgy) into EnergyAtlas
- Finalized JAX Strategy document with Thermodynamic Unification architecture
- Verified end-to-end flow from Frontend to Backend"

# 4. Push to the current branch (assuming main or master, or create a new feature branch)
# git checkout -b feature/grand-unification
# git push origin feature/grand-unification
git push origin main
