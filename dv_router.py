from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.dv = {}
        self.dv_neighbors = {}
        self.neighbor_link_weights = {}

    def handle_rx (self, packet, port):
        # Add your code here!
        if isinstance(packet, DiscoveryPacket):
        	if(packet.is_link_up):
        		available_route = RoutingUpdate()
        		self.dv[packet.src] = packet.latency
        		self.neighbor_link_weights[packet.src] = packet.latency
        		available_route.paths = self.dv
        		self.send(available_route, packet.src, flood=True)
        elif isinstance(packet, RoutingUpdate):
        	print "routing update"
        	self.dv_neighbors[packet.src] = packet.paths
        else:
        	self.send(packet, packet.dst, flood=True)


