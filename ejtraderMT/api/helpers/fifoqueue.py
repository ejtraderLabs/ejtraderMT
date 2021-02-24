class Node(object):
    def __init__(self, value):
        self.value = value
        self.next = None

    def __repr__(self):
        return 'Node %s' % self.value


class Queue(object):
    """A FIFO queue."""

    def __init__(self):
        self.length = 0
        self.head = None
        self.last = None

    def __repr__(self):
        result = ''
        node = self.head
        while node:
            result += ' %s' % node
            node = node.next
        return result

    def is_empty(self):
        return self.length == 0

    def add(self, value):
        new_node = Node(value)
        if self.length == 0:
            self.head = new_node
            self.last = new_node
        else:
            self.last.next = new_node
            self.last = new_node
        self.length += 1

    def remove(self):
        if not self.head:
            return
        value = self.head.value
        self.head = self.head.next
        self.length -= 1
        return value
