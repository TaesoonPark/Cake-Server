import socket, json

HOST = '127.0.0.1'
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
client_socket.connect((HOST, PORT));

#msg = 'ack';
#data = msg.encode();
#length = len(data);

#client_socket.sendall(length.to_bytes(4, byteorder='little'));
#client_socket.sendall(data);

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

  if data["message_id"] == 0:
    session_id = data["session_id"];
    nickname = str(session_id);

    req = dict();
    req["message_id"] = 1;
    req["session_id"] = session_id;
    req["nickname"] = str(session_id);

    req_msg = json.dumps(req);
    req_bytes = req_msg.encode();
    req_len = len(req_bytes);
    client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
    client_socket.sendall(req_bytes);

  if data["message_id"] == 2:
    req = dict();
    req["message_id"] = 3;
    req["session_id"] = session_id;
    req["text"] = str("hi i'm " + nickname);

    req_msg = json.dumps(req);
    req_bytes = req_msg.encode();
    req_len = len(req_bytes);
    client_socket.sendall(req_len.to_bytes(4, byteorder="little"));
    client_socket.sendall(req_bytes);

  #client_socket.close();
  #break;


print("client socket close");
client_socket.close();
