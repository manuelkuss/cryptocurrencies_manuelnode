# echo-client.py

from ipaddress import ip_address
from logging import exception
import socket
import json
from time import perf_counter
import canonicaljson

HOST = "127.0.0.1"
PORT = 18018

hello_message = {
    "type": "hello",
    "version": "0.8.0",
    "agent": "Kerma-Core Client 0.8"
}

get_peers_message = {
    "type": "getpeers"
}


class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __iter__(self):
        return self

    def __str__(self):
        return f"{self.ip}, {self.port}"

class CheckMessageError(Exception):
    pass

def jsonTOCanonicalJson(msg):
    return canonicaljson.encode_canonical_json(msg) 


def checkMessage(message):
    msg = json.loads(message)
    if "type" in msg and msg["type"] == "hello" and "version" in msg and msg["version"] == "0.8.0":
        print("passed message check")
        return True
    else:
        print("[ERROR] failed message check")
        return False

def discover(peerList):
    for peer in peerList:
        try:
            connectingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connectingSocket.connect((peer.ip, peer.port))
            print("sending type hello message ...")

            # json_hello_message = json.dumps(hello_message)
            # s.sendall(bytes(json_hello_message, encoding="utf-8"))
            marshalledMsg = jsonTOCanonicalJson(hello_message)
            connectingSocket.sendall(marshalledMsg)
            recv_msg = connectingSocket.recv(1024)

            print("Received " + recv_msg.decode("utf-8"))
            if(not checkMessage(recv_msg)):
                raise CheckMessageError("Received hello invalid") 

            recv_msg = connectingSocket.recv(1024)
            print(recv_msg)
            print(canonicaljson.encode_canonical_json(recv_msg.decode("utf-8")))
            decoded_recv_msg = recv_msg.decode("utf-8")
            unmarshalled_recv_msg = json.decoder(recv_msg)
            print("Received " + unmarshalled_recv_msg)
            print(unmarshalled_recv_msg)

            newPeer = Peer(recv_msg.decode("utf-8").ip, 1234)
            
            extendedPeerlist = peerList
            peerList.append(recv_msg.decode("utf-8"))
            print(newPeer)


        except Exception as e: print(e)

        connectingSocket.close()



def main():
    peerList = []
    peerList.append(Peer("128.130.122.101", 18018))

    try: 
        listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to free address for reuse after close
        listeningSocket.bind((HOST, PORT))
        listeningSocket.listen()

        print(f"Listening on {(HOST, PORT)}")

        discover(peerList)

        conn, addr = listeningSocket.accept()
        with conn:
            print(f"Connected by {addr}")
            # while True:
            #     data = conn.recv(1024)
            #     if not data:
            #         break
            #     conn.sendall(data)


    except Exception as e: print(e)

    listeningSocket.close()



if __name__ == '__main__':
    main()