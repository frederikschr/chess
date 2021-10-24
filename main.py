import pygame
import sys
from network import Network
import ast

"""
To-Do:
-Umwandlung
"""

class Game():
    def __init__(self):
        self.stage = 1
        self.FPS = 60
        self.is_connected = False
        self.username = None
        self.selected = False
        self.name_text = "Enter Name"
        self.events = None
        self.sound = True

    def run(self):
        while True:
            if self.stage == 1:
                self.startscreen()

            elif self.stage == 2:
                self.gameslist()

            elif self.stage == 3:
                self.create_board()

            elif self.stage == 4:
                self.game()

            elif self.stage == 5:
                self.settings()

            else:
                pass

            self.events = pygame.event.get()
            self.handle_quit()
            clock.tick(self.FPS)
            pygame.display.update()

    def handle_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def connect(self):
        try:
            self.n = Network()
            self.player_id = int(self.n.get_id())
            self.player = Player(self.player_id)
            return True
        except:
            return False

    def startscreen(self):
        screen.fill((133, 94, 66))
        connect_btn = Button((255, 255, 255), width / 2 - 50, height / 1.5, 100, 100, text="Play")
        name_button = Button((255, 255, 255), width / 2 - 100, height / 2, 200, 50)
        settings_button = Button((255, 255, 255), width - 125, height - 100, 100, 75, text="Settings")

        if self.selected:
            for event in self.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.selected = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_text = self.name_text[:-1]
                    else:
                        if len(self.name_text) <= 15:
                            self.name_text += event.unicode

        if name_button.isClicked(pygame.mouse.get_pos()):
            if not self.selected:
                self.selected = True
                self.name_text = ""
            else:
                self.selected = False
                self.name_text = "Enter Name"

        if connect_btn.isClicked(pygame.mouse.get_pos()):
            if self.name_text != "":
                if self.connect():
                    self.n.send(str({"set-name": self.name_text}))
                    self.username = self.name_text
                    self.is_connected = True
                    self.stage = 2

        if settings_button.isClicked(pygame.mouse.get_pos()):
            self.stage = 5

        connect_btn.draw(border=3)
        settings_button.draw(border=3)
        pygame.draw.line(screen, (255, 255, 255), (width / 2 - 100, height / 2 + 50), (width / 2 + 100, height / 2 + 50), 3)
        title = big_font.render("Chess", None, (255, 255, 255))
        name = small_font.render(str(self.name_text), None, (255, 255, 255))
        screen.blit(title, (width / 2 - title.get_width() / 2, height / 3))
        screen.blit(name, (width / 2 - name.get_width() / 2, height / 2))

    def gameslist(self):
        font = pygame.font.SysFont("Comic Sans MS", 40)
        small_font = pygame.font.SysFont("Comic Sans MS", 25)
        screen.fill((133, 94, 66))
        create_game_btn = Button((255, 255, 255), width / 2 + 250, height / 3, 100, 60, text="Create")

        connections = int(self.n.send("get-connections"))
        games = ast.literal_eval(self.n.send("get-games"))

        if create_game_btn.isClicked(pygame.mouse.get_pos()):
            self.n.send("create-game")

        y_count = height / 2

        game_join_buttons = []

        for game in games:
            game_text = small_font.render(f"{game['game_id']}.  {game['host']}", None, (255, 255, 255))
            if not game["host"] == self.username:
                game_join_btn = Button((255, 255, 255), width / 2 + 150, y_count, 50, 50, text="Join", data=game["game_id"])
                game_join_buttons.append(game_join_btn)
            screen.blit(game_text, (width / 2 - game_text.get_width() / 2 , y_count))
            y_count += 100

        for join_btn in game_join_buttons:
            join_btn.draw(border=3)
            if join_btn.isClicked(pygame.mouse.get_pos()):
                self.n.send(str({"join-game": join_btn.data}))

        if ast.literal_eval(self.n.send("get-game-start")) == True:
            self.stage = 3

        create_game_btn.draw(border=3)
        games_text = font.render("Games", None, (255, 255, 255))
        conn_text = font.render(str(connections), None, (255, 255, 255))
        screen.blit(games_text, (width / 2 - games_text.get_width() / 2, height / 3))
        screen.blit(conn_text, (width - (conn_text.get_width() * 2), height - 50))

    def create_board(self):
        self.board = Board(self.player, ast.literal_eval(self.n.send("get-players")), self, self.n)
        self.board.create()
        self.n.send(str({"set-figures": [figure.id for figure in self.board.figures]}))
        self.old_pos_updates = None
        self.stage = 4
        if self.sound:
            pygame.mixer.Sound.play(start_sound)

    def settings(self):
        screen.fill((133, 94, 66))
        settings_text = big_font.render("Settings", None, (255, 255, 255))
        sounds_button = Button((255, 255, 255), width / 2 - 50, height / 2, 75, 50, text="Sound")
        back_button = Button((255, 255, 255), width - 125, height - 100, 100, 75, text="Back")

        if sounds_button.isClicked(pygame.mouse.get_pos()):
            self.sound = not self.sound

        if back_button.isClicked(pygame.mouse.get_pos()):
            self.stage = 1

        sound_text = small_font.render("On" if self.sound else "Off", None, (255, 255, 255))
        screen.blit(sound_text, (width / 2 + 50, height / 2 + sound_text.get_height() / 2))
        screen.blit(settings_text, (width / 2 - settings_text.get_width() / 2, height / 3))
        sounds_button.draw(border=3)
        back_button.draw(border=3)


    def game(self):
        turn = int(self.n.send("get-turn"))
        pos_updates = ast.literal_eval(self.n.send("get-pos-update"))
        figure_ids = ast.literal_eval(self.n.send("get-figures"))
        #has_won = self.n.send("get-won")
        removed = False
        has_pos_updates = False
        for figure in self.board.figures:
            if figure.id not in figure_ids:
                self.board.figures.remove(figure)
                removed = True
                if figure in self.player.figures:
                    self.player.figures.remove(figure)
                if figure == self.board.king.attacker:
                    self.board.king.attacker = None
                for field in self.board.fields:
                    if field.figure == figure:
                        field.figure = None

        if pos_updates != {} and pos_updates != self.old_pos_updates:
            self.old_pos_updates = pos_updates
            has_pos_updates = True
            for pos_update in pos_updates:
                field = self.board.get_field_by_id(int(pos_update["field_id"]))
                figure = self.board.get_figure(int(pos_update["move-figure"]))
                old_field = self.board.get_field_by_coords([figure.coordinates[0], figure.coordinates[1]])
                old_field.figure = None
                field.update_figure(figure)
            self.board.set_all_moveable_fields()
            self.board.check_blocks_check()

        if self.sound and has_pos_updates:
            if not self.board.get_check():
                if removed:
                    pygame.mixer.Sound.play(capture_sound)
                else:
                    if len(pos_updates) > 1:
                        pygame.mixer.Sound.play(rochade_sound)
                    else:
                        pygame.mixer.Sound.play(move_sound)
            else:
                if self.board.get_checkmate():
                    pygame.mixer.Sound.play(checkmate_sound)
                else:
                    pygame.mixer.Sound.play(check_sound)

        if not self.board.king.is_checkmate():
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for field in self.board.fields:
                        if field.is_clicked(pos[0], pos[1]):
                            if self.player.selected_field:
                                if field != self.player.selected_field:
                                    if self.player.id == turn:
                                        if field.coordinates in self.player.selected_field.figure.moveable_fields:
                                            rochade = False
                                            if not self.board.king.in_check():
                                                if field.has_figure():
                                                    if field.figure in self.player.figures:
                                                        if isinstance(self.player.selected_field.figure, King):
                                                            for figure in self.board.king.check_rochade():
                                                                if figure == field.figure:
                                                                    rook = figure
                                                            if rook.coordinates[1] > self.board.king.coordinates[1]:
                                                                new_field_king = self.board.get_field_by_coords([self.board.king.coordinates[0], self.board.king.coordinates[1] + 2])
                                                                new_field_rook = self.board.get_field_by_coords([self.board.king.coordinates[0], self.board.king.coordinates[1] + 1])
                                                            else:
                                                                new_field_king = self.board.get_field_by_coords([self.board.king.coordinates[0], self.board.king.coordinates[1] - 2])
                                                                new_field_rook = self.board.get_field_by_coords([self.board.king.coordinates[0], self.board.king.coordinates[1] - 1])
                                                            rochade = True
                                                        else:
                                                            break
                                                    else:
                                                        self.n.send(str({"remove-figure": field.figure.id}))
                                            else:

                                                print("check")

                                                check_fields = ast.literal_eval(self.n.send("get-fields-check"))
                                                if not self.player.selected_field.figure in self.board.king.get_attacker_beaters():
                                                    if not self.board.king.can_move_between(self.player.selected_field.figure, check_fields):
                                                        if not self.player.selected_field.coordinates == self.board.king.coordinates:
                                                            break
                                                    else:
                                                        if not field.coordinates in check_fields:
                                                            break
                                                        else:
                                                            self.player.selected_field.figure.blocks_check = True

                                                elif self.board.king.can_move_between(self.player.selected_field.figure, check_fields):
                                                    if not field.coordinates in check_fields:
                                                        break
                                                else:
                                                    self.n.send(str({"remove-figure": field.figure.id}))
                                        else:
                                            break

                                        if rochade:
                                            self.n.send(str({"move-figures": [{"move-figure": self.player.selected_field.figure.id, "field_id": new_field_king.id},
                                                                              {"move-figure": field.figure.id, "field_id": new_field_rook.id}]}))
                                        else:
                                            self.n.send(str({"move-figure": self.player.selected_field.figure.id, "field_id": field.id}))

                                        self.n.send("change-turn")
                                        self.player.selected_field.figure = None
                                        self.player.selected_field.is_highlighted = False
                                        self.player.selected_field = None

                                else:
                                    field.is_highlighted = False
                                    self.player.selected_field = None
                            else:
                                if field.has_figure():
                                    if field.figure.player == self.player.id:
                                        self.player.selected_field = field
                                        field.is_highlighted = True

        else:
            self.n.send(str({"has_won": 2 if self.player.id == 1 else 1}))

        self.board.draw()

