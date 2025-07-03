import scripts.preparation
import subprocess
import pathlib


# preparation
scripts.preparation.RunPreparation()

# server run
run_prefix = pathlib.Path(__file__).parent.resolve()
subprocess.run(f"python3 -m streamlit run {run_prefix}/scripts/server.py".split())
