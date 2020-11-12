import threading
import json
import time

from queue import Queue

from custom_message import *
from session_manager import SessionManager

q = Queue();
worker_threads = [];
message_handlers = dict();

io_q = Queue();
io_threads = [];

# 워커쓰레드의 루프. 대기하다가 처리가 필요한 메시지가 생기면 진행
def doWork(index, q):
  print("Worker start", index);
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


# 입력받은 메시지에 맞는 핸들러 호출
def handleMessage(message):
  req = json.loads(message);
  if "message_id" not in req:
    print("wrong message", req);
    return;
  
  if req["message_id"] not in message_handlers:
    print("cannot find handler", req["message_id"]);
    return;

  message_handlers[req["message_id"]](req);


# 소켓에서 받은 메시지를 워커에 맞게 수정 후 push
def pushMessage(message):
  q.put(message);


# message_handlers에 등록한 함수들을 등록
def addMessageHandler(message_id, handler):
  global message_handlers;
  if message_id in message_handlers:
    print("duplicate message handler id=", message_id);
    return;

  message_handlers[message_id] = handler;


# 워커쓰레드의 루프. 대기하다가 처리가 필요한 메시지가 생기면 진행
def doIO(index, q):
  print("IO Worker start", index);
  while True:
    if q.empty():
      time.sleep(0.1);
      continue;

    job = q.get();
    if job is None:
      time.sleep(0.1);
      print("wrong process", index);
      continue;

    SessionManager().send_message(job[0], job[1]);


# io큐에 할일 저장
def pushIOMessage(session_id, message):
  io_q.put((session_id, message));


# 워커 쓰레드 초기화
def initWorkers(worker_count=2, io_count=2):
  global worker_threads;
  print("init workers", worker_count);
  for i in range(worker_count):
    t = threading.Thread(target=doWork, args=(i, q));
    t.setDaemon(True);
    worker_threads.append(t);
    t.start();

  global io_threads;
  print("init IO workers", io_count);
  for i in range(io_count):
    t = threading.Thread(target=doIO, args=(i, io_q));
    t.setDaemon(True);
    io_threads.append(t);
    t.start();
