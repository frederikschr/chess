import pygame
import sys
from network import Network
import ast

class Game():
    def __init__(self):
        self.FPS = 60
        self.over = False

    def run(self):
        self.menu()
        self.game()

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
            self.board = Board(self.player)
            return True
        except:
            return False

    def menu(self):
        connected = False
        connect_btn = Button((255, 0, 0), width / 2 - 50, height / 1.5, 100, 100, text="Play")
        while True:
            if connect_btn.isClicked(pygame.mouse.get_pos()):
                if self.connect():
                    connected = True
                    connections = int(self.n.send("get-connections"))
                    if connections < 2:
                        info = font.render("Waiting for second player...", None, (255, 0, 0))
                        screen.blit(info, (width / 2 - info.get_width() / 2, height / 2))
                    else:
                        break

            if connected:
                connections = int(self.n.send("get-connections"))
                if connections != 1:
                    break
            else:
                connect_btn.draw()

            title = font.render("Chess", None, (255, 0, 0))
            screen.blit(title, (width / 2 - title.get_width() / 2, height / 3))
            self.handle_quit()
            clock.tick(self.FPS)
            pygame.display.update()

    def game(self):
        self.board.create()
        old_pos_update = None
        self.n.send(str({"set-figures": [figure.id for figure in self.board.figures]}))
        while True:
            turn = int(self.n.send("get-turn"))
            pos_update = self.n.send("get-pos-update")
            update_fields = False
            figure_ids = ast.literal_eval(self.n.send("get-figures"))
            #has_won = self.n.send("get-won")

            if pos_update != "200" and pos_update != old_pos_update:
                old_pos_update = pos_update
                update_fields = True
                ids = pos_update.split(",")
                field = self.board.get_field_by_id(int(ids[1]))
                figure = self.board.get_figure(int(ids[0]))
                field.update_figure(figure)

            for figure in self.board.figures:
                if figure.id not in figure_ids:
                    self.board.figures.remove(figure)
                    if figure in self.player.figures:
                        self.player.figures.remove(figure)
                    for field in self.board.fields:
                        if field.figure == figure:
                            field.figure = None
                else:
                    if update_fields:
                        figure.set_moveable_fields()

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

                                                if not self.board.king.in_check():
                                                    if field.has_figure():
                                                        if field.figure in self.player.figures:
                                                            break
                                                        else:
                                                            self.n.send(str({"remove-figure": field.figure.id}))

                                                else:
                                                    if not self.player.selected_field.coordinates == self.board.king.coordinates:
                                                        break

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
            self.handle_quit()
            clock.tick(self.FPS)
            pygame.display.update()

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

        if isinstance(figure, Pawn):
            if figure.first_move:
                figure.first_move = False

    def has_figure(self):
        return True if self.figure else False

    def draw_figure(self):
        self.figure.draw()

    def get_figure(self):
        return self.figure

class Board():
    def __init__(self, player):
        self.fields = []
        self.figures = []
        self.field_size = height / 8
        self.player = player

        self.king = None

    def create(self):
        win_pos_y = 0
        win_pos_x = 0
        field_id_count = 1
        figure_id_count = 1
        for y in range(8):
            owner = 2 if y < 2 else 1
            for x in range(8):
                if y == 1 or y == 6:
                    figure = Pawn(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

                elif y == 0 or y == 7:
                    if x == 0 or x == 7:
                        figure = Rook(y + 1, x + 1, win_pos_y, win_pos_x, figure_id_count, owner, self)

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
                    color = (0, 0, 0)
            else:
                if field.coordinates[1] % 2 == 0:
                    color = (0, 0, 0)
                else:
                    color = (255, 255, 255)

            field.color = color

    def draw(self):
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
            figure.set_moveable_fields()

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

    def draw(self):
        if self.player == 1:
            pygame.draw.rect(screen, (255, 0, 0), (self.win_pos_x, self.win_pos_y, 50, 50))
        else:
            pygame.draw.rect(screen, (0, 255, 0), (self.win_pos_x, self.win_pos_y, 50, 50))

        textsurface = font.render(self.__class__.__name__, None, (255, 255, 255))
        screen.blit(textsurface, (self.win_pos_x, self.win_pos_y))

    def can_go_to(self, coords):
        pass

    def set_moveable_fields(self):
        raise NotImplementedError("Please Implement this method")

class Pawn(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)
        self.first_move = True
        self.beatable_fields = []

    def set_moveable_fields(self):
        fields = []
        beatable_fields = []

        if self.player == 1:
            direction = -1
        else:
            direction = 1

        field_tr = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1] + 1])
        field_tl = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1] - 1])
        field_top = self.board.get_field_by_coords([self.coordinates[0] + direction, self.coordinates[1]])
        field_top2 = self.board.get_field_by_coords([self.coordinates[0] + direction * 2, self.coordinates[1]])

        if field_tr:
            if field_tr.has_figure():
                fields.append(field_tr.coordinates)
            beatable_fields.append(field_tr.coordinates)
        if field_tl:
            if field_tl.has_figure():
                fields.append(field_tl.coordinates)
            beatable_fields.append(field_tl.coordinates)
        if field_top:
            if not field_top.has_figure():
                fields.append(field_top.coordinates)
        if self.first_move:
            if field_top2:
                if not field_top2.has_figure():
                    fields.append(field_top2.coordinates)

        self.moveable_fields = fields
        self.beatable_fields = beatable_fields

class King(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

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
                    if isinstance(figure, Pawn):
                        if field.coordinates in figure.beatable_fields:
                            append = False
                    else:
                        if field.coordinates in figure.moveable_fields:
                            append = False

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
                    return True
        return False

    def is_checkmate(self):
        return True if self.moveable_fields == [] else False

class Rook(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, id, player, board)

    def set_moveable_fields(self):
        fields = []

        y_couter = 1
        x_couter = 1

        for i in range(8):
            field = self.board.get_field_by_coords([self.coordinates[0] + y_couter, self.coordinates[1]])
            if field:
                if field.has_figure():
                    if field.figure.player != self.player:
                        fields.append(field.coordinates)
                        break
                else:
                    fields.append(field.coordinates)
                    y_couter += 1

        self.moveable_fields = fields

class Button():
    def __init__(self, color, x, y, width, height, text=None, text_size=None):
        self.color = color
        self.default_color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_size = text_size

    def draw(self, outline=None, transparent=False):
        if outline:
            pygame.draw.rect(screen, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        if transparent:
                rect = pygame.Surface((self.width, self.height))
                rect.set_alpha(128)
                rect.fill(self.color)
                screen.blit(rect, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)

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

width, height = 800, 800

screen = pygame.display.set_mode([width, height])

pygame.font.init()

font = pygame.font.SysFont("Comic Sans MS", 20)

pygame.display.set_caption("Chess")

clock = pygame.time.Clock()


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
