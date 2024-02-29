import logging


logging.basicConfig(
    filename="storage/logs/chat.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

LOG_HANDLER = logging.getLogger
