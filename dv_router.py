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
        if isinstance(packet, DiscoveryPacket):
            # print "dp: ----------------------"
            # print packet.src
            # print packet.latency
            # print "dp end: --------------------"
            self.handle_dp(packet, port)
        elif isinstance(packet, RoutingUpdate):
            # print "---------------------"
            # print packet.src
            # print packet.paths
            # print "---------------------"
        	#self.handle_ru(packet) 
            self.create_routing_update(packet)
        else: #Data packet, foward approroately
        	#Look up best path in DV, send to appropriate neighbor
            if (self.dv.has_key(packet.dst) and self.dv[packet.dst][1] != float("inf")):
                self.handle_data(packet)

    def handle_data(self, packet):
        print "dv"
        print self.dv
        next_hop = self.dv[packet.dst][0]
        port_num = self.neighbor_ports[next_hop]
        print next_hop
        self.send(packet, port_num)

    def handle_dp(self, packet, port): #takes in a discovery packet
        #print "hello DP"
        update_to_send = RoutingUpdate()
        self.neighbor_ports[packet.src] = port

        if (packet.is_link_up):
            if (isinstance(packet.src, BasicHost)):

                self.dv[packet.src] = [packet.src, packet.latency]
                self.my_hosts[packet.src] = packet.latency
                self.neighbor_latency[packet.src] = packet.latency
                update_to_send.add_destination(packet.src, packet.latency)
                self.simple_send_RU(update_to_send)
 
            elif(isinstance(packet.src, Entity)):
                self.neighbor_latency[packet.src] = packet.latency
                #self.neighbor_ports[packet.src] = port
                update_to_send.paths = self.my_hosts
                self.simple_send_RU(update_to_send)
            # self.dv[packet.dst] = [packet.src, packet.latency]
            # self.neighbor_latency[packet.src] = packet.latency

        elif (packet.is_link_up == False): #how to handle ports going down??
            if (isinstance(packet.src, BasicHost)):
                self.dv[packet.src] = [self, float("inf")]
                self.neighbor_latency[packet.src] = float("inf")
                update_to_send.add_destination(packet.src, float("inf"))
                self.my_hosts[packet.src] = packet.latency
                self.send_RU(update_to_send)

            elif (isinstance(packet.src, Entity)):
                print "were up in here "
                self.neighbor_latency[packet.src] = float("inf")
                for key in self.dv:

                    if self.dv[key][0] == packet.src: #a path has the link that doesn't exist
                        print " is your girl on the pill ?"
                        print self.name
                        print self.neighbor_latency
                        if key in self.my_hosts:
                            self.dv[key] = [key, self.my_hosts[key]]
                        else:
                            self.dv[key] = [self, float("inf")]
                        update_to_send.add_destination(key, self.dv[key][1])
                #update_to_send.paths = self.neighbor_latency
                #self.update_dv(packet.src)
                self.send_RU(update_to_send)
    
    def update_dv_neighbors(self, packet, dest):
		if self.dv_neighbors.has_key(packet.src):
			self.dv_neighbors[packet.src][dest] = packet.get_distance(dest)
		else:
			self.dv_neighbors[packet.src] = {dest:packet.get_distance(dest)}

  #   def update_dv(self, neighbor):
		# latency = self.neighbor_latency[neighbor]
		# ru = RoutingUpdate()
		# for dest in self.dv:
		# 	if self.dv[dest][0] == neighbor:
		# 		new_next_hop = neighbor
		# 		new_cost = self.dv_neighbors[neighbor][dest] + latency
		# 		for n in self.dv_neighbors:
		# 			if self.dv_neighbors[n].has_key(dest):
		# 				if self.dv_neighbors[n][dest] + self.neighbor_latency[n] < new_cost:
		# 					new_next_hop = n
		# 					new_cost = self.dv_neighbors[n][dest] + self.neighbor_latency[n]
		# 					ru.add_destination(dest, self.dv_neighbors[n][dest] + self.neighbor_latency[n])
		# self.send_RU(ru)


    def send_RU(self, RU):
        dests = RU.all_dests()
        for key in self.neighbor_ports:
            if (not self.neighbor_latency[key] == float("inf")) and (not isinstance(key, BasicHost)):
                Custom_RU = RoutingUpdate()
                for dest in dests:
                    if self.dv.has_key(dest):
                        if self.dv[dest][0] == key:
                            print 'problems'
                            print self.dv[dest][0]
                            Custom_RU.add_destination(dest, float("inf"))
                        else:
                            Custom_RU.add_destination(dest, RU.get_distance(dest))
                    else:
                        Custom_RU.add_destination(dest, RU.get_distance(dest))
                self.send(Custom_RU, self.neighbor_ports[key])



    def simple_send_RU(self, RU):
        for neighbor in self.neighbor_latency:
            port_number = self.neighbor_ports[neighbor]
            self.send(RU, port_number)





    def create_routing_update(self, packet):
        #print self.dv
        update_to_send = RoutingUpdate()
        send_update = False
        packet_destinations = packet.all_dests()
        for host in packet_destinations:
            #self.update_dv_neighbors(packet, host)

            from_source_to_host = packet.get_distance(host)
            
            if(not self.dv.has_key(host)):
                #print" why we not in here doe? "
                #print('not in dv')
                total_cost = from_source_to_host + self.neighbor_latency[packet.src]
                # print "total cost is: "
                # print total_cost
                self.dv[host] = [packet.src, total_cost] #what if inf
                print(self.dv)
                update_to_send.add_destination(host, total_cost)
                send_update = True
            else: #i have this host in my dv
                # current_cost_to_host = self.dv[host][1]
                # new_cost_to_host = from_source_to_host + self.neighbor_latency[packet.src]
                # if (current_cost_to_host > new_cost_to_host and from_source_to_host is not float("inf")):

                #     self.dv[host] = [packet.src, new_cost_to_host]
                #     update_to_send.add_destination(host, new_cost_to_host)
                #     send_update = True
                # elif (from_source_to_host == float("inf")and self.dv[host][0] == packet.src):
                #     print "this is why "
                #     if (self.my_hosts.has_key(host)):
                #         self.dv[host] = [host, self.my_hosts[host]]
                #         update_to_send.add_destination(host, self.my_hosts[host])

                #     else:
                #         self.dv[host] = [self, float("inf")]
                #         update_to_send.add_destination(host, float("inf"))
                #     send_update = True
                # #elif (current_cost_to_host == new_cost_to_host) need to add case if their equal set to lowest port#
                if(from_source_to_host == float("inf") and self.dv[host][0] != packet.src and self.dv[host][1] != float("inf")):
                    update_to_send.add_destination(host, self.dv[host][1])
                    print " in this case "
                    send_update = True;
                if(from_source_to_host == float("inf") and self.dv[host][0] == packet.src and self.dv[host][1] != float("inf")):
                    print "in this bitch rightche"
                    if(host in self.my_hosts): # i have a direct link to host
                        self.dv[host] = [host, self.my_hosts[host]]
                        update_to_send.add_destination(host, self.my_hosts[host])
                    else: #no direct link to host
                        self.dv[host] = [None, float("inf")]
                        update_to_send.add_destination(host, float("inf"))
                    send_update = True;

                elif (self.dv[host][1] == float("inf") and from_source_to_host != float("inf")):
                    self.dv[host] = [packet.src, from_source_to_host + self.neighbor_latency[packet.src]]
                    update_to_send.add_destination(host, from_source_to_host + self.neighbor_latency[packet.src])
                    send_update = True;

                elif ((self.dv[host][0] == packet.src) and (from_source_to_host != float("inf"))):

                    total = from_source_to_host + self.neighbor_latency[packet.src]
                    if (self.dv[host][1] != (total)):
                        if (self.dv[host][1] > total):
                            self.dv[host] = [self.dv[host][0], total]
                        elif (host in self.my_hosts):
                            if (self.my_hosts[host] < total):
                                self.dv[host] = [host, self.my_hosts[host]] 
                            else:
                                self.dv[host] = [self.dv[host][0], total]
                        else:
                            self.dv[host] = [self.dv[host][0], total]
                        self.update_to_send.add_destination(self.dv[host], self.dv[host][1])
                        send_update = True;

            if send_update:
                #self.simple_send_RU(update_to_send)
                self.send_RU(update_to_send)


