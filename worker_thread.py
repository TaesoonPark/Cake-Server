import threading
import json
import time

from queue import Queue

from custom_message import *
from session_manager import SessionManager


class WorkerManager():
  # 싱글톤 구현을 위한 오버라이딩
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(WorkerManager, cls).__new__(cls);
      cls.q = Queue();
      cls.worker_threads = [];
      cls.message_handlers = dict();
      for i in range(2):
        t = threading.Thread(target=cls.do_work, args=(cls, i, cls.q));
        t.setDaemon(True);
        cls.worker_threads.append(t);
        t.start();
    return cls.instance;

  # 워커쓰레드의 루프. 대기하다가 처리가 필요한 메시지가 생기면 진행
  def do_work(cls, index, q):
    print("Worker start", index);
    while True:
      if cls.q.empty():
        time.sleep(0.1);
        continue;

      message = cls.q.get();
      if message is None:
        time.sleep(0.1);
        print("wrong process", index);
        continue;

      print("Thread handleMessage", index);
      cls.handle_message(cls, message);

  # 소켓에서 받은 메시지를 워커에 맞게 수정 후 push
  def push_message(cls, message):
    cls.q.put(message);

  # 입력받은 메시지에 맞는 핸들러 호출
  def handle_message(cls, message):
    req = json.loads(message);
    if "message_id" not in req:
      print("wrong message", req);
      return;
    
    if req["message_id"] not in cls.message_handlers:
      print("cannot find handler", req["message_id"]);
      return;

    cls.message_handlers[req["message_id"]](req);

  # message_handlers에 등록한 함수들을 등록
  def add_message_handler(cls, message_id, handler):
    if message_id in cls.message_handlers:
      print("duplicate message handler id=", message_id);
      return;

    cls.message_handlers[message_id] = handler;


class IOWorkerManager():
  # 싱글톤 구현을 위한 오버라이딩
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(IOWorkerManager, cls).__new__(cls);
      cls.q = Queue();
      cls.worker_threads = [];
      for i in range(2):
        t = threading.Thread(target=cls.do_io, args=(cls, i, cls.q));
        t.setDaemon(True);
        cls.worker_threads.append(t);
        t.start();
    return cls.instance;

  # 워커쓰레드의 루프. 보낼 메시지가 들어오면 SessionManager로 접근
  def do_io(cls, index, q):
    print("IO Worker start", index);
    while True:
      if cls.q.empty():
        time.sleep(0.1);
        continue;

      job = cls.q.get();
      if job is None:
        time.sleep(0.1);
        print("wrong process", index);
        continue;

      SessionManager().send_message(job[0], job[1]);

  # io큐에 할일 저장
  def push_io_message(cls, session_id, message):
    cls.q.put((session_id, message));
