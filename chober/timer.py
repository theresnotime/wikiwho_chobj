from time import process_time


class Timer():

    """Context manager that measures the time of a process, usage:

    with Timer():
        # the code that you want to meassure
        # and it will output the processing time
    
    Attributes:
        t1 (flost): initial time
    """
    ctr = 0

    def __init__(self, name=None, silent=True):
        self.silent=silent
        if name:
            self.name = name
        else:
            self.name = Timer.ctr
            Timer.ctr += 1

    
    def __enter__(self):
        self.t1 = process_time()
        return self

    def __exit__(self, *a):
        self.diff = process_time() - self.t1
        if not self.silent:
            print(str(self.name) + ': ' + str(self.diff))