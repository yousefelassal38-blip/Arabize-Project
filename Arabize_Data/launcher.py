from updater.client import run_update_preflight
from app.main import App
if __name__ == "__main__" and run_update_preflight(): App().mainloop()
