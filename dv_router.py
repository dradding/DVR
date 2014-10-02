from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.dv = {} # destination: (total cost to dest, next-hop)
        self.dv_neighbors = {} # neighbor: neighbor DV
        self.neighbor_ports = {} #Key is neighbor, value is ports
        self.neighbor_latency = {} #neighbor: link-latency

    def handle_rx (self, packet, port):
        # Add your code here!
        if isinstance(packet, DiscoveryPacket):
        	if(packet.is_link_up):
        		available_route = RoutingUpdate()
        		self.dv[packet.src] = packet.latency
        		self.neighbor_link_weights[packet.src] = packet.latency
        		self.neighbor_ports[packet.src] = port
        		available_route.paths = self.dv
        		self.send(available_route, packet.src, flood=False)
        	#add Else
        elif isinstance(packet, RoutingUpdate):
        	print "routing update"
        	self.dv_neighbors[packet.src] = packet.paths
        else: #Data packet, foward approroately
        	#Look up best path in DV, send to appropriate neighbor
        	self.send(packet, packet.dst, flood=False)

    def handle_dp(self, packet, port):
        if (packet.is_link_up):
            self.dv[]




        elif !(packet.is_link_up):


    def handle_ru(self):


    def update_dv(self, src, change_type): #src is the node that sent an updated dv
    	#Check to see if DV needs update. If updated, send routing update
    	#Check for changes when latency changes
    	#Eventually add Poison and Split Horizon
    	send_update = False #Set to True if  Routing Update should be sent
    	latency = self.neighbor_latency[src]
    	if change_type == "DP": #Only called when link is lost. When link is added, handle_rx will handle it
    		for key in self.dv:
    			if self.dv[key] == src:
    				for n in self.dv_neighbors: #n is a neighbor
    					if self.dv_neighbors[n].has_key(key) #if the n contains a key then a path exists
    						if self.dv_neighbors[n][key] < self.dv_neighbors[self.dv[key]]: 
    							self.dv[key] = n
    							send_update = True
    							#Update RU object here

    	elif change_type == "RU":
    		for key in self.dv_neighbors[src]: #add tie breaking by lower port number
    			if self.dv.has_key(key):
    				if self.dv_neighbors[src][key] < self.dv_neighbors[self.dv[key]]:
    					self.dv[key] = src
    					send_update = True
    					#Update RU object here
    			else:
    				self.dv[key] = src
    	else:
    		pass
    def send_RU(self, RU):
    	for n in self.neighbor_ports:
    		self.send(RU, n, self.neighbor_ports[0])
