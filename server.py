import socket
from _thread import *
import ast

server = "192.168.178.75"
port = 6666

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(6)
print("Waiting for a connection, Server Started")

clients = {}
games = []

connections = 0
idCount = 0
gameIdCount = 1

class Game():
    def __init__(self, id, host):
        self.id = id

        self.first_player = host["player_id"]
        self.first_player_name = host["player_name"]

        self.second_player = None
        self.second_player_name = None

        self.can_start = False

        self.turn = self.first_player
        self.pos_updates = []
        self.figure_ids = []
        self.check_fields = []
        self.check = None
        self.has_won = None
        self.win_reason = None

def threaded_client(conn, id):
    global turn, pos_updates, connections, figure_ids, has_won, check_fields, clients, gameIdCount, games
    conn.send(str.encode(str(id)))
    session_id = conn.getpeername()[1]
    player_id = clients[session_id]["player_id"]
    while True:
        try:
            game = clients[session_id]["game"]
            data = conn.recv(2048).decode()


            #Set
            if "set-name" in data:
                data = ast.literal_eval(data)
                clients[session_id]["player_name"] = data["set-name"]

            elif data == "create-game":
                has_game = False
                for game in games:
                    if game.first_player == player_id:
                        has_game = True

                if not has_game:
                    game = Game(gameIdCount, clients[session_id])
                    games.append(game)
                    clients[session_id]["game"] = game
                    gameIdCount += 1

            elif "join-game" in data:
                data = ast.literal_eval(data)
                game_join = data["join-game"]
                for game in games:
                    if not game.first_player == player_id:
                        if game.id == game_join:
                            if not game.second_player:
                                game.second_player = player_id
                                game.second_player_name = data["username"]
                                clients[session_id]["game"] = game
                                game.can_start = True
                                games.remove(game)
                                for game in games:
                                    if game.first_player == player_id:
                                        games.remove(game)

            elif data == "delete-game":
                if game:
                    del(game)
                    clients[session_id]["game"] = None

            elif data == "change-turn":
                if game.turn == game.first_player:
                    game.turn = game.second_player
                else:
                    game.turn = game.first_player

            elif "remove-figure" in data:
                data = ast.literal_eval(data)
                figure_id = data["remove-figure"]
                game.figure_ids.remove(figure_id)

            elif "move-figures" in data:
                data = ast.literal_eval(data)
                game.pos_updates = []
                for update in data["move-figures"]:
                    game.pos_updates.append(update)

            elif "move-figure" in data:
                data = ast.literal_eval(data)
                game.pos_updates = []
                game.pos_updates.append(data)

            elif "set-figures" in data:
                data = ast.literal_eval(data)
                game.figure_ids = data["set-figures"]

            elif "has_won" in data:
                data = ast.literal_eval(data)
                game.has_won = data["has_won"]
                game.win_reason = data["reason"]

            elif "player-check" in data:
                data = ast.literal_eval(data)
                game.check = data["player-check"]

            elif "check-fields" in data:
                data = ast.literal_eval(data)
                game.check_fields = data["check-fields"]

            #Get
            elif data == "get-games":
                games_dict = [{"game_id": game.id, "host": game.first_player_name} for game in games]
                conn.send(str.encode(str(games_dict)))
                continue

            elif data == "get-game-start":
                can_start = False
                if game:
                    if game.can_start:
                        can_start = True
                conn.send(str.encode(str(can_start)))
                continue

            elif data == "get-players":
                players = {"first_player": game.first_player, "first_player_name": game.first_player_name, "second_player": game.second_player, "second_player_name": game.second_player_name}
                conn.send(str.encode(str(players)))
                continue

            elif data == "get-turn":
                conn.send(str.encode(str(game.turn)))
                continue

            elif data == "get-connections":
                conn.send(str.encode(str(connections)))
                continue

            elif data == "get-pos-update":
                if game.pos_updates:
                    conn.send(str.encode(str(game.pos_updates)))
                else:
                    conn.send(str.encode(str({})))
                continue

            elif data == "get-figures":
                conn.send(str.encode(str(game.figure_ids)))
                continue

            elif data == "get-won":
                conn.send(str.encode(str({"has_won": game.has_won, "win_reason": game.win_reason})))
                continue

            elif data == "get-fields-check":
                conn.send(str.encode(str(game.check_fields)))
                continue

            elif data == "get-check":
                conn.send(str.encode(str(game.check)))
                continue

            conn.send(str.encode("200"))

            if not data:
                break

        except Exception as e:
            print(e)
            break

    del clients[session_id]
    print("Lost connection")
    conn.close()
    connections -= 1

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    connections += 1
    clients[conn.getpeername()[1]] = {"player_id": idCount, "game": None, "player_name": None}

    start_new_thread(threaded_client, (conn, idCount))