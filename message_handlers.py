import threading, json, time

from queue import Queue

from session_manager import *
from custom_message import *

q = Queue();
worker_threads = [];

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
    #q.task_done();

def initWorkers(count=2):
  print("init workers", count);
  for i in range(count):
    t = threading.Thread(target=doWork, args=(i, q));
    t.setDaemon(True);
    worker_threads.append(t);
    t.start();


def handleLogin(message):
  print("handleLogin");
  if message["message_id"] != MSG_LOGIN:
    return;

  session_id = message["session_id"];
  res = makeMessage(MSG_LOGIN_RES);
  res["result"] = "ok";

  sendMessage(session_id, res);

messageHandlers = dict();
messageHandlers[MSG_LOGIN] = handleLogin;


def handleMessage(message):
  print("handleMessage");
  req = json.loads(message);
  if "message_id" not in req:
    print("wrong message", req);
    return;

  messageHandlers[req["message_id"]](req);

def pushMessage(message):
  print("pushMessage");
  q.put(message);
