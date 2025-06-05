import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
from pathlib import Path
import subprocess
from datetime import datetime
import json
import shutil

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / f"kairo_service_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class KairoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KairoAI"
    _svc_display_name_ = "Kairo AI Service"
    _svc_description_ = "Kairo AI System Service - Manages the AI system and BitcoinArmory in production mode"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.process = None
        self.bitcoin_process = None
        self._setup_bitcoin_environment()

    def _setup_bitcoin_environment(self):
        """Setup BitcoinArmory environment"""
        try:
            # Create necessary directories
            config_path = Path.home() / '.kairoai' / 'bitcoin_armory'
            for dir_name in ['data', 'wallets', 'backups']:
                (config_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Copy BitcoinArmory files if needed
            armory_path = Path(__file__).parent / 'BitcoinArmory'
            if not (config_path / 'data' / 'armoryd.conf').exists():
                shutil.copy2(
                    armory_path / 'armoryd.conf',
                    config_path / 'data' / 'armoryd.conf'
                )

            # Load and update configuration
            config_file = Path(__file__).parent / 'bitcoin_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                config['data_dir'] = str(config_path / 'data')
                config['wallet_dir'] = str(config_path / 'wallets')
                config['backup_dir'] = str(config_path / 'backups')
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=4)

            logging.info("BitcoinArmory environment setup completed")
        except Exception as e:
            logging.error(f"Failed to setup BitcoinArmory environment: {e}")
            raise

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
        # Stop BitcoinArmory process
        if self.bitcoin_process:
            try:
                self.bitcoin_process.terminate()
                self.bitcoin_process.wait(timeout=30)
            except Exception as e:
                logging.error(f"Error stopping BitcoinArmory: {e}")
        
        # Stop main process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=30)
            except Exception as e:
                logging.error(f"Error stopping main process: {e}")
        
        logging.info("Service stopping...")

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            logging.info("Service starting...")
            self.main()
        except Exception as e:
            logging.error(f"Service error: {str(e)}")
            servicemanager.LogErrorMsg(f"Service error: {str(e)}")

    def main(self):
        while True:
            try:
                # Start BitcoinArmory daemon
                armory_path = Path(__file__).parent / 'BitcoinArmory'
                self.bitcoin_process = subprocess.Popen(
                    [sys.executable, str(armory_path / 'armoryd.py')],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                logging.info("BitcoinArmory daemon started")

                # Start the main application
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.py")
                self.process = subprocess.Popen(
                    [sys.executable, script_path, "--api"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                logging.info("Main application started")
                
                # Wait for stop event
                win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
                
                # Cleanup processes
                if self.process:
                    self.process.terminate()
                    self.process.wait()
                if self.bitcoin_process:
                    self.bitcoin_process.terminate()
                    self.bitcoin_process.wait()
                
            except Exception as e:
                logging.error(f"Main loop error: {str(e)}")
                # Wait before retrying
                win32event.WaitForSingleObject(self.stop_event, 5000)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(KairoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(KairoService) 