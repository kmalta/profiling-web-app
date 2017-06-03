from threading import Thread,Semaphore
from time import sleep, time
import sys, os
from cStringIO import StringIO
from multiprocessing import Process, Queue

class Barrier:
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Semaphore(1)
        self.barrier = Semaphore(0)

    def wait(self):
        self.mutex.acquire()
        self.count = self.count + 1
        self.mutex.release()
        if self.count == self.n: self.barrier.release()
        self.barrier.acquire()
        self.barrier.release()


def mp():
    queue = Queue()
    p = Process(target=loop,args=('output_1','hello'))
    q = Process(target=loop,args=('output_2','there'))
    p.start()
    q.start()
    # p.join()
    # q.join()

def loop(p,x):
    old_stdout = sys.stdout  # Redirection of the printing output to a StringIO
    sys.stdout = mystdout = open(p, 'w', buffering=0)
    for i in xrange(100):
        print x, repr(time())
        sleep(3)
    ### Write the code\functions necessary in here. ###
    sys.stdout = old_stdout
    # dataStats_1 = mystdout.getvalue()    # Put all the redirected output into a string.
    # f = open(p, 'w')
    # f.write(dataStats_1)
    # f.close()



def main():
    mp()


if __name__ == "__main__":
    main()
