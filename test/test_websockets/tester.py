#! /usr/bin/python
import thread
import time
import datetime
import logging
import json
import sys
import uuid
import websocket
from multiprocessing import Pool


echo_server_loc = "ws://echo.websocket.org/"
whatsup_server_loc = "ws://192.168.0.19:9000/ws"

extremis_id = str(uuid.UUID('9174e63367b64387bb3f2b903e8214c6'))

def on_message(ws, message):
  logging.info("%s received %s" % (ws, message))
  ws.close()

def on_open(ws):
  message = json.dumps({'type': 'init', 'msg' : extremis_id})
  ws.send(message)
  #time.sleep(3)
  #message = json.dumps({'type': 'msg', 'src' : extremis_id, 'user': 'Tester', 'msg': 'TestComment'})
  #ws.send(message)

def task(log_num):
  websocket.enableTrace(False)
  
  logfile = "wstest.log."+str(log_num)

  logging.basicConfig(filename=logfile, format='%(asctime)s:%(message)s', level=logging.DEBUG)

  ws = (websocket.WebSocketApp(whatsup_server_loc,
                              on_message = on_message))

  ws.on_open = on_open
  ws.run_forever()

if __name__ == '__main__':
  num_ps = int(sys.argv[1])
  p = Pool(num_ps)

  p.map(task, range(num_ps))

