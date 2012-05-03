from Queue import PriorityQueue


class MemoryQueue(PriorityQueue):
    def __init__(self, **kwargs):
        PriorityQueue.__init__(self)
