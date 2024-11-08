import logging

class LogFile:
    """
    Class for logging messages to a specified file.
    Attributes:
    - logFilePath (str): The path where log messages will be stored.
    Methods:
    - log_info(message): Logs an info-level message.
    - log_error(message): Logs an error-level message.
    """

    def __init__(self, path, level=logging.INFO):
        """
        Initializes the LogFile class with the specified path and log level.

        Parameters:
        - path (str): File path for the log file.
        - level (int): Logging level (default is logging.INFO).
        """
        self.logFilePath = path
        logging.basicConfig(
            filename=self.logFilePath,
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_info(self, message):
        """
        Logs an info-level message.

        Parameters:
        - message (str): Message to be logged at info level.
        """
        logging.info(message)

    def log_error(self, message):
        """
        Logs an error-level message.

        Parameters:
        - message (str): Message to be logged at error level.
        """
        logging.error(message)

if __name__ == '__main__':
    log = LogFile('log/lidar_logs.log')
