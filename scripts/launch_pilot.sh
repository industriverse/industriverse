#!/bin/bash
echo "🚀 Launching S-REAN Pilot App (Area 12: Magnet Assembly)..."
streamlit run src/frontend_widgets/pilot_app.py --server.port 8501 --server.address 0.0.0.0
