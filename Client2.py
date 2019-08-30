import sys
import socket
import numpy as np
import cv2

img = cv2.imread("cat.jpg")
img=cv2.resize(img,(320,256))

print("client 2, trying connecting")
SERVER = "192.168.50.181"
PORT = 5002
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  client.connect((SERVER, PORT))
except Exception as e:
  print("Caught exception socket.error :"+str(e))
  sys.exit(0)

print("client connected")

try:
  while True:
 
      
    image = np.array(img, np.uint8).reshape( 256*320*3, 1 )
    print(len(image))
    client.sendall(bytes(image))
except KeyboardInterrupt:
  # client.close()

  print('Key pressed and interrupted!')
except Exception as e:
  print("Exception: "+str(e))

finally:
  
  # close the client by the end of the demo
  # client.close()
  print("client 2 closed")



