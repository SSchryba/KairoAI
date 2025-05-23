import sys
from interfaces.cli_interface import run_cli
from interfaces.api_interface import app as api_app

if __name__ == "__main__":
    if "--api" in sys.argv:
        print("🌐 KAIRO API MODE ENABLED")
        api_app.run(host="0.0.0.0", port=5000)
    else:
        run_cli()
