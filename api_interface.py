from flask import Flask, request, jsonify
from memory import Memory
from decision_engine import DecisionEngine
import psutil
import os
from datetime import datetime
import logging
from healthcheck import HealthCheck, EnvironmentDump
import json_logger
from bitcoin_armory_integration import BitcoinArmoryManager, register_bitcoin_endpoints

# Configure logging
logger = json_logger.JsonLogger()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Initialize health check
health = HealthCheck(app, "/health")
envdump = EnvironmentDump(app, "/environment")

# Initialize core components
memory = Memory()
engine = DecisionEngine(memory)

# Initialize BitcoinArmory manager
btc_manager = BitcoinArmoryManager()

# Register Bitcoin endpoints
register_bitcoin_endpoints(app, btc_manager)

# Add health checks
def check_disk_usage():
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        return False, "Disk usage is above 90%"
    return True, "Disk usage is OK"

def check_memory_usage():
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        return False, "Memory usage is above 90%"
    return True, "Memory usage is OK"

def check_cpu_usage():
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 90:
        return False, "CPU usage is above 90%"
    return True, "CPU usage is OK"

def check_bitcoin_status():
    try:
        btc_manager.get_balance()
        return True, "BitcoinArmory is operational"
    except Exception as e:
        return False, f"BitcoinArmory error: {str(e)}"

# Add the checks
health.add_check(check_disk_usage)
health.add_check(check_memory_usage)
health.add_check(check_cpu_usage)
health.add_check(check_bitcoin_status)

# Add environment information
def application_data():
    return {
        "maintainer": "KairoAI",
        "git_repo": "https://github.com/yourusername/KairoAI",
        "version": "1.0.0",
        "bitcoin_armory": {
            "version": "0.96.5",
            "network": btc_manager.config['network'],
            "wallet_path": btc_manager.config['wallet_path']
        }
    }

envdump.add_section("application", application_data)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "kairo-ai"})

@app.route("/api/memory", methods=["GET"])
def get_memory():
    try:
        return jsonify({"memory": memory.recall()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/respond", methods=["POST"])
def respond():
    try:
        data = request.json
        if not data or "input" not in data:
            return jsonify({"error": "Missing input field"}), 400
            
        input_text = data.get("input", "")
        response = engine.process(input_text)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get detailed system status"""
    try:
        status = {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "uptime": psutil.boot_time()
            },
            "process": {
                "pid": os.getpid(),
                "memory_info": dict(psutil.Process().memory_info()._asdict()),
                "cpu_percent": psutil.Process().cpu_percent()
            },
            "bitcoin": {
                "status": "operational" if btc_manager.wallet else "no_wallet",
                "balance": btc_manager.get_balance() if btc_manager.wallet else None
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error("Status check failed", extra={"error": str(e)})
        return jsonify({"status": "error", "message": str(e)}), 500

# Initialize BitcoinArmory on startup
@app.before_first_request
def initialize_bitcoin():
    try:
        btc_manager.start()
        logger.info("BitcoinArmory manager started successfully")
    except Exception as e:
        logger.error(f"Failed to start BitcoinArmory manager: {e}")

# Cleanup on shutdown
@app.teardown_appcontext
def cleanup_bitcoin(exception=None):
    try:
        btc_manager.stop()
        logger.info("BitcoinArmory manager stopped")
    except Exception as e:
        logger.error(f"Error stopping BitcoinArmory manager: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
