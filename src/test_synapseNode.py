import unittest
from unittest.mock import patch, MagicMock
from SynapseNode import SynapseNode

class TestSynapseNode(unittest.TestCase):
    def setUp(self):
        # Mocking ring nodes and SynapseNode setup
        self.ring1_entry_node = ('127.0.0.1', 5001)
        self.ring2_entry_node = ('127.0.0.1', 5002)
        self.node_ip = '127.0.0.1'
        self.node_port = 5000

        # Initializing SynapseNode with mock IP and ports
        self.synapse_node = SynapseNode(
            ring1_entry_node=self.ring1_entry_node,
            ring2_entry_node=self.ring2_entry_node,
            my_ip=self.node_ip,
            my_port=self.node_port
        )

    @patch('socket.socket.sendto')
    def test_join_ring(self, mock_sendto):
        # Test if joining ring sends a JOIN message to the entry nodes
        self.synapse_node.join_ring(self.ring1_entry_node)
        self.synapse_node.join_ring(self.ring2_entry_node)
        
        # Check if the JOIN messages were sent correctly
        self.assertEqual(mock_sendto.call_count, 2)
        print("Test for joining rings passed.")

    @patch('socket.socket.sendto')
    def test_start_lookup(self, mock_sendto):
        # Testing lookup initiation
        test_key = "test_key"
        test_code = "GET"
        
        self.synapse_node.start_lookup(test_code, test_key)
        
        # Verify that FIND messages were sent to both rings
        self.assertEqual(mock_sendto.call_count, 2)
        print("Test for starting lookup passed.")

    @patch('socket.socket.recvfrom')
    def test_handle_incoming_find(self, mock_recvfrom):
        # Testing handling of an incoming FIND message
        find_message = {
            'type': 'FIND', 'code': 'GET', 'ttl': 5, 'mrr': 3, 'tag': 'tag1', 
            'key': 'test_key', 'value': None, 'ipdest': self.node_ip
        }
        mock_recvfrom.return_value = (json.dumps(find_message).encode(), self.ring1_entry_node)
        
        # Testing message handling
        with patch.object(self.synapse_node, 'on_receive_find') as mock_on_receive_find:
            self.synapse_node.listen_for_responses()
            mock_on_receive_find.assert_called_with(
                find_message['code'], find_message['ttl'], find_message['mrr'],
                find_message['tag'], find_message['key'], find_message['value'], find_message['ipdest']
            )
        print("Test for handling incoming FIND message passed.")

    @patch('socket.socket.sendto')
    def test_send_find(self, mock_sendto):
        # Test the send_find method for correct message structure and dispatch
        test_code = "GET"
        test_ttl = 5
        test_mrr = 3
        test_tag = "tag1234"
        test_key = "example_key"
        test_value = "example_value"
        ipdest = self.ring1_entry_node

        self.synapse_node.send_find(test_code, test_ttl, test_mrr, test_tag, test_key, test_value, ipdest)
        
        # Assert that sendto was called correctly
        self.assertTrue(mock_sendto.called)
        print("Test for sending FIND message passed.")

    def tearDown(self):
        self.synapse_node.stop()

if __name__ == "__main__":
    unittest.main()
