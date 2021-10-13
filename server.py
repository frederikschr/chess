import socket
from _thread import *
import ast

server = "192.168.178.75"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(2)
print("Waiting for a connection, Server Started")

connections = 0
idCount = 0
turn = 1
pos_update = {}
figure_ids = []
has_won = None

def threaded_client(conn, id):
    global turn, pos_update, connections, figure_ids, has_won
    conn.send(str.encode(str(id)))
    while True:
        try:
            data = conn.recv(2048).decode()

            #Set
            if data == "change-turn":
                if turn == 1:
                    turn = 2
                else:
                    turn = 1

            elif "remove-figure" in data:
                data = ast.literal_eval(data)
                figure_id = data["remove-figure"]
                figure_ids.remove(figure_id)

            elif "move-figure" in data:
                data = ast.literal_eval(data)
                pos_update = data

            elif "set-figures" in data:
                data = ast.literal_eval(data)
                figure_ids = data["set-figures"]

            elif "has_won" in data:
                data = ast.literal_eval(data)

                print(data)

                has_won = data["has_won"]

            #Get
            elif data == "get-turn":
                conn.send(str.encode(str(turn)))
                continue

            elif data == "get-connections":
                conn.send(str.encode(str(connections)))
                continue

            elif data == "get-pos-update":
                if pos_update:
                    conn.send(str.encode(f"{pos_update['move-figure']}, {pos_update['field_id']}"))
                    continue

            elif data == "get-figures":
                conn.send(str.encode(str(figure_ids)))
                continue

            elif data == "get-won":
                conn.send(str.encode(str(has_won)))

            conn.send(str.encode("200"))

            if not data:
                break

        except Exception as e:
            print(e)
            break

    print("Lost connection")
    conn.close()
    connections -= 1

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    idCount += 1
    connections += 1
    start_new_thread(threaded_client, (conn, idCount))