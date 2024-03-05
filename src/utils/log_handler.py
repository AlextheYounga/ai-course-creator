import logging
import os

env = os.environ.get("APP_ENV", "development")

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the minimum logging level

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if env == "development":
    app_handler = logging.FileHandler('storage/logs/app.log')
    app_handler.setFormatter(formatter)
    logger.addHandler(app_handler)

else:
    test_handler = logging.FileHandler('test/data/test.log')
    test_handler.setFormatter(formatter)
    logger.addHandler(test_handler)


LOG_HANDLER = logger
