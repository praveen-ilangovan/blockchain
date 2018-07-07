import logging

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt="%(levelname)s: %(msg)s"):
        super(CustomFormatter, self).__init__(fmt)

    def format(self, record):
        original_format = self._fmt

        if record.levelno in (logging.CRITICAL, logging.ERROR):
            self._fmt = '-'*80
            self._fmt += "\n[%(levelname)s] : File %(pathname)s, line %(lineno)d, in %(funcName)s\n\t -> %(message)s\n"
            self._fmt += '-'*80
        else:
            self._fmt = "[%(levelname)s] : %(message)s"

        result = super(CustomFormatter, self).format(record)
        self._fmt = original_format
        return result

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

# Handler
handler = logging.StreamHandler()

# create formatter and add it to the handlers
formatter = CustomFormatter()
handler.setFormatter(formatter)

LOG.addHandler(handler)