class Field():
    def __init__(self, id, game_coord_y, game_coord_x, win_pos_y, win_pos_x, size, figure):
        self.id = id
        self.coordinates = [game_coord_y, game_coord_x]
        self.win_pos_y = win_pos_y
        self.win_pos_x = win_pos_x
        self.size = size
        self.color = ()

        self.is_highlighted = False

        self.figure = figure

    def is_clicked(self, mouse_x, mouse_y):
        if mouse_x > self.win_pos_x and mouse_x < self.win_pos_x + self.size:
            if mouse_y > self.win_pos_y and mouse_y < self.win_pos_y + self.size:
                return True
        return False

    def update_figure(self, figure):
        self.figure = figure
        self.figure.win_pos_x = self.win_pos_x
        self.figure.win_pos_y = self.win_pos_y
        self.figure.coordinates[0] = self.coordinates[0]
        self.figure.coordinates[1] = self.coordinates[1]

        if isinstance(figure, (Pawn, King, Rook)):
            if figure.first_move:
                figure.first_move = False

    def has_figure(self):
        return True if self.figure else False

    def draw_figure(self):
        self.figure.draw()

    def get_figure(self):
        return self.figure

class Board():
    def __init__(self, player, players, game, n):
        self.fields = []
        self.figures = []
        self.field_size = height / 8
        self.player = player
        self.game = game
        self.king = None
        self.n = n
        self.first_player = players["first_player"]
        self.second_player = players["second_player"]

    def create(self):
        win_pos_y = 0
        win_pos_x = 0
        field_id_count = 1
        figure_id_count = 1
        for y in range(8):
            if self.player.id == self.first_player:
                owner = self.player.id if y > 2 else self.second_player
            else:
                owner = self.player.id if y < 3 else self.first_player

            for x in range(8):
                if y == 1 or y == 6:
                    figure = Pawn(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                elif y == 0 or y == 7:
                    if x == 0 or x == 7:
                        figure = Rook(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                    elif x == 1 or x == 6:
                        figure = Knight(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                    elif x == 2 or x == 5:
                        figure = Bishop(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                    elif x == 3:
                        figure = Queen(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                    elif x == 4:
                        figure = King(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)
                        if figure.player == self.player.id:
                            self.king = figure

                    else:
                        figure = None
                else:
                    figure = None

                self.fields.append(Field(field_id_count, y + 1, x + 1, win_pos_y, win_pos_x, self.field_size, figure))

                if figure:
                    figure_id_count += 1
                    self.figures.append(figure)
                    if figure.player == self.player.id:
                        self.player.figures.append(figure)

                field_id_count += 1
                win_pos_x += self.field_size

            win_pos_x = 0
            win_pos_y += self.field_size

        self.color_fields()
        self.set_all_moveable_fields()

    def color_fields(self):
        for field in self.fields:
            if field.coordinates[0] % 2 == 0:
                if field.coordinates[1] % 2 == 0:
                    color = (255, 255, 255)
                else:
                    color = (133, 94, 66)
            else:
                if field.coordinates[1] % 2 == 0:
                    color = (133, 94, 66)
                else:
                    color = (255, 255, 255)

            field.color = color

    def draw(self):
        screen.fill((133, 94, 66))
        for field in self.fields:
            outline = False
            if self.player.selected_field:
                if field.coordinates in self.player.selected_field.figure.moveable_fields:
                    outline = True
                else:
                    outline = False

            if field.is_highlighted:
                pygame.draw.rect(screen, (255, 0, 0), (field.win_pos_x, field.win_pos_y, self.field_size, self.field_size))
            else:
                pygame.draw.rect(screen, field.color, (field.win_pos_x, field.win_pos_y, self.field_size, self.field_size))
                if outline:
                    pygame.draw.rect(screen, (0, 0, 255), (field.win_pos_x, field.win_pos_y, self.field_size, self.field_size), 3)

            if field.has_figure():
                field.draw_figure()

    def set_all_moveable_fields(self):
        for figure in self.figures:
            figure.blocks_check = False
            if not isinstance(figure, King):
                figure.set_moveable_fields()
        self.king.set_moveable_fields()

        if self.king.in_check():
            check_fields = ast.literal_eval(self.n.send("get-fields-check"))
            for figure in self.figures:
                if figure.player == self.player.id:
                    self.king.get_attacker_beaters()
                    self.king.can_move_between(figure, check_fields)

    def check_blocks_check(self):
        for move_figure in self.player.figures:
            for figure in self.figures:
                if figure.player != self.player.id:
                    if move_figure in figure.figures_to_king:
                        if len(figure.figures_to_king) == 1:
                            moveable_fields = []
                            for field in figure.line_fields:
                                if not isinstance(move_figure, Pawn):
                                    if field in move_figure.moveable_fields:
                                        moveable_fields.append(field)
                                else:
                                    if field in move_figure.beatable_fields:
                                        moveable_fields.append(field)

                            if figure.coordinates in move_figure.moveable_fields:
                                moveable_fields.append(figure.coordinates)

                            move_figure.moveable_fields = moveable_fields


    def get_field_by_id(self, id):
        for field in self.fields:
            if field.id == id:
                return field

    def get_field_by_coords(self, coords):
        for field in self.fields:
            if field.coordinates == coords:
                return field
        return None

    def get_fields_by_coords(self, coords):
        fields = []
        for field in self.fields:
            if field.coordinates in coords:
                fields.append(field)
        return fields

    def get_figure(self, id):
        for figure in self.figures:
            if figure.id == id:
                return figure
        return None

    def get_check(self):
        for figure in self.figures:
            if isinstance(figure, King):
                if figure.in_check():
                    return True
        return False

    def get_checkmate(self):
        for figure in self.figures:
            if isinstance(figure, King):
                if figure.is_checkmate():
                    return True
        return False

class Player():
    def __init__(self, id):
        self.id = id

        self.figures = []

        self.has_won = False
        self.has_turn = False

        self.selected_field = None

class Figure():
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        self.coordinates = [game_coord_y, game_coord_x]
        self.win_pos_y = win_pos_y
        self.win_pos_x = win_pos_x

        self.board = board

        self.id = id

        self.player = player

        self.moveable_fields = []
        self.beatable_fields = []

        self.figures_to_king = []

        self.blocks_check = False

    def draw(self):
        if self.player == self.board.first_player:
            screen.blit(self.image_w, self.image_w.get_rect(center=(self.win_pos_x + (self.board.field_size / 2), self.win_pos_y + (self.board.field_size / 2))))
        else:
            screen.blit(self.image_b, self.image_w.get_rect(center=(self.win_pos_x + (self.board.field_size / 2), self.win_pos_y + (self.board.field_size / 2))))

    def set_moveable_fields(self):
        raise NotImplementedError("Please Implement this method")

class Pawn(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)
        self.first_move = True

        self.image_w = pygame.image.load("./assets/pawn_w.png")
        self.image_b = pygame.image.load("./assets/pawn_b.png")

    def set_moveable_fields(self):
        fields = []
        beatable_fields = []

        if self.player == self.board.first_player:
            direction = -1
        else:
            direction = 1

        field_tr = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1] + 1])
        field_tl = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1] - 1])
        field_top = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1]])
        field_top2 = self.board.get_field_by_coords([self.coordinates[0] + direction * 2, self.coordinates[1]])

        if field_tr:
            if field_tr.has_figure():
                if field_tr.figure.player != self.player:
                    fields.append(field_tr.coordinates)
            beatable_fields.append(field_tr.coordinates)
        if field_tl:
            if field_tl.has_figure():
                if field_tl.figure.player != self.player:
                    fields.append(field_tl.coordinates)
            beatable_fields.append(field_tl.coordinates)
        if field_top:
            if not field_top.has_figure():
                fields.append(field_top.coordinates)
        if self.first_move:
            if field_top:
                if not field_top.has_figure():
                    if field_top2:
                        if not field_top2.has_figure():
                            fields.append(field_top2.coordinates)

        self.moveable_fields = fields
        self.beatable_fields = beatable_fields

