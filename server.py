'''
Created on Aug 13, 2012

@author: teddydestodes, MrLoom
'''

import socket, time, struct
import threading
import pickle
import hashlib

pGREEN = "ehrpwm.2:1"
pRED = "ehrpwm.2:0"
pBLUE = "ehrpwm.1:0"
FREQUENCY = 1000000


class RecieveThread(threading.Thread):
                
    def __init__(self, address, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket( socket.AF_INET,
                                   socket.SOCK_DGRAM )
        self.sock.bind((address, port))
        
    def fade(self, color):
        steps = 50
        for s in range(0,steps):
            self.set_color(self.avg_color(self.get_color(), color, steps-s))
            time.sleep(0.001)
        self.set_color(color)

    def get_color(self):
        fw = file("/sys/class/pwm/" + pRED + "/duty_ns", "r")
        red = 255 - int(int(fw.read()) * 255 / FREQUENCY)
        fw.close()
        fw = file("/sys/class/pwm/" + pGREEN + "/duty_ns", "r")
        green = 255 - int(int(fw.read()) * 255 / FREQUENCY)
        fw.close()
        fw = file("/sys/class/pwm/" + pBLUE + "/duty_ns", "r")
        blue = 255 - int(int(fw.read()) * 255 / FREQUENCY)
        fw.close()
        return [red, green, blue]
    
    def set_color(self, color):
        red = FREQUENCY - (color[0] * FREQUENCY / 255)
        green = FREQUENCY - (color[1] * FREQUENCY / 255)
        blue = FREQUENCY - (color[2] * FREQUENCY / 255)
        fw = file("/sys/class/pwm/" + pRED + "/duty_ns", "w")
        fw.write("%d" % (red))
        fw.close()
        fw = file("/sys/class/pwm/" + pGREEN + "/duty_ns", "w")
        fw.write("%d" % (green))
        fw.close()
        fw = file("/sys/class/pwm/" + pBLUE + "/duty_ns", "w")
        fw.write("%d" % (blue))
        fw.close()
    
    def avg_color(self, color1, color2, weight=1):
        return ((color1[0]*weight+color2[0])/(1+weight),(color1[1]*weight+color2[1])/(1+weight),(color1[2]*weight+color2[2])/(1+weight))
    
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
                pass
            if t[0] == 3:
                self.command_fade(t[1])
                
    def command_off(self):
        self.set_color((0,0,0))
    def command_setcolor(self, param):
        self.set_color(param[0],param[1])
    def command_fade(self, param):
        self.fade(param)
        
class LichtServer(object):

    def __init__(self, address, port, size):
        self.recieve_thread = RecieveThread(address, port)
        self.recieve_thread.setDaemon(True)
        self.recieve_thread.start() 
                
server = LichtServer('192.168.178.56', 16321, 25)

while True:
    time.sleep(100)
