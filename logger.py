import logging
import os


def setup_logging():
    # Создаем директорию для логов, если её нет
    os.makedirs('logs', exist_ok=True)

    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()
