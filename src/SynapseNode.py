from WhiteBoxProtocol import WhiteBoxProtocol

class SynapseNode(WhiteBoxProtocol):
    def __init__(self, ring1_entry_node, ring2_entry_node, my_ip):
        super().__init__(my_ip)
        self.ring1_entry_node = ring1_entry_node  # Entry point to the first Chord ring
        self.ring2_entry_node = ring2_entry_node  # Entry point to the second Chord ring
        self.my_ip = my_ip

    def start_lookup(self, code, key, value):
        """
        Start a lookup process by sending an initial FIND message to both rings.

        :param code: Operation code (e.g., GET, PUT)
        :param key: The key to look up
        :param value: The value to store or retrieve (optional)
        """
        tag = self.new_tag(self.my_ip)
        self.send_find(code, ttl=5, mrr=3, tag=tag, key=key, value=value, ipdest=self.my_ip)
        print(f"Initiated lookup for key {key} with tag {tag}")

    def find_successor(self, key, ring):
        """
        Custom method to find the successor of a key within a specific ring.

        :param key: The key for which to find the successor.
        :param ring: The target ring (either 'ring1' or 'ring2').
        """
        entry_node = self.ring1_entry_node if ring == 'ring1' else self.ring2_entry_node
        successor = entry_node.find_successor(key)
        return successor

    def on_receive_find(self, code, ttl, mrr, tag, key, value, ipdest):
        """
        Overrides the FIND handling method to include specific logic for inter-ring communication.
        """
        super().on_receive_find(code, ttl, mrr, tag, key, value, ipdest)

        # Determine if further lookup in the alternate ring is needed
        if not self.is_responsible(self.ring1_entry_node, key):
            print("Key not found in Ring 1, forwarding lookup to Ring 2.")
            next_hop = self.next_hop(self.ring2_entry_node, key)
            self.send_find(code, ttl - 1, mrr, tag, key, value, next_hop)

    def handle_incoming_message(self, message):
        """
        Main handler to process incoming messages based on their type.

        :param message: The message object (e.g., dict with 'type', 'code', 'key', etc.)
        """
        msg_type = message.get('type')
        if msg_type == 'FIND':
            self.on_receive_find(
                message['code'], message['ttl'], message['mrr'], message['tag'],
                message['key'], message['value'], message['ipdest']
            )
        elif msg_type == 'FOUND':
            self.on_receive_found(
                message['code'], message['net'], message['mrr'], message['key'],
                message['value'], message['ipsend']
            )
        elif msg_type == 'INVITE':
            self.on_receive_invite(message['net'], message['ipsend'])
        elif msg_type == 'JOIN':
            self.on_receive_join(message['net'], message['ipsend'])
        else:
            print(f"Unknown message type: {msg_type}")

    # Example method to simulate receiving a FIND message from an external node
    def receive_find_request(self, code, key, value, ttl=5):
        """
        Simulates receiving a FIND request and handling it.

        :param code: Operation code (e.g., GET, PUT)
        :param key: The key to look up
        :param value: Value associated with the key (if applicable)
        :param ttl: Time-to-live for the request
        """
        print(f"Received FIND request for key {key} with TTL {ttl}")
        self.start_lookup(code, key, value)

    def add_network(self, net, ring='ring1'):
        """
        Adds a new network (ring) to this synapse node's list of connected networks.

        :param net: Network to add.
        :param ring: Specifies which ring ('ring1' or 'ring2').
        """
        if ring == 'ring1':
            self.ring1_entry_node = net
        elif ring == 'ring2':
            self.ring2_entry_node = net
        else:
            print("Invalid ring specified")
        print(f"Network {net} added to {ring}")
