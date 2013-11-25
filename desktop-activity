# Copyright (c) 2013 Pablo SEMINARIO <pablo@seminar.io>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import time
import signal
import socket
import logging
import threading

from Xlib import X, display
from Xlib.ext import record
from Xlib.protocol import rq


CARBON_SERVER = '192.168.1.100'
CARBON_PORT = 2003
SEND_INTERVAL = 60

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s',
                    level=logging.INFO)


class RecordActivity(threading.Thread):
    def __init__(self, counter, logger):
        threading.Thread.__init__(self)
        self.counter = counter
        self.logger = logger

        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

        if not self.record_dpy.has_extension("RECORD"):
            self.logger.error("RECORD extension not found.")
            sys.exit(1)

        xspecs = [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.ButtonPress),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }]
        self.ctx = self.record_dpy.record_create_context(0, [record.AllClients], xspecs)

    def record_activity(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            # received swapped protocol data, cowardly ignored
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return
        data = reply.data
        while len(data):
            ef = rq.EventField(None)
            event, data = ef.parse_binary_value(data, self.record_dpy.display,
                                                None, None)
            if event.type == X.KeyPress:
                self.logger.debug("Key pressed")
                self.counter['keyboard'] += 1
                return
            if event.type == X.ButtonPress:
                self.logger.debug("Mouse button pressed")
                self.counter['mouse'] += 1
                return

    def run(self):
        self.logger.debug("Thread started.")
        self.record_dpy.record_enable_context(self.ctx, self.record_activity)

    def stop(self):
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
        self.record_dpy.record_free_context(self.ctx)
        self.logger.debug("Stop record activity.")


class SendActivityTimer(threading.Thread):
    def __init__(self, counter, logger):
        threading.Thread.__init__(self)
        self.counter = counter
        self.logger = logger
        self.event = threading.Event()
        self.hostname = socket.gethostname()

        self.sock = socket.socket()
        try:
            self.sock.connect((CARBON_SERVER, CARBON_PORT))
        except socket.error:
            self.logger.error("Couldn't connect to %s on port %d."
                              % (CARBON_SERVER, CARBON_PORT))
            sys.exit(1)

    def send_data(self):
        timestamp = int(time.time())
        message = ''
        for metric, value in self.counter.items():
            message += 'desktop.%s.%s %d %d\n' % (self.hostname, metric, value, timestamp)
        self.logger.info("Sending data: %s" % [message])
        self.sock.sendall(message)

    def run(self):
        while not self.event.wait(SEND_INTERVAL):
            self.send_data()

    def stop(self):
        self.logger.debug("Stop send activity.")
        self.event.set()


def main():
    logger = logging.getLogger(__name__)
    counter = {
        'keyboard': 0,
        'mouse': 0,
    }

    def shutdown(signal, frame):
        logger.debug("Shutdown...")
        thread1.stop()
        thread2.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    thread1 = RecordActivity(counter, logger)
    thread2 = SendActivityTimer(counter, logger)

    thread1.start()
    thread2.start()

    signal.pause()


if __name__ == '__main__':
    main()
