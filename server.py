'''
Created on Aug 13, 2012

@author: teddydestodes, MrLoom
'''

import socket, time, struct
import threading
import pickle
import spidev
import hashlib

class RefreshThread(threading.Thread):
    SPILock = threading.Lock()
    
    def __init__(self, length):
        threading.Thread.__init__(self)
        self.buffer = []
        self.length = length
        for i in range(0,length*3):
            self.buffer.append(0)
        self.spi = spidev.SpiDev(2,0)
        self.spi.max_speed_hz = 1000000
    
    def run(self):
        while True:
            self.flush_buffer()
            time.sleep(.5)
            
    def flush_buffer(self):
        RefreshThread.SPILock.acquire()
        self.spi.writebytes(self.buff)
        time.sleep(0.0005)
        RefreshThread.SPILock.release()
        
    def set_color(self, color, pixel=None, flush=True):
        if pixel != None:
            self.buffer[pixel*3]   = color[0]
            self.buffer[pixel*3+1] = color[1]
            self.buffer[pixel*3+2] = color[2]
        else:
            for p in range(0,self.length):
                self.buffer[p*3] = color[0]
                self.buffer[p*3+1] = color[1]
                self.buffer[p*3+2] = color[2]
        if flush:
            self.flush_buffer()

    def push_color(self, color):
        self.buffer.insert(0,color[2])
        self.buffer.insert(0,color[1])
        self.buffer.insert(0,color[0])
        self.buffer.pop()
        self.buffer.pop()
        self.buffer.pop()
        self.flush_buffer()
        
    def fade(self, color):
        steps = 50
        for s in range(0,steps):
            for p in range(0, self.length):
                self.set_color(self.avg_color(self.get_color(p), color, steps-s), p, flush=False)
            self.flush_buffer()
        self.set_color(color)
        

    def get_color(self, pixel):
        return [self.buffer[pixel*3],self.buffer[pixel*3+1],self.buffer[pixel*3+2]]

    def avg_color(self, color, color2, weight=1):
        return ((color[0]*weight+color2[0])/(1+weight),(color[1]*weight+color2[1])/(1+weight),(color[2]*weight+color2[2])/(1+weight))

class RecieveThread(threading.Thread):
    
    def __init__(self,address,port, refresh):
        threading.Thread.__init__(self)
        self.sock = socket.socket( socket.AF_INET,
                                   socket.SOCK_DGRAM )
        self.sock.bind( (address,port) )
        self.rthread = refresh
    
    def run(self):
        while True:
            data, addr = self.sock.recvfrom( 1024 ) # buffer size is 1024 bytes
            
            checksumData = data[:16]
            pickledData = data[16:]
            
            checksum = hashlib.sha256(pickledData + "TESTSALT").hexdigest()[:16]
            if checksum != checksumData:
                continue
            
            t = pickle.loads(pickledData)   
            if t[0] == 0:
                self.command_off()
            if t[0] == 1:
                self.command_setcolor(t[1])
            if t[0] == 2:
                self.command_pushcolor(t[1])
            if t[0] == 3:
                self.command_fade(t[1])
    def command_off(self):
        self.rthread.set_color((0,0,0))
    def command_setcolor(self, param):
        self.rthread.set_color(param[0],param[1])
    def command_pushcolor(self, param):
        self.rthread.push_color(param[0])
    def command_fade(self, param):
        self.rthread.fade(param)
class LichtServer(object):
    '''
    classdocs
    '''


    def __init__(self,address,port, size):
        '''
        Constructor
        '''
        self.refresh_thread = RefreshThread(size)
        self.recieve_thread = RecieveThread(address,port, self.refresh_thread)
        self.recieve_thread.setDaemon(True)
        self.refresh_thread.setDaemon(True)
        self.recieve_thread.start() 
        self.refresh_thread.start()
        
        
                
server = LichtServer('localhost',16321, 25)