import threading
import time
import sys

class SpinnerThread(threading.Thread):
    def __init__(self, indent = 2, speed=0.15):
        super().__init__(target=self._spin)
        self.daemon = True
        self._indent = indent
        self._stopevent = threading.Event()
        self._speed = speed
        self._written = False

    def stop(self):
        self._stopevent.set()
        if self._written:
            self._clear_spin()

    def _print_spin(self, char):
        message = self._indent + char + self._indent
        print(message, end='', file=sys.stdout, flush=True)
        self._written = True

    def _clear_spin(self):
        message = '\b' * (len(self._indent) * 2 + 1)
        print(message, end='', file=sys.stdout, flush=True)
        self._written = False

    def _spin(self):
        while not self._stopevent.isSet():
            for t in '|/-\\':
                self._print_spin(t)
                time.sleep(self._speed)

                if self._written and not self._stopevent.isSet():
                    self._clear_spin()

                if self._stopevent.isSet():
                    break