class King(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)
        self.attacker = None
        self.first_move = True

        self.image_w = pygame.image.load("./assets/king_w.png")
        self.image_b = pygame.image.load("./assets/king_b.png")

    def set_moveable_fields(self):
        fields = []

        field_objs = self.board.get_fields_by_coords([[self.coordinates[0] + 1, self.coordinates[1]],
                                                      [self.coordinates[0] + 1, self.coordinates[1] + 1],
                                                      [self.coordinates[0], self.coordinates[1] + 1],
                                                      [self.coordinates[0] - 1, self.coordinates[1] + 1],
                                                      [self.coordinates[0] - 1, self.coordinates[1]],
                                                      [self.coordinates[0] - 1, self.coordinates[1] - 1],
                                                      [self.coordinates[0], self.coordinates[1] - 1],
                                                      [self.coordinates[0] + 1, self.coordinates[1] - 1]])

        for field in field_objs:
            append = True
            for figure in self.board.figures:
                if figure.player != self.player:
                    if not isinstance(figure, Pawn):
                        if field.coordinates in figure.moveable_fields:
                            append = False
                    else:
                        if field.coordinates in figure.beatable_fields:
                            append = False
                else:
                    if isinstance(figure, Rook):
                        if figure in self.check_rochade():
                            fields.append(figure.coordinates)

            if field.has_figure():
                if field.figure.player == self.player:
                    append = False
            if append:
                fields.append(field.coordinates)

        self.moveable_fields = fields

    def in_check(self):
        for figure in self.board.figures:
            if figure not in self.board.player.figures:
                if self.coordinates in figure.moveable_fields:
                    self.attacker = figure
                    return True
        return False

    def get_attacker_beaters(self):
        figures = []
        if self.attacker:
            for figure in self.board.player.figures:
                if self.attacker.coordinates in figure.moveable_fields:
                    figures.append(figure)
                    figure.moveable_fields = [self.attacker.coordinates]

        return figures

    def can_move_between(self, figure, check_fields):
        moveable_fields = []
        for field in figure.moveable_fields:
            if field in check_fields:
                moveable_fields.append(field)
        if moveable_fields:
            figure.moveable_fields = moveable_fields
            return True
        return False

    def is_checkmate(self):
        return False
        #if self.moveable_fields == [] and self.in_check():
            #return True

    def check_rochade(self):
        rooks = []
        if self.first_move and not self.in_check():
            for figure in self.board.player.figures:
                if isinstance(figure, Rook):
                    if figure.first_move:
                        append = True
                        for i in range(3):
                            i += 1
                            if figure.coordinates[1] < self.coordinates[1]:
                                field = self.board.get_field_by_coords([figure.coordinates[0], figure.coordinates[1] + i])
                                if field.has_figure():
                                    if not field.figure == self:
                                        append = False
                                for f in self.board.figures:
                                    if f.player != self.player:
                                        if field.coordinates in f.moveable_fields:
                                            append = False
                            else:
                                field = self.board.get_field_by_coords([figure.coordinates[0], figure.coordinates[1] - i])
                                if field.has_figure():
                                    if not field.figure == self:
                                        append = False

                                for f in self.board.figures:
                                    if f.player != self.player:
                                        if field.coordinates in f.moveable_fields:
                                            append = False
                                            break
                        if append:
                            rooks.append(figure)
        return rooks

