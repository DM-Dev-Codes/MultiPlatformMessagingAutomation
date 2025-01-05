import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from common.utils import ensureEnvVars


BASE_DIR = Path(__file__).resolve().root
load_dotenv()


def startStreamlit():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR) 
    website_dir = BASE_DIR / "website"  
    os.chdir(website_dir)
    return subprocess.Popen(["streamlit", "run", "app.py"], env=env)


def startBackend():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)   # Ensure the entire project is in PYTHONPATH
    action_module = "action_manager.manage_actions" 
    return subprocess.Popen(["python3", "-m", action_module], env=env)

def main():
    from pipe_manager import NamedPipeManager
    _ = NamedPipeManager()._initialize()
    streamlit_proc = startStreamlit()
    bot_proc = startBackend()
    try:
        streamlit_proc.wait()
        bot_proc.wait()
    except KeyboardInterrupt:
        print("Stopping processes...")
        # Kill the actual subprocess
        streamlit_proc.terminate()
        bot_proc.terminate()
        streamlit_proc.wait()
        bot_proc.wait()

if __name__ == "__main__":
    ensureEnvVars()
    main()

