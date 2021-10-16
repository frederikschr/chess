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
pos_updates = []
figure_ids = []
check_fields = []
has_won = None

def threaded_client(conn, id):
    global turn, pos_updates, connections, figure_ids, has_won, check_fields
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

            elif "move-figures" in data:
                data = ast.literal_eval(data)
                pos_updates = []
                for update in data["move-figures"]:
                    pos_updates.append(update)

            elif "move-figure" in data:
                data = ast.literal_eval(data)
                pos_updates = []
                pos_updates.append(data)

            elif "set-figures" in data:
                data = ast.literal_eval(data)
                figure_ids = data["set-figures"]

            elif "has_won" in data:
                data = ast.literal_eval(data)
                has_won = data["has_won"]

            elif "check-fields" in data:
                data = ast.literal_eval(data)
                check_fields = data["check-fields"]

            #Get
            elif data == "get-turn":
                conn.send(str.encode(str(turn)))
                continue

            elif data == "get-connections":
                conn.send(str.encode(str(connections)))
                continue

            elif data == "get-pos-update":
                if pos_updates:
                    conn.send(str.encode(str(pos_updates)))
                else:
                    conn.send(str.encode(str({})))
                continue

            elif data == "get-figures":
                conn.send(str.encode(str(figure_ids)))
                continue

            elif data == "get-won":
                conn.send(str.encode(str(has_won)))
                continue

            elif data == "get-fields-check":
                conn.send(str.encode(str(check_fields)))
                continue

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