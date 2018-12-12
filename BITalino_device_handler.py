from __main__ import *

def tostring(data):
    """
    :param data: object to be converted into a JSON-compatible `str`
    :type data: any
    :return: JSON-compatible `str` version of `data`

    Converts `data` from its native data type to a JSON-compatible `str`.
    """
    dtype=type(data).__name__
    if dtype=='ndarray':
        if numpy.shape(data)!=(): data=data.tolist() # data=list(data)
        else: data='"'+data.tostring()+'"'
    elif dtype=='dict' or dtype=='tuple':
        try: data=json.dumps(data, sort_keys=True)
        except: pass
    elif dtype=='NoneType':
        data=''
    elif dtype=='str' or dtype=='unicode':
        data=json.dumps(data, sort_keys=True)

    return str(data)

class BITalino_handler:
    device_data = []
    async def read_data(self, device, ch_mask, srate, nsamples, labels):
        ch_mask = numpy.array(ch_mask) - 1
        cols = numpy.arange(len(ch_mask)+5)
        labels = ["nSeq", "I1", "I2", "O1", "O2","A1","A2","A3","A4","A5","A6"]
        # print(labels)
        try:
            data = device.read(nsamples)
            res = "{"
            for i in cols:
                idx = i
                if (i > 4): idx = ch_mask[i - 5] + 5
                res += '"' + labels[idx] + '":' + tostring(data[:, i]) + ','
            res = res[:-1] + "}"
            # print(res)
            print('streaming from: %s' % device.macAddress)
            self.device_data.append(data[0][0])
        except Exception as e:
            print(e)
            print ("connection to %s dropped" % device)
            raise Exception("BITalinoConnectionError")
        await asyncio.sleep(0.0)
