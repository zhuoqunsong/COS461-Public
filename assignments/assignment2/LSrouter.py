####################################################
# LSrouter.py
# Names: Yang Song, Zhuo Qun Song
# NetIds: yangsong, zsong
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads

class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeatTime = heartbeatTime # heartbeat time
        self.currentTime = 0 # current time
        self.sentTime = 0
        self.routingTable = dict() # table of routers with their LSPs
        self.neighbors = [] # list of neighbors [(address, cost, port)]
        self.confirmed = dict() # final routing table, for dijkstra
        self.tentative = [] # for dijkstra
        self.debugtentative = [] # used for debugging only
        self.packeta = set() # set of routers which self has received info about (for debugging)


    def dijkstra(self):
        """Create confirmed from routing table"""
        self.confirmed = dict() # reset confirmed
        self.confirmed[self.addr] = {'cost': 0, 'port': 0} # Add 
        for neighs in self.neighbors:
            self.tentative.append(neighs)
        while self.tentative:
            self.tentative.sort(key=lambda x: -int(x[1]))
            lowest = self.tentative[-1]            
            self.tentative.pop()
            if lowest[0] in self.confirmed: 
                continue
            self.confirmed[lowest[0]] = {'cost': lowest[1], 'port': lowest[2]}

            if lowest[0] not in self.routingTable:
                pass
            else: 
                for neigh in self.routingTable[lowest[0]]['neighs'].keys():
                    if neigh in self.confirmed: 
                        continue
                    elif neigh.isupper(): 
                        self.tentative.append((neigh, lowest[1]+int(self.routingTable[lowest[0]]['neighs'][neigh]['cost']), lowest[2]))#'''self.routingTable[lowest[0]]['neighs'][neigh]['port']'''))
                    else: 
                        self.confirmed[neigh] = {'cost': lowest[1]+int(self.routingTable[lowest[0]]['neighs'][neigh]['cost']), 'port': lowest[2]}#'''self.routingTable[lowest[0]]['neighs'][neigh]['port']'''}

    def create_lsp(self):
        list_neigh = []
        for neighbor in self.neighbors:
            add, cost, port, _ = neighbor
            list_neigh.append('{}%{}%{}'.format(add, cost, port))
        neigh = '@'.join(list_neigh)
        neigh = '{}@{}@{}'.format(self.addr, neigh, self.currentTime)
        return Packet(Packet.ROUTING, self.addr, add, neigh)


    def flood(self, lsp):
        for neighbor in self.neighbors:
            add, cost, port, _ = neighbor
            source = lsp.srcAddr
            if add != source:
                self.send(port, lsp)
        pass    


    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isRouting(): # update routing table
            neighbors = packet.content.split('@')
            address = neighbors[0]
            time = neighbors[~0]
            ns = neighbors[1:-1]
            self.packeta.add(address)
            neighs = dict()
            for n in ns:
                ad, cost, port = n.split('%')
                neighs[ad] = {'cost': cost, 'port': port}
            if address in self.routingTable:
                if time > self.routingTable[address]['time']:
                    self.routingTable[address] = {'neighs' : neighs, 'time': time}
            else:
                self.routingTable[address] = {'neighs' : neighs, 'time': time}
            for nexts in self.neighbors:
                if nexts[0] != port and nexts[3] != packet.content:
                    print packet.content
                    self.send(nexts[-2], packet)
                    nexts = (nexts[0], nexts[1], nexts[2], packet.content)
        else: # if packet.isTraceroute(): send to destination
            dst = packet.dstAddr
            if dst in self.confirmed: # if destination in our table, then send
                port = self.confirmed[dst]['port']
                self.send(port, packet)


    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        #self.routingTable[endpoint] = {'port': port, 'cost': cost}
        self.neighbors.append((endpoint,cost,port, ""))
        self.flood(self.create_lsp())


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        address = None # address corresponds to address of removed port
        for add in self.neighbors:
            if self.routingTable[add[0]]['ID'] == port:
                address = add
        self.neighbors.remove(address)
        self.flood(self.create_lsp())
        pass


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        self.currentTime = timeMillisecs # handle current time
        if self.sentTime == 0 or self.currentTime - self.sentTime > self.heartbeatTime: # periodically send routing table to all neighbors
            self.dijkstra()
            self.sentTime = self.currentTime

    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        self.dijkstra()
        return "CONFIRM {}, Mirror router: address {}, time {}, heartbeat {}, table {}, neighbors {}, packeta {}, string {}, tentative {}"\
        .format(self.confirmed, self.addr, self.currentTime, self.heartbeatTime, self.routingTable, self.neighbors, self.packeta, \
            self.debugtentative, self.tentative)
