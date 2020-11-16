import socket, json
import time

from multiprocessing import Process
from custom_message import *


def client():
  HOST = '127.0.0.1'
  PORT = 9999

  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
  client_socket.connect((HOST, PORT));

  session_id = -1;
  nickname = "";

  while True:
    recv_data = client_socket.recv(4);
    if len(recv_data) == 0:
      break;
    recv_len = int.from_bytes(recv_data, 'little');
    recv_data = client_socket.recv(recv_len);
    msg = recv_data.decode();
    
    data = json.loads(msg);
    print ("recv=", msg);

    if data["message_id"] == MSG_CONNECTED:
      session_id = data["session_id"];
      nickname = str(session_id);

      req = dict();
      req["message_id"] = MSG_LOGIN;
      req["session_id"] = session_id;
      req["nickname"] = str(session_id);

      req_msg = json.dumps(req);
      req_bytes = req_msg.encode();
      req_len = len(req_bytes);
      client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
      client_socket.sendall(req_bytes);

    if data["message_id"] == MSG_LOGIN_RES:
      req = dict();
      req["message_id"] = MSG_SEND_CHAT;
      req["session_id"] = session_id;
      req["text"] = str("hi i'm " + nickname);

      req_msg = json.dumps(req);
      req_bytes = req_msg.encode();
      req_len = len(req_bytes);
      #client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
      #client_socket.sendall(req_bytes);

      req = dict();
      req["message_id"] = MSG_ROOM_LIST;
      req["session_id"] = session_id;

      req_msg = json.dumps(req);
      req_bytes = req_msg.encode();
      req_len = len(req_bytes);
      client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
      client_socket.sendall(req_bytes);

    if data["message_id"] == MSG_ROOM_LIST_ACK:
      if len(data["room_list"]) == 0:
        req = dict();
        req["message_id"] = MSG_MAKE_ROOM;
        req["session_id"] = session_id;
        req["title"] = "title";

        req_msg = json.dumps(req);
        req_bytes = req_msg.encode();
        req_len = len(req_bytes);
        client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
        client_socket.sendall(req_bytes);
      else:
        req = dict();
        req["message_id"] = MSG_JOIN_ROOM;
        req["session_id"] = session_id;
        req["title"] = data["room_list"][0]["title"];

        req_msg = json.dumps(req);
        req_bytes = req_msg.encode();
        req_len = len(req_bytes);
        client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
        client_socket.sendall(req_bytes);

    if data["message_id"] == MSG_ROOM_STATUS:
      if len(data["session_list"]) == 2:
        req = dict();
        req["message_id"] = MSG_START_GAME;
        req["session_id"] = session_id;

        req_msg = json.dumps(req);
        req_bytes = req_msg.encode();
        req_len = len(req_bytes);
        client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
        client_socket.sendall(req_bytes);

    #client_socket.close();
    #break;


  print("client socket close");
  client_socket.close();

procs = [];
for i in range(5):
  proc = Process(target=client);
  procs.append(proc);
  proc.start();
  time.sleep(0.1);
