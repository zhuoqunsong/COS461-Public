####################################################
# DVrouter.py
# Names: Yang Song, Zhuo Qun Song
# NetIds: yangsong, zsong
#####################################################

import sys
from collections import defaultdict, namedtuple
from router import Router
from packet import Packet
from json import dumps, loads

INFINITY = 16

def _table_string(routingTable):
	"""Turn routing table into string format."""
	result = []
	for address in routingTable:
		cost = routingTable[address]['cost']
		port = routingTable[address]['port']
		result.append('{}%{}&{}'.format(address, cost, port))
	return '#'.join(result)

class DVrouter(Router):
	"""Distance vector routing protocol implementation."""

	def __init__(self, addr, heartbeatTime):
		"""TODO: add your own class fields and initialization code here"""
		Router.__init__(self, addr)  # initialize superclass - don't remove
		self.heartbeatTime = heartbeatTime # heartbeat time
		self.sentTime = 0 # time last sent
		self.currentTime = 0 # current time
		self.routingTable = dict() # routing table
		self.routingTable[self.addr] = {'port': None, 'cost': 0}
		self.neighbors = set() # set of neighbors
		# self.packeta = [] # content of packets received (for debugging purposes)

	def handlePacket(self, port, packet):
		"""TODO: process incoming packet"""
		if packet.isRouting(): 
			src = packet.srcAddr # source
			dst = packet.dstAddr # destination
			content = packet.content # content
			# self.packeta.append(content) # for debugging
			table = content.split('#')
			for entry in table:
				router = entry.split('%')[0]
				if router in self.routingTable: # Update our routing table if less cost
					dist = self.routingTable[src]['cost']
					cost = int(entry.split('%')[1].split('&')[0]) + dist
					port = self.routingTable[src]['port']
					if cost > self.routingTable[router]['cost'] and self.routingTable[router]['port'] == port:
						self.routingTable[router]['cost'] = INFINITY
					if cost < self.routingTable[router]['cost']:
						self.routingTable[router]['port'] = port
						self.routingTable[router]['cost'] = cost
				else: # Add to our routing table
					# DO ADDRESS STUFF TOO
					dist = self.routingTable[src]['cost']
					cost = int(entry.split('%')[1].split('&')[0]) + dist
					port = self.routingTable[src]['port']
					self.routingTable[router] = {'port': port, 'cost': cost}
		else: # packet.isTraceroute(): send packet to destination
			dst = packet.dstAddr
			if dst in self.routingTable:
				port = self.routingTable[dst]['port']
				self.send(port, packet)


	def handleNewLink(self, port, endpoint, cost):
		"""TODO: handle new link"""
		self.routingTable[endpoint] = {'port': port, 'cost': cost, 'ID': port} # add link to routing table
		self.neighbors.append((endpoint,cost,port)) # add new endpoint to neighbors
		for router in self.neighbors: # send new routing table to all neighbors
			if router[0] == self.addr: continue
			porta = self.routingTable[router[0]]['port']
			packets = Packet(Packet.ROUTING, self.addr, router[0], _table_string(self.routingTable))
			self.send(porta, packets)

	def handleRemoveLink(self, port):
		"""TODO: handle removed link"""
		address = None # address corresponds to address of removed port
		for add in self.neighbors:
			if self.routingTable[add[0]]['ID'] == port:
				address = add[0]
		for router in self.routingTable:
			if self.routingTable[router]['port'] == port:
				self.routingTable[router]['cost'] = INFINITY
		self.neighbors.remove(address)


	def handleTime(self, timeMillisecs):
		"""TODO: handle current time"""
		self.currentTime = timeMillisecs # handle current time
		if self.sentTime == 0: # periodically send routing table to all neighbors
			for router in self.neighbors:
				if router[0] == self.addr: continue
				porta = self.routingTable[router[0]]['port']
				packets = Packet(Packet.ROUTING, self.addr, router[0], _table_string(self.routingTable))
				self.send(porta, packets)
		if self.currentTime - self.sentTime > self.heartbeatTime:
			for router in self.neighbors:
				if router[0] == self.addr: continue
				porta = self.routingTable[router[0]]['port']
				packets = Packet(Packet.ROUTING, self.addr, router[0], _table_string(self.routingTable))
				self.send(porta, packets)
			self.sentTime = self.currentTime


	def debugString(self):
		"""TODO: generate a string for debugging in network visualizer"""
		return "Mirror router: address {}, time {}, heartbeat {}, table {}, neighbors {}, string{}"\
		.format(self.addr, self.currentTime, self.heartbeatTime, self.routingTable, self.neighbors, \
			_table_string(self.routingTable))
