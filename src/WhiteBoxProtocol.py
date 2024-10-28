import time

class WhiteBoxProtocol:
    def __init__(self, my_ip):
        self.my_ip = my_ip
        self.net_list = []
        self.processed_tags = set()

    def new_tag(self, source_ip):
        return f"{source_ip}-{int(time.time() * 1000)}"

    def on_receive_ope(self, code, key, value, source_ip):
        tag = self.new_tag(source_ip)
        self.send_find(code, ttl=5, mrr=3, tag=tag, key=key, value=value, ipdest=self.my_ip)

    def on_receive_find(self, code, ttl, mrr, tag, key, value, ipdest):
        if ttl == 0 or self.game_over(tag):
            print("Lookup aborted due to TTL expiry or game over.")
        else:
            self.processed_tags.add(tag)
            next_mrr = self.distrib_mrr(mrr, self.net_list)
            for net in self.net_list:
                if self.is_responsible(net, key):
                    self.send_found(code, net, mrr, key, value, ipdest)
                elif self.good_deal(net, ipdest):
                    self.send_find(code, ttl - 1, next_mrr.get(net), tag, key, value, self.next_hop(net, key))

    def on_receive_found(self, code, net, mrr, key, value, source_ip):
        self.good_deal_update(net, source_ip)
        if code == "GET":
            self.send_read_table(net, key, source_ip)
        elif code == "PUT":
            if mrr < 0:
                print("Stopping replication as mrr is negative.")
            else:
                self.send_write_table(net, key, value, source_ip)

    def on_receive_invite(self, net, source_ip):
        if self.good_deal(net, source_ip):
            self.send_join(net, source_ip)

    def on_receive_join(self, net, source_ip):
        if self.good_deal(net, source_ip):
            self.insert_net(net, source_ip)

    def send_find(self, code, ttl, mrr, tag, key, value, ipdest):
        print(f"Sending FIND message to {ipdest} with key {key} and ttl {ttl}")

    def send_found(self, code, net, mrr, key, value, ipdest):
        print(f"Sending FOUND message to {ipdest} for key {key}")

    def send_read_table(self, net, key, ipdest):
        print(f"Sending READ_TABLE message for key {key} to {ipdest}")

    def send_write_table(self, net, key, value, ipdest):
        print(f"Sending WRITE_TABLE message for key {key} and value {value} to {ipdest}")

    def send_join(self, net, ipdest):
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
