import os
import subprocess
import sys
import uvicorn
from core.settings import settings
import re
import time

def kill_port(port):
    """
    Finds and kills the process listening on the specified port (Windows only).
    """
    try:
        # Run netstat to find the PID
        # -a: Display all connections and listening ports.
        # -n: Display addresses and port numbers in numerical form.
        # -o: Own process ID associated with each connection.
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        lines = output.strip().split("\n")
        
        target_pid = None
        for line in lines:
            if "LISTENING" in line:
                # Format is typically:  TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
                parts = re.split(r'\s+', line.strip())
                # We expect at least Protocol, Local Address, Foreign Address, State, PID
                if len(parts) >= 5:
                    target_pid = parts[-1]
                    break
        
        if target_pid:
            print(f"[!] Port {port} is in use by PID {target_pid}. Killing it...")
            subprocess.run(f"taskkill /F /PID {target_pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1) # Give OS time to release port
            print(f"[+] Process {target_pid} killed and port released.")
            
    except subprocess.CalledProcessError:
        # netstat returns error if string not found, which means port is free
        pass
    except Exception as e:
        print(f"[!] Warning: Failed to clean up port {port}: {e}")


def run_dev_server():
    """
    Starts the Svelte frontend and FastAPI backend.
    Intended for development with debugger attachment support.
    """
    
    
    # 0. Cleanup Port
    # ---------------
    kill_port(settings.PORT)

    # 1. Start Frontend (Svelte)
    # --------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shell_dir = os.path.join(base_dir, "shell")
    
    print("==========================================")
    print("   WebSH Development Server (Python)      ")
    print("==========================================")
    print(f"[1/2] Starting Frontend in {shell_dir}...")
    
    # Use Popen to run non-blocking
    # On Windows, 'npm' is a batch file, so shell=True is often required.
    frontend_cmd = ["npm", "run", "dev", "--", "--open"]
    frontend_process = subprocess.Popen(
        frontend_cmd, 
        cwd=shell_dir, 
        shell=True
    )
    
    # 2. Start Backend (FastAPI)
    # --------------------------
    print("[2/2] Starting Backend (Main Process)...")
    print("      (Attach your debugger to this process)")
    
    try:
        # Import app here to avoid side effects before printing header
        from main import app
        
        # Run uvicorn in the main process (reload=False allows debugging)
        uvicorn.run(
            app, 
            host=settings.HOST, 
            port=settings.PORT, 
            log_level="info",
            # reload=False is default, which is what we want for direct debugging
        )
        
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt received. Stopping servers...")
    except Exception as e:
        print(f"\n[!] Error starting backend: {e}")
    finally:
        # 3. Cleanup
        # ----------
        print("Cleaning up frontend process...")
        if frontend_process:
            # On Windows with shell=True, terminate() kills the shell, not necessarily the child (npm/node).
            # We might need a stronger kill if it persists, but terminate is the polite start.
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print("Frontend process did not exit, forcing kill...")
                frontend_process.kill()
        
        print("Shutdown complete.")

if __name__ == "__main__":
    run_dev_server()
