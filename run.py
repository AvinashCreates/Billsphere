import os
import sys
import subprocess
import time

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def find_python():
    """Find virtual environment python or fallback to active python interpreter."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_win = os.path.join(base_dir, "backend", ".venv", "Scripts", "python.exe")
    venv_unix = os.path.join(base_dir, "backend", ".venv", "bin", "python")
    cfg_win = os.path.join(base_dir, "backend", ".venv", "pyvenv.cfg")
    cfg_unix = os.path.join(base_dir, "backend", ".venv", "pyvenv.cfg")
    
    if os.path.exists(venv_win) and os.path.exists(cfg_win):
        return venv_win
    elif os.path.exists(venv_unix) and os.path.exists(cfg_unix):
        return venv_unix
    return sys.executable

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")
    
    python_bin = find_python()
    
    print("==================================================")
    print("        Starting Billsphere Full Stack            ")
    print("==================================================")
    print(f"Python Executable: {python_bin}")
    print("Backend API will run at: http://127.0.0.1:8000")
    print("Frontend Dev App will run at: http://127.0.0.1:5173")
    print("==================================================\n")
    
    processes = []
    
    try:
        # Start FastAPI Backend
        print("[Backend] Launching Uvicorn server...")
        backend_cmd = [python_bin, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
        backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)
        processes.append(backend_proc)
        
        # Give backend a moment to boot
        time.sleep(1.5)
        
        # Start Vite Frontend
        print("[Frontend] Launching Vite dev server...")
        frontend_cmd = "npm run dev -- --host 0.0.0.0"
        frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=True)
        processes.append(frontend_proc)

        
        print("\n[SUCCESS] Both servers are running! Press Ctrl+C to stop.\n")
        
        # Keep main process alive and watch sub-processes
        while True:
            time.sleep(0.5)
            for proc in processes:
                if proc.poll() is not None:
                    print(f"[Warning] A sub-process exited with code {proc.returncode}")
                    
    except KeyboardInterrupt:
        print("\nShutting down backend and frontend...")
    finally:
        for proc in processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()
        print("All servers stopped cleanly.")

if __name__ == "__main__":
    main()
