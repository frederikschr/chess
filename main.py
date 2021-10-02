import pygame
import sys
from network import Network

class Game():

    def __init__(self):
        self.FPS = 60
        self.over = False

        self.n = Network()

        self.player_id = int(self.n.get_id())

        self.player = Player(self.player_id)

        self.board = Board(self.player)


    def handle_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


    def run(self):


        self.board.create()


        while True:

            turn = int(self.n.send("get-turn"))



            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()





                    for field in self.board.fields:
                        if field.is_clicked(pos[0], pos[1]):  #Check if field is clicked




                            if self.player.has_selected:




                                if field != self.player.selected_field:

                                    if self.player.id == turn:

                                        self.player.selected_field.figure.set_moveable_fields()

                                        if field.coordinates in self.player.selected_field.figure.moveable_fields:

                                            field.figure = self.player.selected_field.figure

                                            field.update_figure()

                                            self.n.send("change-turn")


                                            self.player.selected_field.figure = None
                                            self.player.selected_field.is_highlighted = False
                                            self.player.has_selected = False

                                else:
                                    field.is_highlighted = False
                                    self.player.has_selected = False




                            else:
                                if field.has_figure():
                                    if field.figure.player == self.player.id:
                                        self.player.selected_field = field
                                        self.player.has_selected = True
                                        field.is_highlighted = True



            self.board.draw()


            self.handle_quit()

            clock.tick(self.FPS)
            pygame.display.update()

class Field():
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, size, figure):
        self.coordinates = [game_coord_y, game_coord_x]
        self.win_pos_y = win_pos_y
        self.win_pos_x = win_pos_x
        self.size = size

        self.is_highlighted = False

        self.figure = figure

    def is_clicked(self, mouse_x, mouse_y):
        if mouse_x > self.win_pos_x and mouse_x < self.win_pos_x + self.size:
            if mouse_y > self.win_pos_y and mouse_y < self.win_pos_y + self.size:
                return True
        return False

    def update_figure(self):
        self.figure.win_pos_x = self.win_pos_x
        self.figure.win_pos_y = self.win_pos_y
        self.figure.coordinates[0] = self.coordinates[0]
        self.figure.coordinates[1] = self.coordinates[1]

    def has_figure(self):
        return True if self.figure else False

    def draw_figure(self):
        self.figure.draw()

    def get_figure(self):
        return self.figure

class Board():
    def __init__(self, player):
        self.fields = []
        self.field_size = height / 8
        self.player = player

    def create(self):
        win_pos_y = 0
        win_pos_x = 0

        for y in range(8):

            if y < 2:
                owner = 2
            else:
                owner = 1


            for x in range(8):

                if y == 1 or y == 6:

                    figure = Pawn(y + 1, x + 1, win_pos_y, win_pos_x, owner)

                else:
                    figure = None

                self.fields.append(Field(y + 1, x + 1, win_pos_y, win_pos_x, self.field_size, figure))

                if figure:
                    if figure.player == self.player.id:
                        self.player.figures.append(figure)

                win_pos_x += self.field_size

            win_pos_x = 0
            win_pos_y += self.field_size

    def draw(self):
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

            if field.is_highlighted:
                pygame.draw.rect(screen, (255, 0, 0), (field.win_pos_x, field.win_pos_y, self.field_size, self.field_size))

            else:
                pygame.draw.rect(screen, color, (field.win_pos_x, field.win_pos_y, self.field_size, self.field_size))

            if field.has_figure():
                field.draw_figure()

class Player():
    def __init__(self, id):

        self.id = id

        self.figures = []
        self.has_won = False
        self.has_turn = False

        self.selected_field = None

        self.has_selected = False



class Figure():
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, player):
        self.coordinates = [game_coord_y, game_coord_x]
        self.win_pos_y = win_pos_y
        self.win_pos_x = win_pos_x

        self.player = player

        self.moveable_fields = []

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.win_pos_x, self.win_pos_y, 50, 50))
        textsurface = font.render(self.__class__.__name__, None, (255, 255, 255))
        screen.blit(textsurface, (self.win_pos_x, self.win_pos_y))


    def can_go_to(self, coords):
        pass

    def set_moveable_fields(self):
        pass

class Pawn(Figure):
    def __init__(self, game_coord_y, game_coord_x, win_pos_y, win_pos_x, player):
        super().__init__(game_coord_y, game_coord_x, win_pos_y, win_pos_x, player)

    def set_moveable_fields(self):
        fields = []

        if self.player == 1:
            fields.append([self.coordinates[0] - 1, self.coordinates[1]])
        else:
            fields.append([self.coordinates[0] + 1, self.coordinates[1]])

        self.moveable_fields = fields


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
