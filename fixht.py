# -*- coding: utf-8 -*-

"""固定头尾编码/解码器(fix-header-tail)"""

import struct


class FixHTEncoder(object):
    """固定头尾编码器"""
    
    def __init__(self, header="", tail=""):
        self.header = header
        self.tail = tail
    
    def encode(self, msg):
        return self.header + msg + self.tail
    

class FixHTDecoder(object):
    """固定头尾解码器"""
    
    _buf = ""
    
    def __init__(self, header="", tail=""):
        self.header = header
        self.tail = tail
        
    def decode(self, data):
        buf = self._buf = self._buf + data
        while True:
            if not buf:
                raise StopIteration
            if len(buf) < len(self.header):
                yield ("short", "header")
                break
            if self.header:
                extra, h, rest = buf.partition(self.header)
                if not h: # 没找到头,弃包(已经接收的)
                    buf = ""
                    self._buf = ""
                    yield ("oops", "no header")
                    break
                buf = rest
            pos_tail = buf.find(self.tail)
            if pos_tail == -1:
                yield ("oops", "not find tail yet")
                break
            msg = buf[:pos_tail]
            buf = buf[pos_tail+len(self.tail):]
            self._buf = buf
            yield ("msg", msg)
            

if __name__ == "__main__":
    encode = FixHTEncoder("\xff\xff", "\n").encode
    decoder = FixHTDecoder("\xff\xff", "\n")
    
    data = encode("abcdef")
    print repr(data)
    
    for d in data * 2:
        for m in decoder.decode(d):
            print m


__all__ = ["FixHTEncoder", "FixHTDecoder"]