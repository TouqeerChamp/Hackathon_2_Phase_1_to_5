Ubuntu ya WSL

1. Backend Start Karein (Terminal 1)

Step 1: 
# Pehle backend folder mein jayein
cd ~/projects/phase_III/backend
Step 2: 
# PYTHONPATH set karein (taake modules sahi import hon)
export PYTHONPATH=$PYTHONPATH:.
Step 3:
# Server start karein
python3 -m uvicorn src.main:app --reload
 

2. Frontend Start Karein (Terminal 2)

Step 1:
# Frontend folder mein jayein
cd ~/projects/phase_III/frontend
Step 2:
# App chalaein
npm run dev