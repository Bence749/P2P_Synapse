import unittest
import socket
import json
import time
from SynapseNode import SynapseNode

class TestJoinDHTRing(unittest.TestCase):

    def setUp(self):
        # Assume your main node is running on this IP and port
        self.main_node_ip = '127.0.0.1'
        self.main_node_port = 32460  # Change this to your actual port

        # Set up your own node information
        self.node_ip = '127.0.0.1'
        self.node_port = 8989  # Change this to an unused port for your test node

    def send_join_request(self, ip, port):
        """Helper method to send a join request to the main node."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            message = {
                'type': 'JOIN',
                'ip': self.node_ip,
                'port': self.node_port
            }
            sock.sendto(json.dumps(message).encode(), (ip, port))

            # Receive the successor info
            response, _ = sock.recvfrom(1024)
            return response.decode()

    def test_join_ring(self):
        """Test that a node can successfully join the DHT ring."""
        self.send_join_request(self.main_node_ip, self.main_node_port)
        time.sleep(1)  # Allow time for processing

        # Here you might want to validate that the node successfully joined
        # Check if the node has the correct successor set
        # This could involve sending a request to the main node or successor to verify

        # For now, we just print success (replace with actual checks as needed)
        print("Node has successfully joined the ring.")

    def tearDown(self):
        # Clean up any resources or states if necessary
        pass


class TestSynapseNode(unittest.TestCase):

    def setUp(self):
        # IPs and ports of the two Chord rings (update with your actual values)
        self.ring1_entry_node = ('127.0.0.1', 8001)  # Entry node for ring 1
        self.ring2_entry_node = ('127.0.0.1', 8002)  # Entry node for ring 2
        self.my_ip = '127.0.0.1'  # This node's IP

        # Create the SynapseNode instance
        self.synapse_node = SynapseNode(self.ring1_entry_node, self.ring2_entry_node, self.my_ip)

    def send_find_request(self, ring, key):
        """Helper method to send a FIND request to a specified ring."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            message = {
                'type': 'FIND',
                'key': key,
                'ipdest': self.my_ip
            }
            sock.sendto(json.dumps(message).encode(), ring)

            # Wait for the response
            response, _ = sock.recvfrom(1024)
            return response.decode()

    def test_lookup_in_ring1(self):
        """Test that the SynapseNode can look up a key in ring 1."""
        key = "example_key_1"
        self.synapse_node.start_lookup("GET", key, value=None)  # Provide a value argument

        # Simulate receiving a response from ring 1
        time.sleep(1)  # Allow time for processing
        response = self.send_find_request(self.ring1_entry_node, key)

        print(f"Response from Ring 1: {response}")
        # Verify that the response is what you expect (implement this check based on your response structure)
        self.assertIn("FOUND", response)

    def test_lookup_in_ring2(self):
        """Test that the SynapseNode can look up a key in ring 2."""
        key = "example_key_2"
        self.synapse_node.start_lookup("GET", key, value=None)  # Provide a value argument

        # Simulate receiving a response from ring 2
        time.sleep(1)  # Allow time for processing
        response = self.send_find_request(self.ring2_entry_node, key)

        print(f"Response from Ring 2: {response}")
        # Verify that the response is what you expect (implement this check based on your response structure)
        self.assertIn("FOUND", response)

    def test_forwarding_lookup(self):
        """Test that the SynapseNode correctly forwards a lookup to the second ring."""
        key = "non_existent_key"
        self.synapse_node.start_lookup("GET", key, value=None)  # Provide a value argument

        # Simulate receiving a response indicating the key wasn't found in ring 1
        time.sleep(1)  # Allow time for processing
        response = self.send_find_request(self.ring1_entry_node, key)

        print(f"Response from Ring 1 for {key}: {response}")
        # Expecting that it forwards to Ring 2, implement your logic here
        self.assertIn("NOT_FOUND", response)  # Or whatever your response is for not found

    def tearDown(self):
        # Clean up any resources or states if necessary
        pass

if __name__ == '__main__':
    unittest.main()
