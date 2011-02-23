# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0
#
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is Pika.
#
# The Initial Developers of the Original Code are LShift Ltd, Cohesive
# Financial Technologies LLC, and Rabbit Technologies Ltd.  Portions
# created before 22-Nov-2008 00:00:00 GMT by LShift Ltd, Cohesive
# Financial Technologies LLC, or Rabbit Technologies Ltd are Copyright
# (C) 2007-2008 LShift Ltd, Cohesive Financial Technologies LLC, and
# Rabbit Technologies Ltd.
#
# Portions created by LShift Ltd are Copyright (C) 2007-2009 LShift
# Ltd. Portions created by Cohesive Financial Technologies LLC are
# Copyright (C) 2007-2009 Cohesive Financial Technologies
# LLC. Portions created by Rabbit Technologies Ltd are Copyright (C)
# 2007-2009 Rabbit Technologies Ltd.
#
# Portions created by Tony Garnock-Jones are Copyright (C) 2009-2010
# LShift Ltd and Tony Garnock-Jones.
#
# All Rights Reserved.
#
# Contributor(s): ______________________________________.
#
# Alternatively, the contents of this file may be used under the terms
# of the GNU General Public License Version 2 or later (the "GPL"), in
# which case the provisions of the GPL are applicable instead of those
# above. If you wish to allow use of your version of this file only
# under the terms of the GPL, and not to allow others to use your
# version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the
# notice and other provisions required by the GPL. If you do not
# delete the provisions above, a recipient may use your version of
# this file under the terms of any one of the MPL or the GPL.
#
# ***** END LICENSE BLOCK *****

"""
Send n messages and confirm you can retrieve them with Basic.Consume
"""
import nose
import os
import sys
sys.path.append('..')
sys.path.append(os.path.join('..', '..'))

import support.tools as tools
from pika.adapters import SelectConnection

HOST = 'localhost'
MESSAGES = 10
PORT = 5672


class TestSendConsume(tools.AsyncPattern):

    def __init__(self):
        tools.AsyncPattern.__init__(self)
        self._sent = list()
        self._received = list()

    @nose.tools.timed(2)
    def test_send_and_consume(self):
        self.connection = self._connect(SelectConnection, HOST, PORT)
        self.connection.ioloop.start()
        if self._timeout:
            assert False, "Test timed out"
        if len(self._sent) != MESSAGES:
            assert False, "We did not send the expected qty of messages: %i" %\
                          len(self._sent)
        if len(self._received) != MESSAGES:
            assert False, "Did not receive the expected qty of messages: %i" %\
                          len(self._received)
        for message in self._received:
            if message not in self._sent:
                print message
                print self._sent
                print self._received
                assert False, 'Received a message we did not send.'
        for message in self._sent:
            if message not in self._received:
                assert False, 'Sent a message we did not receive.'

    def _on_channel(self, channel):
        self.channel = channel
        self._queue_declare()

    @tools.timeout
    def _on_queue_declared(self, frame):
        for x in xrange(0, MESSAGES):
            self._sent.append(self._send_message())
        self.channel.basic_consume(self._on_message, queue=self._queue)

    def _on_message(self, channel_number, method, header, body):
        self._received.append(body)
        if len(self._received) == MESSAGES:
            self.connection.add_on_close_callback(self._on_closed)
            self.connection.close()

if __name__ == "__main__":
    nose.runmodule()