# -*- coding: utf-8 -*-

"""固定4字节头的编码/解码器(fix-4-bytes-header),各种编码都可以用这个"""

import struct


class Fix4HEncoder(object):
    """固定4bytes长度头编码器"""
    
    def __init__(self, dumps=None):
        self.dumps = dumps or (lambda data: data)
        
    def encode(self, msg):
        body = self.dumps(msg)
        length = len(body)
        data = struct.pack(">I%ds" % length, length, body)
        return data


class Fix4HDecoder(object):
    """固定4bytes长度头解码器"""
        
    _buf = ""
    
    def __init__(self, loads=None):
        self.loads = loads or (lambda data: data)
    
    def decode(self, data):
        buf = self._buf =  self._buf + data
        while True:
            if not buf:
                raise StopIteration
            if len(buf) < 4:
                yield ("short", "header")
                break
            length, = struct.unpack(">I", buf[:4])
            if len(buf) < length + 4:
                yield ("short", "message")
                break
            body = buf[4:4+length]
            buf = buf[4+length:]
            self._buf = buf
            msg = self.loads(body)
            yield ("msg", msg)


if __name__ == "__main__":
    import cPickle as pickle
    # test pickle
    encode = Fix4HEncoder(pickle.dumps).encode
    decoder = Fix4HDecoder(pickle.loads)
    
    data = encode({"a":[1,2,3]})
    print repr(data)
    
    for d in data * 2:
        for m in decoder.decode(d):
            print m


__all__ = ["Fix4HEncoder", "Fix4HDecoder"]