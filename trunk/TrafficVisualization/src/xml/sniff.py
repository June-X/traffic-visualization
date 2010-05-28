#! /usr/bin/env python
"""
Example to sniff all HTTP traffic on eth0 interface:
    sudo ./sniff.py eth0 "port 80"
"""

import sys
from urlparse import urlparse
import pcap
import string
import time
import socket
import struct
import dpkt
import re
from time import strftime
from datetime import datetime

hosts=[]
PORT=50008
#s,conn,addr=None

protocols={socket.IPPROTO_TCP:'tcp',
            socket.IPPROTO_UDP:'udp',
            socket.IPPROTO_ICMP:'icmp'}

def print_packet(pktlen, data, timestamp):
    if not data:
        return

    eth=dpkt.ethernet.Ethernet(data)
    ip=eth.data
    tcp=ip.data

    if tcp.dport == 80 and len(tcp.data) > 0:
        dst=pcap.ntoa(struct.unpack('i',ip.dst)[0])
        """
        try:
            name=socket.gethostbyaddr(dst)[0]
        except socket.herror:
            name=dst
        """
        name=dst
        try:
            http = dpkt.http.Request(tcp.data)
            host = dst + http.headers['host']
        except:
            http = name
            host = dst+name

        try:
            message= '[%s%s]\n' % (http.headers['host'],http.uri) 
        except:
            message= '[%s]\n' % (http)
        print message
        logged_msg = message.strip("[")
        logged_msg = logged_msg.rstrip("]")
        current_time = strftime("%Y-%m-%d %H:%M:%S")
        current_time += "." + str(datetime.now().microsecond)
        f.write(current_time + " " + dst + " " + logged_msg + "\n")


        #if not host in hosts:
            #conn.send(message)
            #hosts.append(host)

#    rcv=conn.recv(1024)
#    if rcv:
#        if re.match("quit",rcv):
#            sys.exit(0)

if __name__=='__main__':
    if len(sys.argv)>1:
        name=sys.argv[1]       
    if len(sys.argv)>2:
        PORT=int(sys.argv[2])
	global f 
    f = open(name, "a")
	
    devs = pcap.findalldevs()
    i=0
    for eth in devs:
        print " %d - %s" %(i,devs[i][0])
        i+=1
    sel=input(" Select interface: ")
    dev=devs[sel][0]
	
    """
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',PORT))
    s.listen(1)
    print "Waiting for connection..."
    conn,addr=s.accept()
    print "Client succesfully connected!\n"
    """    

    p = pcap.pcapObject()
    net, mask = pcap.lookupnet(dev)
    p.open_live(dev, 1600, 0, 100)
    p.setfilter('tcp dst port 80',0,0)
    #p.setnonblock(1)
    print "Listening on %s: \n" % (dev)
    try:
        while 1:
            p.dispatch(1, print_packet)

        # the loop method is another way of doing things
            #p.loop(1, print_packet)

        # as is the next() method
        # p.next() returns a (pktlen, data, timestamp) tuple 
        #    apply(print_packet,p.next())
    except KeyboardInterrupt:
        #print '%s' % sys.exc_type
        print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()
        print 'quit'
        #conn.send('quit\n')
        #conn.close()
        f.close()

