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
import logging
from socket import socket

from Xlib import X, display
from Xlib.ext import record
from Xlib.protocol import rq



CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 20030

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s', level=logging.DEBUG)


def main():
    logger = logging.getLogger(__name__)
    local_dpy = display.Display()
    record_dpy = display.Display()

    if not record_dpy.has_extension("RECORD"):
        logger.error("RECORD extension not found.")
        sys.exit(1)

    ctx = record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.ButtonPress),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }])

    counters = {
        'desktop.host1.keyboard': 0,
        'desktop.host1.mouse': 0,
    }
    sock = socket()
    try:
        sock.connect((CARBON_SERVER,CARBON_PORT))
    except:
        print "Couldn't connect to %(server)s on port %(port)d." % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
        sys.exit(1)

    def record_activity(reply):
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
            event, data = rq.EventField(None).parse_binary_value(data,
                                    record_dpy.display, None, None)
            if event.type == X.KeyPress:
                logger.debug("Key pressed")
                counters['desktop.host1.keyboard'] += 1
                return
            if event.type == X.ButtonPress:
                logger.debug("Mouse button pressed")
                counters['desktop.host1.mouse'] += 1
                return

    def send_data(signal, frame):
        timestamp = int(time.time())
        message = ''
        for metric, value in counters.items():
            message += '%s %d %d\n' % (metric, value, timestamp)
        counters['desktop.host1.keyboard'] = 0
        counters['desktop.host1.mouse'] = 0
        logger.debug("Sending:\n%s" % message)
        sock.sendall(message)

    def signal_handler(signal, frame):
        sock.close()
        local_dpy.record_disable_context(ctx)
        local_dpy.flush()
        record_dpy.record_free_context(ctx)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, send_data)

    record_dpy.record_enable_context(ctx, record_activity)


if __name__ == '__main__':
    main()
