import socket
import threading
import json

class SessionManager():
  # 싱글톤 구현을 위한 오버라이딩
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(SessionManager, cls).__new__(cls);
      cls.client_sockets = dict();
      cls.client_sockets_lock = threading.Lock();
    return cls.instance;

  # 연결이 확인된 세션 추가
  def add_session(cls, session_id, client_socket):
    cls.client_sockets_lock.acquire();

    if session_id in cls.client_sockets:
      print("duplicate session", session_id);
      return False;

    cls.client_sockets[session_id] = client_socket;

    cls.client_sockets_lock.release();

    return True;

  # 세션 아이디로 세션 획득(별 쓸모 없고 좋은 구현이 아님)
  def get_session(cls, session_id):
    cls.client_sockets_lock.acquire();

    if session_id not in cls.client_sockets:
      print("not exist session", session_id);
      return None;

    cls.client_sockets_lock.release();

    return cls.client_sockets[session_id];


  # 연결 끊긴 세션 제거
  def remove_session(cls, session_id):
    cls.client_sockets_lock.acquire();

    if session_id in cls.client_sockets:
      print("socket closed", session_id);
      cls.client_sockets[session_id].close();
      del cls.client_sockets[session_id];

    cls.client_sockets_lock.release();


  # 세션에 메시지 전송. 처음 4바이트는 메시지 길이.
  def send_message(cls, session_id, message):
    msg = json.dumps(message);
    print("send message=", msg);
    bytes = msg.encode();
    msg_len = len(bytes);

    try:
      cls.client_sockets_lock.acquire();

      if session_id not in cls.client_sockets:
        print("cannot find session", session_id);
        return;

      client_socket = cls.client_sockets[session_id];
      client_socket.sendall(msg_len.to_bytes(4, byteorder="little"));
      client_socket.sendall(bytes);
    except socket.error as e:
      print("exception :", e);
    finally:
      cls.client_sockets_lock.release();
