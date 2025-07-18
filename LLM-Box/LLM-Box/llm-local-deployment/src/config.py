# This file contains the project configuration settings, such as download sources and storage paths.

class Config:
    MODEL_DOWNLOAD_URL = "https://example.com/models/"
    MODEL_STORAGE_PATH = "./models/"
    DATA_STORAGE_PATH = "./data/"
    VERSION_CONTROL_PATH = "./versions/"
    LOGGING_LEVEL = "INFO"
    TIMEOUT = 30  # seconds
    MAX_RETRIES = 3

    @staticmethod
    def get_model_path(model_name):
        return f"{Config.MODEL_STORAGE_PATH}{model_name}"

    @staticmethod
    def get_data_path(data_name):
        return f"{Config.DATA_STORAGE_PATH}{data_name}"