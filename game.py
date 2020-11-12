from threading import Timer
import time

from worker_thread import pushIOMessage
from custom_message import *

# 인게임 슈퍼 클래스
class Game:
  def __init__(self, sessions, finish_callback):
    self.sessions = sessions;
    self.finish_callback = finish_callback;

  def sendToAll(self, message):
    for session_id in self.sessions:
      pushIOMessage(session_id, message);

  def startGame(self):
    self.result_data = dict();

    # 테스트용 5초 후 게임이 종료된다고 가정
    self.finish_timer = Timer(5, self.finishGame);
    self.finish_timer.start();

    msg = makeMessage(MSG_GAME_STATUS);
    msg["game_status"] = "start";
    self.sendToAll(msg);

  def finishGame(self):
    msg = makeMessage(MSG_GAME_STATUS);
    msg["game_status"] = "end";
    self.sendToAll(msg);
    return self.finish_callback(self.result_data);
