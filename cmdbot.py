import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.agent import run_agent

if __name__ == "__main__":
    run_agent()