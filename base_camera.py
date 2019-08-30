import time
import threading
import cv2
import numpy as np
import socket

host = '0.0.0.0'
size = 245760


try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}
        print("Camera Event Created")



    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):


    def __init__(self,port):
        """Start the background camera thread if it isn't running yet."""
        

        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.event = CameraEvent()
        self.frames_iterator=None
        self.port=port

        self.setup()        
        
        if self.thread is None:
            self.last_access = time.time()

            # start background frame thread
            self.thread = threading.Thread(target=self._thread)
            self.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""

        self.last_access = time.time()

        # wait for a signal from the camera thread
        
        self.event.wait()
        self.event.clear()

        return self.frame

    def setup(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host,self.port))
        self.s.listen(1)         
        

        try:
            self.client, self.address = self.s.accept()     
            print(str(self.client)+" connected")

        except Exception as e:
            print("Fucked")  
       

    # @staticmethod
    def frames(self):

        try:
            print("camera1 sending")

            yArr = []
            while True:
                while len(yArr)<245760:
                    yArr+=self.client.recv(245760)      

                data = self.client.recv(245760)
                if not data: self.client.close()     
                
                image = np.array(yArr[:size], np.uint8).reshape( 256, 320, 3 )
                yArr = yArr[size:]     

                yield cv2.imencode('.jpg', image)[1].tobytes()
            self.client.close()
        except Exception as e:
            print("FUCKED")


    def _thread(cls):
      
        print('Starting camera thread.')          
        
        cls.frames_iterator = cls.frames()

        for frame in cls.frames_iterator:
            cls.frame = frame
            cls.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - cls.last_access > 1000:
                cls.frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        cls.thread = None
