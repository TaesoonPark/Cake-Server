from threading import Timer
import time
import datetime

from worker_thread import IOWorkerManager
from custom_message import *

# 인게임 슈퍼 클래스
class Game:
  def __init__(cls, sessions, finish_callback):
    cls.sessions = sessions;
    cls.finish_callback = finish_callback;
    cls.index = 0;

  def send_to_all(cls, message):
    for session_id in cls.sessions:
      IOWorkerManager().push_io_message(session_id, message);

  def start_game(cls):
    cls.result_data = dict();

    # 테스트용 5초 후 게임이 종료된다고 가정
    cls.finish_timer = Timer(5, cls.finish_game);
    cls.finish_timer.start();

    msg = make_message(MSG_GAME_STATUS);
    msg["game_status"] = "start";
    cls.send_to_all(msg);

  def finish_game(cls):
    msg = make_message(MSG_GAME_STATUS);
    msg["game_status"] = "end";
    cls.send_to_all(msg);
    return cls.finish_callback(cls.result_data);

  def process_update(cls):
    print("index=" , cls.index);
    cls.index += 1;
