import logging

class SpongeLog():
    def __init__(self, logname):
        self.logname = "logs/" + logname
        logging.basicConfig(filename=self.logname,
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
        self.logger = logging.getLogger(logname)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def debug(self, msg):
        self.logger.debug(msg)
