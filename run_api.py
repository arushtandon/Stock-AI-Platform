#!/usr/bin/env python3
"""Run FastAPI from project root with PYTHONPATH set."""
import os
import sys

# Ensure project root is on path
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
os.chdir(root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
