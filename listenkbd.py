# Copyright (c) 2010 Pablo Seminario <pabluk@gmail.com>
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
import logging
import threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

class ListenKbd(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Thread created")

        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

        if not self.record_dpy.has_extension("RECORD"):
            self.logger.error("RECORD extension not found.")
            sys.exit(1)

        self.ctx = self.record_dpy.record_create_context(
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

    def run(self):
        self.logger.debug("Thread started.")
        self.record_dpy.record_enable_context(self.ctx, self.record_activity)

    def record_activity(self, reply):

        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            self.logger.warning(
                "* received swapped protocol data, cowardly ignored"
            )
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,
                                    self.record_dpy.display, None, None)
            #self.logger.debug("Event type: %s" % event.type)
            if event.type == X.KeyPress:
                self.logger.debug("Key pressed")
                return
            if event.type == X.ButtonPress:
                self.logger.debug("Mouse button pressed")
                return

    def stop(self):
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
        self.record_dpy.record_free_context(self.ctx)
        self.logger.debug("Thread stopped.")
