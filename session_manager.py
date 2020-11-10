import threading
import json

client_sockets = dict();
client_sockets_lock = threading.Lock();

def addSession(session_id, client_socket):
  global client_sockets;

  client_sockets_lock.acquire();

  if session_id in client_sockets:
    print("duplicate session", session_id);
    return False;

  client_sockets[session_id] = client_socket;

  client_sockets_lock.release();

  return True;


def getSession(session_id):
  global client_sockets;

  client_sockets_lock.acquire();

  if session_id not in client_sockets:
    print("not exist session", session_id);
    return None;

  client_sockets_lock.release();

  return client_sockets[session_id];


def removeSession(session_id):
  global client_sockets;

  client_sockets_lock.acquire();

  if session_id in client_sockets:
    print("socket closed", session_id);
    client_sockets[session_id].close();
    del client_sockets[session_id];

  client_sockets_lock.release();


def sendMessage(session_id, message):
  global client_sockets;

  msg = json.dumps(message);
  print("send message= ", msg);
  bytes = msg.encode();
  msg_len = len(bytes);

  client_sockets_lock.acquire();

  if session_id not in client_sockets:
    print("cannot find session", session_id);
    return;

  client_socket = client_sockets[session_id];
  client_socket.sendall(msg_len.to_bytes(4, byteorder="little"));
  client_socket.sendall(bytes);

  client_sockets_lock.release();
