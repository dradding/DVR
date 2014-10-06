def handle_dp(self, packet, port): #takes in a discovery packet
        #print "hello DP"
        update_to_send = RoutingUpdate()
        update_to_path = RoutingUpdate()
        self.neighbor_ports[packet.src] = port

        if (packet.is_link_up):
            print self.name
            print self.dv
            self.dv[packet.src] = [packet.src, packet.latency]
            #self.my_hosts[packet.src] = packet.latency
            update_to_path.paths = self.neighbor_latency
            self.send(update_to_path, port)
            #update_to_send.paths = self.neighbor_latency
            self.neighbor_latency[packet.src] = packet.latency
            update_to_send.add_destination(packet.src, packet.latency)
            self.simple_send_RU(update_to_send)
            #self.neighbor_latency[packet.src] = packet.latency
            self.neighbor_ports[packet.src] = port
            #self.neighbor_ports[packet.src] = port

            #self.simple_send_RU(update_to_send)
            #self.update_dv(packet.src)
            # self.dv[packet.dst] = [packet.src, packet.latency]
            # self.neighbor_latency[packet.src] = packet.latency

        elif (packet.is_link_up == False): #how to handle ports going down??
            self.dv[packet.src] = [self, float("inf")]
            self.neighbor_latency[packet.src] = float("inf")
            update_to_path.add_destination(packet.src, float("inf"))
            #self.my_hosts[packet.src] = packet.latency
            #self.send_RU(update_to_send)


            #self.neighbor_latency[packet.src] = float("inf")
            # for key in self.dv:

            #     if self.dv[key][0] == packet.src: #a path has the link that doesn't exist
            #             self.dv[key] = [key, self.neighbor_latency[key]]
            #     else:
            #         self.dv[key] = [self, float("inf")]
            #         update_to_path.add_destination(key, self.dv[key][1])
            #update_to_send.paths = self.neighbor_latency
            #self.update_dv(packet.src)
            self.send_RU(update_to_path)
