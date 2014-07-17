# -*- coding: utf-8 -*-

"""使用makefile的,固定4字节头的编码/解码器(makefile-fix-4-bytes-header),各种编码都可以用这个
: 把socket 变为 makefile 可以使用 file io 接口读写,
: 可以实现类似 golang 的 io.ReadFull, io.ReadAtLeast 等
"""

import struct


class MF4HEncoder(object):
    """固定4bytes长度头编码器"""
    
    def __init__(self, dumps=None):
        self.dumps = dumps or (lambda data: data)
        
    def encode(self, msg):
        body = self.dumps(msg)
        length = len(body)
        data = struct.pack(">I%ds" % length, length, body)
        return data


class MF4HDecoder(object):
    """固定4bytes长度头解码器"""
        
    def __init__(self, sock, loads=None, header_timeout=None, msg_timeout=None):
        self.sock_file = sock.makefile(mode="r")
        self.loads = loads or (lambda data: data)
        self.header_timeout = header_timeout
        self.msg_timeout = msg_timeout
        self.st_header = struct.Struct(">I")
    
    def decode(self):
        while True:
            # 读取4bytes头,如果没有读到4bytes会一直阻塞 ,直到超时.TODO: header timeout
            header = self.sock_file.read(4)
            length, = self.st_header.unpack(header)
            # 读取length bytes消息体, TODO: msg timeout
            body = self.sock_file.read(length)
            msg = self.loads(body)
            yield ("msg", msg)
            
    def decode2(self):
        """和decode相比, 这个是Mixin形式,使用类要继承 MF4HDecoder"""
        while True:
            # 读取4bytes头,如果没有读到4bytes会一直阻塞 ,直到超时.TODO: header timeout
            header = self.sock_file.read(4)
            length, = self.st_header.unpack(header)
            # 读取length bytes消息体, TODO: msg timeout
            body = self.sock_file.read(length)
            msg = self.loads(body)
            self.on_msg(msg)
    
    def on_msg(self, msg):
        raise NotImplementedError()
    

if __name__ == "__main__":
    from gevent.socket import create_connection
    import cPickle as pickle
    # test pickle    
    sock = create_connection(("127.0.0.1", 1234))
    encode = MF4HEncoder(pickle.dumps).encode
    decoder = MF4HDecoder(sock, pickle.loads)
    data = encode({"a":[1,2,3]})
    print repr(data)
    sock.sendall(data)
    for data in decoder.decode():
        print data


__all__ = ["MF4HEncoder", "MF4HDecoder"]