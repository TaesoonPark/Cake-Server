import socket
import threading

from session import Session

class SessionManager():
  # 싱글톤 구현을 위한 오버라이딩
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(SessionManager, cls).__new__(cls);
      cls.sessions = dict();
      cls.sessions_lock = threading.Lock();
    return cls.instance;

  # 연결이 확인된 세션 추가
  def add_session(cls, session_id, client_socket):
    cls.sessions_lock.acquire();

    result = False;
    if session_id not in cls.sessions:
      cls.sessions[session_id] = Session(session_id, client_socket);
      result = True;

    cls.sessions_lock.release();

    return result;

  # 세션 아이디로 세션 획득(별 쓸모 없고 좋은 구현이 아님)
  def get_session(cls, session_id):
    cls.sessions_lock.acquire();

    if session_id not in cls.sessions:
      cls.sessions_lock.release();
      print("not exist session", session_id);
      return None;

    cls.sessions_lock.release();

    return cls.sessions[session_id];

  # 연결 끊긴 세션 제거
  def remove_session(cls, session_id):
    cls.sessions_lock.acquire();

    if session_id in cls.sessions:
      print("session closed", session_id);
      cls.sessions[session_id].close_socket();
      if session_id in cls.sessions:
        del cls.sessions[session_id];

    cls.sessions_lock.release();

  # 세션에 메시지 전송. 처음 4바이트는 메시지 길이.
  def send_message(cls, session_id, message):
    try:
      cls.sessions_lock.acquire();

      if session_id in cls.sessions:
        cls.sessions[session_id].send_message(message);
      else:
        print("cannot find session", session_id);

    except socket.error as e:
      print("exception :", e);
    finally:
      cls.sessions_lock.release();

  # 세션 컨텍스트에 데이터 저장
  def add_session_context(cls, session_id, key, value):
    cls.sessions_lock.acquire();

    if session_id in cls.sessions:
      cls.sessions[session_id].add_context(key, value);
    else:
      print("cannot find session", session_id);

    cls.sessions_lock.release();

  # 세션 컨텍스트에서 데이터 불러오기
  def get_session_context(cls, session_id, key):
    cls.sessions_lock.acquire();

    if session_id in cls.sessions:
      result = cls.sessions[session_id].get_context(key);
    else:
      print("cannot find session", session_id);
      result = (False, None);

    cls.sessions_lock.release();

    return result;
