####################################################
# mb.py
# Names: Yang Song, Zhuo Qun Song
# NetIds: yangsong, zsong
#####################################################

import sys
import threading
from scapy.all import sniff as scasniff, sendp
from scapy.all import *
from collections import defaultdict
from random import random

def fprint(x):
    print x
    sys.stdout.flush()

class PacketHandler:

    def __init__(self, intf_list, conn_intf_dict, ip_map):
        self.intf_list = intf_list
        self.conn_intf_dict = conn_intf_dict
        self.ip_map = ip_map
        # TODO: Create and initialize additional instance variables
        #       for detection and mitigation
        self.requests = defaultdict(set)
        self.responses = defaultdict(int)

        

    def start(self):
        for (in_intf, out_intf) in self.intf_list:
            t = threading.Thread(target = self.sniff, args = (in_intf, out_intf))
            t.start()


    def incoming(self, pkt, in_intf, out_intf):
        mac1 = self.conn_intf_dict[in_intf]
        mac2 = self.conn_intf_dict[out_intf]

        res = (pkt[Ether].src in mac1 or
               pkt[Ether].dst in mac2 or
                pkt[Ether].dst == "ff:ff:ff:ff:ff:ff")
        return res


    def handle_packet(self, in_intf, out_intf, pkt):
        # Handling ARP (DO NOT CHANGE)
        if (pkt[Ether].dst == "ff:ff:ff:ff:ff:ff"):
            if(pkt[Ether].type == 2054 and
                pkt[ARP].psrc in self.ip_map[in_intf] and
                pkt[ARP].pdst in self.ip_map[out_intf]):
                arp_header = pkt[ARP]
                arp_header.op = 2
                arp_header.hwdst = arp_header.hwsrc
                pdst = arp_header.pdst
                hwsrc =  "00:00:00:00:00:0%s" % pdst[-1]
                arp_header.hwsrc = hwsrc
                arp_header.pdst = arp_header.psrc
                arp_header.psrc = pdst
                pkt = Ether(src=hwsrc, dst=pkt[Ether].src)/arp_header
                sendp(pkt, iface=in_intf, verbose = 0)
            return

	    # TODO: process the packet to perform DNS reflection attack
            #       detection and mitigation

        # check whether pkt is an IP packet
        if IP in pkt:
            # get source IP addresses
            src_ip = pkt[IP].src
            # get destionation IP addresses
            dst_ip = pkt[IP].dst

        # check whether pkt is a DNS packet
        if DNS in pkt:

            # check if pkt is a DNS response or request
            is_response = pkt[DNS].qr == 1
            is_request = pkt[DNS].qr == 0

            # get ID of DNS request/response
            dns_id = pkt[DNS].id

            # DNS packet going out interface mb-eth0 (toward h1 & h4)
            if out_intf == 'mb-eth0' and is_response:
                # Check whether there has been a request with same ID number from destination IP
                if dns_id not in self.requests[dst_ip]:
                    self.responses[dst_ip] += 1
                    #print('r{}'.format(self.responses))
                    if self.responses[dst_ip] > 200:
                        r = random()
                        #print(r)
                        if r < 0.9: 
                            return
                
            if out_intf == 'mb-eth1' and is_request:
                #print(src_ip, dns_id)
                self.requests[src_ip].add(dns_id)

	    # Forwarding the traffic to the target network (DO NOT CHANGE)
        sendp(pkt, iface=out_intf, verbose = 0)

        
    def sniff(self, in_intf, out_intf):
        scasniff(iface=in_intf, prn = lambda x : self.handle_packet(in_intf, out_intf, x),
                  lfilter = lambda x : self.incoming(x, in_intf, out_intf))


if __name__ == "__main__":
    intf1 = "mb-eth0"
    conn_mac1 = ["00:00:00:00:00:01", "00:00:00:00:00:04"]
    ip_list_1 = ["10.0.0.1", "10.0.0.4"]
    intf2 = "mb-eth1"
    ip_list_2 = ["10.0.0.2", "10.0.0.3"]
    conn_mac2 = ["00:00:00:00:00:02", "00:00:00:00:00:03"]

    intf_list = [(intf1, intf2), (intf2, intf1)]
    conn_intf_dict = {intf1 : conn_mac1, intf2 : conn_mac2}
    ip_map = {intf1 : ip_list_1, intf2 : ip_list_2}
    handler = PacketHandler(intf_list, conn_intf_dict, ip_map)
    handler.start()
