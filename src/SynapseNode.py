import threading
import socket
import json
from queue import Queue
from WhiteBoxProtocol import WhiteBoxProtocol


class SynapseNode(WhiteBoxProtocol):
    def __init__(self, ring1_entry_node, ring2_entry_node, my_ip, my_port):
        super().__init__(my_ip)
        self.ring1_entry_node = ring1_entry_node
        self.ring2_entry_node = ring2_entry_node
        self.my_ip = my_ip
        self.my_port = my_port
        self.message_queue = Queue()
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.my_ip, self.my_port))

        threading.Thread(target=self.listen_for_responses, daemon=True).start()

        self.join_ring(self.ring1_entry_node)
        self.join_ring(self.ring2_entry_node)

    def join_ring(self, entry_node):
        self.send_join(entry_node, (self.my_ip, self.my_port))
        print(f"Attempting to join ring at {entry_node}")

    def start_lookup(self, code, key, value=None):
        tag = self.new_tag(self.my_ip)
        self.send_find(code, ttl=5, mrr=3, tag=tag, key=key, value=value, ipdest=self.ring1_entry_node)
        self.send_find(code, ttl=5, mrr=3, tag=tag, key=key, value=value, ipdest=self.ring2_entry_node)
        print(f"Started lookup for key '{key}' with tag '{tag}'")

    def send_find(self, code, ttl, mrr, tag, key, value, ipdest):
        message = {
            'type': 'FIND',
            'code': code,
            'ttl': ttl,
            'mrr': mrr,
            'tag': tag,
            'key': key,
            'value': value
        }

        message_json = json.dumps(message).encode()

        self.sock.sendto(message_json, ipdest)

        print(f"Sending FIND message to {ipdest} with key '{key}' and TTL {ttl}")

    def listen_for_responses(self):
        while True:
            response, addr = self.sock.recvfrom(1024)
            message = json.loads(response.decode())
            self.handle_incoming_message(message)

    def handle_incoming_message(self, message):
        msg_type = message.get('type')
        if msg_type == 'FIND':
            self.on_receive_find(
                message['code'], message['ttl'], message['mrr'], message['tag'],
                message['key'], message['value'], message['ipdest']
            )
        elif msg_type == 'FOUND':
            self.process_response(message)
        elif msg_type == 'NOT_FOUND':
            self.process_response(message)
        elif msg_type == 'JOIN':
            self.on_receive_join(message['net'], message['ipsend'])
        elif msg_type == 'READ_TABLE':
            self.on_receive_read_table(message['net'], message['key'], message['ipsend'])
        elif msg_type == 'WRITE_TABLE':
            self.on_receive_write_table(message['net'], message['key'], message['value'], message['ipsend'])
        else:
            print(f"Unknown message type: {msg_type}")

    def on_receive_find(self, code, ttl, mrr, tag, key, value, ipdest):
        if ttl <= 0:
            print(f"TTL expired for lookup with tag {tag}")
            return

        print(f"Processing FIND request for key '{key}' with TTL {ttl}")
        if self.is_responsible(self.ring1_entry_node, key):
            print(f"Key '{key}' found in Ring 1.")
            self.send_found(code, self.ring1_entry_node, mrr, key, value, ipdest)
        else:
            print(f"Forwarding lookup for key '{key}' to Ring 2.")
            self.send_find(code, ttl - 1, mrr, tag, key, value, self.ring2_entry_node)

    def process_response(self, message):
        if message['type'] == 'FOUND':
            print(f"Key '{message['key']}' found with value '{message['value']}'")
        elif message['type'] == 'NOT_FOUND':
            print(f"Key '{message['key']}' not found in the current ring, checking next ring.")
            if message['ttl'] > 0:
                self.send_find(message['code'], message['ttl'] - 1, message['mrr'],
                               message['tag'], message['key'], message['value'], self.ring2_entry_node)

    def process_messages(self):
        while self.running:
            try:
                message, addr = self.sock.recvfrom(1024)
                message = json.loads(message.decode())
                self.message_queue.put(message)
                print(f"Received message: {message} from {addr}")
            except OSError as e:
                print(f"Error processing messages: {e}")

    def stop(self):
        self.running = False
        self.sock.close()

    def send_read_table(self, net, key, ipdest):
        message = json.dumps({'type': 'READ_TABLE', 'net': net, 'key': key, 'ipsend': ipdest})
        self.sock.sendto(message.encode(), ipdest)
        print(f"Sending READ_TABLE message for key {key} to {ipdest}")

    def send_write_table(self, net, key, value, ipdest):
        message = json.dumps({'type': 'WRITE_TABLE', 'net': net, 'key': key, 'value': value, 'ipsend': ipdest})
        self.sock.sendto(message.encode(), ipdest)
        print(f"Sending WRITE_TABLE message for key {key} and value {value} to {ipdest}")

    def send_join(self, net, ipdest):
        message = json.dumps({'type': 'JOIN', 'net': net, 'ipsend': ipdest})
        self.sock.sendto(message.encode(), ipdest)
        print(f"Sending JOIN message to {ipdest} for network {net}")

    def game_over(self, tag):
        return tag in self.processed_tags

    def distrib_mrr(self, mrr, net_list):
        return {net: mrr // len(net_list) for net in net_list}

    def is_responsible(self, net, key):
        return True

    def good_deal(self, net, ip):
        return True

    def next_hop(self, net, key):
        return net

    def good_deal_update(self, net, source_ip):
        print(f"Updating good deal state for net {net} from source {source_ip}")

    def insert_net(self, net, source_ip):
        self.net_list.append(net)
        print(f"Inserted network {net} from source {source_ip}")
