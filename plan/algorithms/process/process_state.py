from enum import Enum

class processState(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    FINISHED = 3
    WAITING = 4