class Rook(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

        self.first_move = True

        self.image_w = pygame.image.load("./assets/rook_w.png")
        self.image_b = pygame.image.load("./assets/rook_b.png")

        self.line_fields = []

    def set_moveable_fields(self):
        self.figures_to_king.clear()
        fields = []
        beatable_fields = []

        for i in range(4):
            if i == 0:
                y_counter = 1
                x_counter = 0
            elif i == 1:
                y_counter = -1
                x_counter = 0
            elif i == 2:
                y_counter = 0
                x_counter = 1
            else:
                y_counter = 0
                x_counter = -1

            line_fields = []
            figures_to_king = []
            append = True
            for x in range(9):
                field = self.board.get_field_by_coords([self.coordinates[0] + y_counter, self.coordinates[1] + x_counter])
                if field:
                    if field.has_figure():
                        if field.figure.player != self.player:
                            if append:
                                fields.append(field.coordinates)
                            if isinstance(field.figure, King):
                                if int(self.board.n.send("get-turn")) != self.player:
                                    self.board.game.n.send(str({"check-fields": line_fields}))
                                self.line_fields = line_fields
                                self.figures_to_king = figures_to_king
                                break
                            else:
                                line_fields.append(field.coordinates)
                                figures_to_king.append(field.figure)
                            append = False
                        else:
                            break
                    else:
                        line_fields.append(field.coordinates)
                        if append:
                            fields.append(field.coordinates)
                        else:
                            beatable_fields.append(field.coordinates)
                            self.line_fields = line_fields

                    if y_counter != 0:
                        if y_counter > 0:
                            y_counter += 1
                        else:
                            y_counter -= 1
                    else:
                        if x_counter > 0:
                            x_counter += 1
                        else:
                            x_counter -= 1

        self.moveable_fields = fields
        self.beatable_fields = beatable_fields

class Knight(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

        self.image_w = pygame.image.load("./assets/knight_w.png")
        self.image_b = pygame.image.load("./assets/knight_b.png")

    def set_moveable_fields(self):
        fields = []

        field_objs = self.board.get_fields_by_coords([[self.coordinates[0] + 2, self.coordinates[1] + 1],
                                                      [self.coordinates[0] + 2, self.coordinates[1] - 1],
                                                      [self.coordinates[0] + 1, self.coordinates[1] + 2],
                                                      [self.coordinates[0] + 1, self.coordinates[1] - 2],
                                                      [self.coordinates[0] - 1, self.coordinates[1] + 2],
                                                      [self.coordinates[0] - 1, self.coordinates[1] - 2],
                                                      [self.coordinates[0] - 2, self.coordinates[1] + 1],
                                                      [self.coordinates[0] - 2, self.coordinates[1] - 1],
                                                      ])
        for field in field_objs:
            if field.has_figure():
                if field.figure.player != self.player:
                    fields.append(field.coordinates)
            else:
                fields.append(field.coordinates)

        self.moveable_fields = fields

class Queen(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

        self.image_w = pygame.image.load("./assets/queen_w.png")
        self.image_b = pygame.image.load("./assets/queen_b.png")

        self.line_fields = []

        self.figures_to_king = []

    def set_moveable_fields(self):
        self.figures_to_king.clear()
        fields = []
        beatable_fields = []

        for i in range(8):
            if i == 0:
                y_counter = 1
                x_counter = 0
            elif i == 1:
                y_counter = -1
                x_counter = 0
            elif i == 2:
                y_counter = 0
                x_counter = 1
            elif i == 3:
                y_counter = 0
                x_counter = -1
            elif i == 4:
                y_counter = -1
                x_counter = -1
            elif i == 5:
                y_counter = 1
                x_counter = 1
            elif i == 6:
                y_counter = 1
                x_counter = -1
            else:
                y_counter = -1
                x_counter = 1

            line_fields = []
            figures_to_king = []
            append = True
            for i in range(8):
                field = self.board.get_field_by_coords([self.coordinates[0] + y_counter, self.coordinates[1] + x_counter])
                if field:
                    if field.has_figure():
                        if field.figure.player != self.player:
                            if append:
                                fields.append(field.coordinates)
                            if isinstance(field.figure, King):
                                if int(self.board.n.send("get-turn")) != self.player:
                                    self.board.game.n.send(str({"check-fields": line_fields}))
                                self.line_fields = line_fields
                                self.figures_to_king = figures_to_king
                                break
                            else:
                                line_fields.append(field.coordinates)
                                figures_to_king.append(field.figure)
                            append = False
                        else:
                            break
                    else:
                        line_fields.append(field.coordinates)
                        if append:
                            fields.append(field.coordinates)
                        else:
                            beatable_fields.append(field.coordinates)

                    if y_counter != 0:
                        if y_counter > 0:
                            y_counter += 1
                        else:
                            y_counter -= 1
                    if x_counter != 0:
                        if x_counter > 0:
                            x_counter += 1
                        else:
                            x_counter -= 1

        self.moveable_fields = fields
        self.beatable_fields = beatable_fields

class Bishop(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

        self.image_w = pygame.image.load("./assets/bishop_w.png")
        self.image_b = pygame.image.load("./assets/bishop_b.png")

        self.line_fields = []

        self.figures_to_king = []

    def set_moveable_fields(self):
        self.figures_to_king.clear()
        fields = []
        beatable_fields = []

        for i in range(4):
            if i == 0:
                y_counter = 1
                x_counter = 1
            elif i == 1:
                y_counter = -1
                x_counter = 1
            elif i == 2:
                y_counter = -1
                x_counter = -1
            else:
                y_counter = 1
                x_counter = -1

            line_fields = []
            figures_to_king = []
            append = True
            for x in range(8):
                field = self.board.get_field_by_coords([self.coordinates[0] + y_counter, self.coordinates[1] + x_counter])
                if field:
                    if field.has_figure():
                        if field.figure.player != self.player:
                            if append:
                                fields.append(field.coordinates)
                            if isinstance(field.figure, King):
                                if int(self.board.n.send("get-turn")) != self.player:
                                    self.board.game.n.send(str({"check-fields": line_fields}))
                                self.line_fields = line_fields
                                self.figures_to_king = figures_to_king
                                break
                            else:
                                line_fields.append(field.coordinates)
                                figures_to_king.append(field.figure)
                            append = False
                        else:
                            break
                    else:
                        line_fields.append(field.coordinates)
                        if append:
                            fields.append(field.coordinates)
                        else:
                            beatable_fields.append(field.coordinates)

                    if y_counter > 0:
                        y_counter += 1
                    else:
                        y_counter -= 1

                    if x_counter > 0:
                        x_counter += 1
                    else:
                        x_counter -= 1

        self.moveable_fields = fields
        self.beatable_fields = beatable_fields

class Button():
    def __init__(self, color, x, y, width, height, text=None, text_size=None, data=None):
        self.color = color
        self.default_color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_size = text_size
        self.data = data

    def draw(self, outline=None, transparent=False, border=0):
        if outline:
            pygame.draw.rect(screen, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), border)

        if transparent:
                rect = pygame.Surface((self.width, self.height))
                rect.set_alpha(128)
                rect.fill(self.color)
                screen.blit(rect, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border)

        if self.text:
            font = pygame.font.SysFont('comicsans', self.text_size if self.text_size else 30)
            text = font.render(self.text, 1, (255, 255, 255))
            screen.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

    def isClicked(self, pos):
        if self.isOver(pos):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return True
        return False

pygame.init()

width, height = 1000, 800

screen = pygame.display.set_mode([width, height])

pygame.font.init()

small_font = pygame.font.SysFont("Comic Sans MS", 20)
big_font = pygame.font.SysFont("Comic Sans MS", 40)

start_sound = pygame.mixer.Sound("./assets/start_sound.mp3")
move_sound = pygame.mixer.Sound("./assets/move_sound.mp3")
capture_sound = pygame.mixer.Sound("./assets/capture_sound.mp3")
rochade_sound = pygame.mixer.Sound("./assets/rochade_sound.mp3")
check_sound = pygame.mixer.Sound("./assets/check_sound.mp3")
checkmate_sound = pygame.mixer.Sound("./assets/checkmate_sound.mp3")

pygame.display.set_caption("Chess")

clock = pygame.time.Clock()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
