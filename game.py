from threading import Timer
import time

from worker_thread import IOWorkerManager
from custom_message import *

# 인게임 슈퍼 클래스
class Game:
  def __init__(self, sessions, finish_callback):
    self.sessions = sessions;
    self.finish_callback = finish_callback;

  def send_to_all(self, message):
    for session_id in self.sessions:
      IOWorkerManager().push_io_message(session_id, message);

  def start_game(self):
    self.result_data = dict();

    # 테스트용 5초 후 게임이 종료된다고 가정
    self.finish_timer = Timer(5, self.finish_game);
    self.finish_timer.start();

    msg = make_message(MSG_GAME_STATUS);
    msg["game_status"] = "start";
    self.send_to_all(msg);

  def finish_game(self):
    msg = make_message(MSG_GAME_STATUS);
    msg["game_status"] = "end";
    self.send_to_all(msg);
    return self.finish_callback(self.result_data);
