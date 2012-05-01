from Queue import PriorityQueue


class MemoryQueue(PriorityQueue):
    def __init__(self, **kwargs):
        super(BaseDispatcher, self).__init__()
