import logging
from pathlib import Path

log_file = Path.home() / '.PAI/app_logs/PAI_app_log.json'
log_file.parent.mkdir(parents=True, exist_ok=True)  

# Create root logger
logger = logging.getLogger("PAI")
logger.setLevel(logging.DEBUG)  

file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(console_handler)
logger.console_handler = console_handler 