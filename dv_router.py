from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.dv = {} # destination: [next_hop, cost to dest]
        self.dv_neighbors = {} # neighbor: neighbor DV
        self.neighbor_ports = {} #Key is neighbor, value is ports
        self.neighbor_latency = {} #neighbor: link-latency
        self.my_hosts = {} #host: link-latency


    def handle_rx (self, packet, port):
        # Add your code here!
        print self.neighbor_ports
        if isinstance(packet, DiscoveryPacket):
            self.handle_dp(packet, port)
        elif isinstance(packet, RoutingUpdate):
        	self.handle_ru(packet)
        else: #Data packet, foward approroately
        	#Look up best path in DV, send to appropriate neighbor
			self.handle_data(packet)

    def handle_data(self, packet):
        next_hop = self.dv[packet.dst][0]
        port_num = self.neighbor_ports[next_hop]

        self.send(packet, port_num)

    def handle_dp(self, packet, port): #takes in a discovery packet
        print "hello DP"
        update_to_send = RoutingUpdate()
        if (packet.is_link_up):
            if (isinstance(packet.src, BasicHost)):
                self.dv[packet.src] = [packet.src, packet.latency]
                self.my_hosts[packet.src] = packet.latency
            elif(isinstance(packet.src, Entity)):
                self.neighbor_latency[packet.src] = packet.latency
                #self.neighbor_ports[packet.src] = port
                update_to_send.paths = self.my_hosts
                self.send_RU(update_to_send)
            # self.dv[packet.dst] = [packet.src, packet.latency]
            self.neighbor_ports[packet.src] = port
            # self.neighbor_latency[packet.src] = packet.latency

        elif (packet.is_link_up == False): #how to handle ports going down??
            if (isinstance(packet.src, BasicHost)):
                self.dv[packet.src] = (self, float("inf"))
                update_to_send.add_destination(packet.src, packet.latency)
                self.my_hosts[packet.src] = packet.latency
                self.send_RU(update_to_send)

            elif (isinstance(packet.src, Entity)):
                self.neighbor_latency[packet.src] = float("inf")


    def update_dv_neighbors(self, packet, dest):
		if self.dv_neighbors.has_key(packet.src):
			self.dv_neighbors[packet.src][dest] = packet.get_distance(dest)
		else:
			self.dv_neighbors[packet.src] = {dest:packet.get_distance(dest)}

    def handle_ru(self, packet):
        print "hello RU"

    	ru = RoutingUpdate()
    	if self.neighbor_latency.has_key(packet.src):
    		latency = self.neighbor_latency[packet.src]
    	else:
    		latency = float("inf")
    	send_update = False
    	destinations = packet.all_dests()
    	for dest in destinations: #add tie breaking via lower port number
			self.update_dv_neighbors(packet, dest)
			if self.dv.has_key(dest):
				if self.dv[dest][0] == packet.src and packet.get_distance(dest) + latency > self.dv[dest][1]:
					new_next_hop = packet.src
					new_cost = packet.get_distance(dest) + latency
					for n in self.dv_neighbors:
						if self.dv_neighbors[n].has_key(dest):
							if self.dv_neighbors[n][dest] + self.neighbor_latency[n] < new_cost:
								new_next_hop = n
								new_cost = self.dv_neighbors[n][dest] + self.neighbor_latency[n]
								send_update = True
								ru.add_destination(dest, self.dv_neighbors[n][dest] + self.neighbor_latency[n])

				if packet.get_distance(dest) + latency < self.dv[dest][1]:
					self.dv[dest] = [packet.src, packet.get_distance(dest) + latency]
					send_update = True
					ru.add_destination(dest, self.dv[dest][1])
					#Update RU object here
			else:
				send_update = True
				self.dv[dest] = [packet.src, packet.get_distance(dest) + latency]
				ru.add_destination(dest, self.dv[dest][1])
		
			if send_update:
				self.send_RU(ru)

    def send_RU(self, RU):
    	for port_number in self.neighbor_ports:
    		self.send(RU, self.neighbor_ports[port_number])
