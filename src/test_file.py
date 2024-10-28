import unittest
import time
from threading import Event
from SynapseNode import SynapseNode  # Adjust this import based on your file structure

class TestSynapseNode(unittest.TestCase):
    def setUp(self):
        self.ring1_entry_node = ('127.0.0.1', 7621)
        self.ring2_entry_node = ('127.0.0.1', 53635)
        self.my_ip = '127.0.0.1'
        self.my_port = 0

        # Initialize SynapseNode
        self.node = SynapseNode(self.ring1_entry_node, self.ring2_entry_node, self.my_ip, self.my_port)

        # Allow some time for the node to join the rings
        time.sleep(2)

        # Create an event to wait for FOUND or NOT_FOUND messages
        self.response_event = Event()

        # Override the handle_incoming_message method to set the event
        self.original_handle_incoming_message = self.node.handle_incoming_message
        self.node.handle_incoming_message = self.create_handle_incoming_message()

    def create_handle_incoming_message(self):
        def handle_incoming_message(message):
            self.original_handle_incoming_message(message)  # Call the original method
            msg_type = message.get('type')
            if msg_type in ['FOUND', 'NOT_FOUND']:
                self.response_event.set()  # Signal that we received a response

        return handle_incoming_message

    def test_start_lookup(self):
        key = 'alma'
        code = 'FIND'

        # Start a lookup for the key
        self.node.start_lookup(code, key)

        # Wait for a FOUND or NOT_FOUND message, with a timeout of 5 seconds
        found_or_not_found = self.response_event.wait(timeout=30)

        # Assert that we received a response
        self.assertTrue(found_or_not_found, "Did not receive FOUND or NOT_FOUND message in time.")
        print(f"Received a FOUND or NOT_FOUND message for key '{key}' with code '{code}'")

    if __name__ == '__main__':
        unittest.main()