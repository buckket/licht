#!/usr/bin/python

'''
Created on Aug 13, 2012

@author: teddydestodes, MrLoom
'''
import socket
import struct
import pickle
import argparse
import hashlib

class LichtClient(object):
    
    def __init__(self,address, port):
        self.sock = socket.socket( socket.AF_INET, # Internet
                              socket.SOCK_DGRAM ) # UDP
        self.address = address
        self.port = port
    
    def sendCommand(self, command, params):
        pickled = pickle.dumps([command,params])
        checksum = hashlib.sha256(pickled + "TESTSALT").hexdigest()[:16]
        stream = checksum + pickled
        self.sock.sendto(stream, (self.address, self.port))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lichterkette!!!!',
                                     epilog='Penis, LOL!')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    authparser = subparsers.add_parser('fade', help='fades color')
    authparser.add_argument('r')
    authparser.add_argument('g')
    authparser.add_argument('b')
    offparser = subparsers.add_parser('off', help='turns all off')
    nightparser = subparsers.add_parser('night', help='turns on night mode')
    turingparser = subparsers.add_parser('turing', help='turns on turing mode')
    args = parser.parse_args()
    client = LichtClient('192.168.2.145', 16321)
    if args.command == 'off':
        client.sendCommand(3, ((0,0,0)))
    elif args.command == 'turing':
        client.sendCommand(3, ((0xff,0,0xff)))
    elif args.command == 'night':
        client.sendCommand(3, ((0x10,0,0)))
    elif args.command == 'fade':
        client.sendCommand(3, ((int(args.r),int(args.g),int(args.b))))