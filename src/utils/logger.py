import logging
import os


def log_setup(log_file: str = 'app.log'):
    env = os.environ.get("APP_ENV", "development")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the minimum logging level

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if env == "development":
        app_handler = logging.FileHandler(f'storage/logs/{log_file}')
        app_handler.setFormatter(formatter)
        logger.addHandler(app_handler)

    else:
        test_handler = logging.FileHandler(f'test/data/logs/{log_file}')
        test_handler.setFormatter(formatter)
        logger.addHandler(test_handler)

        return logger
