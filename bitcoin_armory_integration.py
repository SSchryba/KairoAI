import os
import sys
import logging
from pathlib import Path
import json
from datetime import datetime
import threading
import queue

# Add BitcoinArmory to Python path
armory_path = Path(__file__).parent / "BitcoinArmory"
sys.path.append(str(armory_path))

# Import BitcoinArmory components
try:
    from armoryengine.ArmoryUtils import *
    from armoryengine.Block import *
    from armoryengine.BDM import *
    from armoryengine.Wallet import *
    from armoryengine.PyBtcWallet import *
    from armoryengine.Transaction import *
except ImportError as e:
    logging.error(f"Failed to import BitcoinArmory components: {e}")
    raise

class BitcoinArmoryManager:
    def __init__(self, config_path=None):
        self.logger = logging.getLogger('KairoAI.BitcoinArmory')
        self.config_path = config_path or Path.home() / '.kairoai' / 'bitcoin_armory'
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize BitcoinArmory components
        self.bdm = None
        self.wallet = None
        self.operation_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self):
        config_file = self.config_path / 'config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {
            'network': 'mainnet',
            'data_dir': str(self.config_path / 'data'),
            'wallet_path': str(self.config_path / 'wallets'),
            'max_fee_rate': 0.0001,
            'auto_backup': True
        }
    
    def _save_config(self):
        config_file = self.config_path / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def start(self):
        """Start the BitcoinArmory manager"""
        if self.is_running:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Initialize BDM
        try:
            self.bdm = BDM()
            self.bdm.start()
            self.logger.info("BitcoinArmory BDM started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start BDM: {e}")
            raise
    
    def stop(self):
        """Stop the BitcoinArmory manager"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.bdm:
            self.bdm.stop()
        self.logger.info("BitcoinArmory manager stopped")
    
    def _run_loop(self):
        """Main processing loop for BitcoinArmory operations"""
        while self.is_running:
            try:
                operation = self.operation_queue.get(timeout=1)
                if operation:
                    self._process_operation(operation)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in BitcoinArmory processing loop: {e}")
    
    def _process_operation(self, operation):
        """Process a BitcoinArmory operation"""
        op_type = operation.get('type')
        try:
            if op_type == 'create_wallet':
                self._create_wallet(operation['params'])
            elif op_type == 'send_transaction':
                self._send_transaction(operation['params'])
            elif op_type == 'get_balance':
                return self._get_balance(operation['params'])
            elif op_type == 'get_transactions':
                return self._get_transactions(operation['params'])
            else:
                self.logger.error(f"Unknown operation type: {op_type}")
        except Exception as e:
            self.logger.error(f"Error processing operation {op_type}: {e}")
            raise
    
    def create_wallet(self, name, password, network='mainnet'):
        """Create a new Bitcoin wallet"""
        self.operation_queue.put({
            'type': 'create_wallet',
            'params': {
                'name': name,
                'password': password,
                'network': network
            }
        })
    
    def _create_wallet(self, params):
        """Internal wallet creation method"""
        try:
            wallet_path = Path(self.config['wallet_path']) / f"{params['name']}.wallet"
            wallet = PyBtcWallet()
            wallet.createNewWallet(
                wallet_path=str(wallet_path),
                passphrase=params['password'],
                network=params['network']
            )
            self.wallet = wallet
            self.logger.info(f"Created new wallet: {params['name']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create wallet: {e}")
            raise
    
    def send_transaction(self, to_address, amount, fee_rate=None):
        """Send a Bitcoin transaction"""
        self.operation_queue.put({
            'type': 'send_transaction',
            'params': {
                'to_address': to_address,
                'amount': amount,
                'fee_rate': fee_rate or self.config['max_fee_rate']
            }
        })
    
    def _send_transaction(self, params):
        """Internal transaction sending method"""
        if not self.wallet:
            raise ValueError("No wallet loaded")
            
        try:
            tx = self.wallet.createTx(
                params['to_address'],
                params['amount'],
                feeRate=params['fee_rate']
            )
            self.wallet.broadcastTransaction(tx)
            self.logger.info(f"Transaction sent: {tx.getHash()}")
            return tx.getHash()
        except Exception as e:
            self.logger.error(f"Failed to send transaction: {e}")
            raise
    
    def get_balance(self):
        """Get wallet balance"""
        if not self.wallet:
            raise ValueError("No wallet loaded")
            
        try:
            return {
                'confirmed': self.wallet.getBalance('confirmed'),
                'unconfirmed': self.wallet.getBalance('unconfirmed'),
                'total': self.wallet.getBalance('total')
            }
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            raise
    
    def get_transactions(self, count=10):
        """Get recent transactions"""
        if not self.wallet:
            raise ValueError("No wallet loaded")
            
        try:
            txs = self.wallet.getTransactions(count)
            return [{
                'txid': tx.getHash(),
                'amount': tx.getValue(),
                'timestamp': tx.getTimestamp(),
                'confirmations': tx.getConfirmations()
            } for tx in txs]
        except Exception as e:
            self.logger.error(f"Failed to get transactions: {e}")
            raise

# Add BitcoinArmory endpoints to the API
def register_bitcoin_endpoints(app, btc_manager):
    @app.route('/bitcoin/wallet/create', methods=['POST'])
    def create_wallet():
        try:
            data = request.get_json()
            btc_manager.create_wallet(
                name=data['name'],
                password=data['password'],
                network=data.get('network', 'mainnet')
            )
            return jsonify({'status': 'success', 'message': 'Wallet creation initiated'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/bitcoin/wallet/balance', methods=['GET'])
    def get_balance():
        try:
            balance = btc_manager.get_balance()
            return jsonify({'status': 'success', 'balance': balance})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/bitcoin/transaction/send', methods=['POST'])
    def send_transaction():
        try:
            data = request.get_json()
            tx_hash = btc_manager.send_transaction(
                to_address=data['to_address'],
                amount=data['amount'],
                fee_rate=data.get('fee_rate')
            )
            return jsonify({'status': 'success', 'tx_hash': tx_hash})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/bitcoin/transactions', methods=['GET'])
    def get_transactions():
        try:
            count = request.args.get('count', default=10, type=int)
            transactions = btc_manager.get_transactions(count)
            return jsonify({'status': 'success', 'transactions': transactions})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500 