import timeit
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)

class Timer:
    # TODO - support passing log-level as a keyword parameter
    def __init__(self, message=None, extra=None):
        self.message = message
        self.extra = extra

    def __enter__(self):
        self.start = timeit.default_timer()
        return self

    def __exit__(self, *args):
        self.end = timeit.default_timer()
        self.interval = self.end - self.start
        if self.message:
            extra = {'duration': self.interval * 1000}
            extra.update(self.extra)
            log.debug(self.message, extra=extra)
