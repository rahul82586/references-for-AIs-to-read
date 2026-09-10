import sys
import os
import time
import logging

# Add current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connectors.mt5_connector import MT5Connector

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("test_manual")

def main():
    logger.info("Initializing manual MT5Connector test...")
    
    # Target credentials (change to correct ones)
    login = 50080
    password = "!o0Od289"
    server = "86.104.251.194:443"
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    
    connector = MT5Connector(config={
        "id": "mt5_main",
        "params": {
            "path": path,
            "login": login,
            "password": password,
            "server": server
        }
    })
    
    logger.info("Calling connector.connect()...")
    success = connector.connect()
    logger.info(f"connector.connect() returned {success}")
    
    logger.info("Waiting for connector to report connection...")
    start_wait = time.time()
    while time.time() - start_wait < 15.0:
        if connector.is_connected:
            logger.info("Successfully connected!")
            break
        if connector.last_error_msg:
            logger.error(f"Connector error reported: {connector.last_error_msg}")
            break
        time.sleep(0.5)
    else:
        logger.warning("Timeout waiting for connection.")
        
    logger.info("Disconnecting connector...")
    connector.disconnect()
    logger.info("Test complete.")

if __name__ == "__main__":
    # On Windows, multiprocessing spawn requires freeze_support
    import multiprocessing
    multiprocessing.freeze_support()
    main()
