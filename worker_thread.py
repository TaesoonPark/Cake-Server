import threading, json, time

from queue import Queue

from custom_message import *

q = Queue();
worker_threads = [];

message_handlers = dict();

def doWork(index, q):
  print("doWork", index);
  while True:
    if q.empty():
      time.sleep(0.1);
      continue;

    message = q.get();
    if message is None:
      time.sleep(0.1);
      print("wrong process", index);
      continue;

    print("Thread handleMessage", index);
    handleMessage(message);


def initWorkers(count=2):
  global q;
  global worker_threads;
  print("init workers", count);
  for i in range(count):
    t = threading.Thread(target=doWork, args=(i, q));
    t.setDaemon(True);
    worker_threads.append(t);
    t.start();


def handleMessage(message):
  print("handleMessage");
  req = json.loads(message);
  if "message_id" not in req:
    print("wrong message", req);
    return;

  message_handlers[req["message_id"]](req);


def pushMessage(message):
  print("pushMessage");
  q.put(message);

def addMessageHandler(message_id, handler):
  global message_handlers;
  if message_id in message_handlers:
    print("duplicate message handler id=", message_id);
    return;

  message_handlers[message_id] = handler;
