from __main__ import plux, time

class BiosignalsPLUX(plux.MemoryDev):
    new_data_input = []
    data_buffer = []
    prev_data_buffer = []
    buffer_size = 10

    # callbacks override
    def onRawFrame(self, nSeq, data):
        self.new_data_input.insert(0, list((nSeq,)+data))
        if nSeq % self.buffer_size == 0:
            self.data_buffer = self.new_data_input
            self.new_data_input = []
        return False

    def onEvent(self, event):
        if type(event) == plux.Event.DigInUpdate:
            print 'Digital input event - Clock source:', event.timestamp.source, \
                  ' Clock value:', event.timestamp.value, ' New input state:', event.state
        elif type(event) == plux.Event.SchedChange:
            print 'Schedule change event - Action:', event.action, \
                  ' Schedule start time:', event.schedStartTime
        elif type(event) == plux.Event.Sync:
            print 'Sync event:'
            for tstamp in event.timestamps:
                print ' Clock source:', tstamp.source, ' Clock value:', tstamp.value
        elif type(event) == plux.Event.SignalGood:
            print "SignalGood"
        elif type(event) == plux.Event.Disconnect:
            print 'Disconnect event - Reason:', event.reason
            return True
        return False

    def onInterrupt(self, param):
        print 'Interrupt:', param
        return False

    def onTimeout(self):
        print 'Timeout'
        return False

    #ServerBIT data_handler
    def read(self):
        return self.data_buffer

    def request_new_seq(self, data_buffer):
        self.prev_data_buffer = data_buffer
