import threading

def _mThread(stop_e):
    while not stop_e.isSet():
      a=input()
      if a == 'q':
        stop_e.set()
      else:
        print('no stop')


class MyT(threading.Thread):
  def __init__(self):
    self.__stop_thread_event = threading.Event()
    threading.Thread.__init__(self)
  
  def run(self):
    while not self.__stop_thread_event.isSet():
      a=input()
      if a == 'q':
        self.stop()
      else:
        print('no stop')
  
  def stop(self):
    self.__stop_thread_event.set()


t = threading.Thread(target=_mThread, args=(threading.Event(),) )
t.start()
