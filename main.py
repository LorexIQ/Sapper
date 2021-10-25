import random
import pygame
import time

run = True
size_block = 30


class GameField(object):
    def __init__(self, mode_selected):
        mode = {'Easy': (10, 15),
                'Normal': (20, 40),
                'Hard': (30, 99)}
        self.settings = mode.get(mode_selected)
        self.matrix = []
        self.matrix_lake = []
        self.id_lakes = []
        self.create_matrix()

    def fill_mines(self):
        self.matrix = [[0 for _ in range(self.settings[0])] for _ in range(self.settings[0])]
        mines = 0
        random.seed()
        while mines != self.settings[1]:
            number = random.randrange(1, self.settings[0] * self.settings[0], 1) - 1
            if 7 != self.matrix[number // self.settings[0]][number % self.settings[0]]:
                mines += 1
                self.matrix[number // self.settings[0]][number % self.settings[0]] = 7

    def indexing_matrix(self):
        for row in range(self.settings[0]):
            for column in range(self.settings[0]):
                mines = 0
                for row_range in range((row - 1) if row > 0 else row,
                                       (row + 2) if row < self.settings[0] - 1 else row + 1):
                    for column_range in range((column - 1) if column > 0 else column,
                                              (column + 2) if column < self.settings[0] - 1 else column + 1):
                        if self.matrix[row_range][column_range] == 7:
                            mines += 1
                if self.matrix[row][column] != 7:
                    self.matrix[row][column] = mines

    def search_lakes(self):
        buffer = []
        for row in range(self.settings[0]):
            for column in range(self.settings[0]):
                zero_coords = []
                if self.matrix[row][column] == 0 and (row, column) not in buffer:
                    for row_range in range((row - 1) if row > 0 else row,
                                           (row + 2) if row < self.settings[0] - 1 else row + 1):
                        for column_range in range((column - 1) if column > 0 else column,
                                                  (column + 2) if column < self.settings[0] - 1 else column + 1):
                            if self.matrix[row_range][column_range] == 0:
                                if (row_range, column_range) not in zero_coords:
                                    zero_coords.append((row_range, column_range))
                    for coords in zero_coords:
                        for row_o in range((coords[0] - 1) if coords[0] > 0 else coords[0],
                                           (coords[0] + 2) if coords[0] < self.settings[0] - 1 else coords[0] + 1):
                            for column_o in range((coords[1] - 1) if coords[1] > 0 else coords[1],
                                                  (coords[1] + 2) if coords[1] < self.settings[0] - 1 else coords[
                                                                                                               1] + 1):
                                if (row_o, column_o) not in zero_coords and (row_o, column_o) != coords \
                                        and self.matrix[row_o][column_o] == 0:
                                    zero_coords.append((row_o, column_o))
                    if zero_coords:
                        buffer += zero_coords
                        self.matrix_lake.append(zero_coords)
        return buffer

    def search_coast(self):
        for lake in self.matrix_lake:
            buffer = []
            for coord in lake:
                for row_lake in range((coord[0] - 1) if coord[0] > 0 else coord[0],
                                      (coord[0] + 2) if coord[0] < self.settings[0] - 1 else coord[0] + 1):
                    for column_lake in range((coord[1] - 1) if coord[1] > 0 else coord[1],
                                             (coord[1] + 2) if coord[1] < self.settings[0] - 1 else coord[1] + 1):
                        if (row_lake, column_lake) not in buffer and (row_lake, column_lake) not in lake:
                            buffer.append((row_lake, column_lake))
            lake += buffer
            self.id_lakes.append([element[0] * self.settings[0] + element[1] + 1 for element in lake])

    def create_matrix(self):
        self.fill_mines()
        self.indexing_matrix()
        self.search_lakes()
        self.search_coast()


class OneCell(pygame.sprite.Sprite):
    def __init__(self, coord, info, surface, cells, id_cell):
        pygame.sprite.Sprite.__init__(self)
        self.id = id_cell
        self.surface = surface
        self.coord = coord
        self.background = pygame.image.load('Images/background_cell_open.png')
        self.cells = cells
        self.status = 0
        self.info = info

    def draw(self):
        if self.status == 1:
            if self.info == 0:
                self.surface.blit(self.cells[0][0], (self.coord.x, self.coord.y))
            else:
                self.surface.blit(self.cells[1][self.info - 1], (self.coord.x, self.coord.y))
        else:
            self.surface.blit(self.background, (self.coord.x - 2, self.coord.y - 2))
            if self.status == 0:
                self.surface.blit(self.cells[0][1], (self.coord.x, self.coord.y))
            elif self.status == 2:
                self.surface.blit(self.cells[0][2], (self.coord.x, self.coord.y))
            elif self.status == 3:
                self.surface.blit(self.cells[0][3], (self.coord.x, self.coord.y))

    def active(self, event_cell):
        pos = pygame.mouse.get_pos()
        if self.coord.collidepoint((pos[0], pos[1] - 95)):
            if event_cell.type == pygame.MOUSEBUTTONDOWN:
                if self.status != 1:
                    if event_cell.button == 1:
                        if self.status in [2, 3]:
                            self.status = 0
                        else:
                            self.status = 1
                            if self.info == 0:
                                return self.id
                            elif self.info == 7:
                                return -1
                    elif event_cell.button == 3:
                        if self.status == 0:
                            self.status = 2
                        elif self.status == 2:
                            self.status = 3
                        elif self.status == 3:
                            self.status = 0


class GamingGrid(pygame.sprite.Sprite):
    def __init__(self, global_info, win_place):
        pygame.sprite.Sprite.__init__(self)
        self.win = win_place
        self.global_info = global_info
        self.id_mass = global_info.id_lakes
        self.play = True
        self.rects_cells = [pygame.Rect(x * size_block + 5 * (x + 1),
                                        y * size_block + 5 * (y + 1),
                                        size_block, size_block)
                            for x in range(global_info.settings[0]) for y in range(global_info.settings[0])]
        self.game_win = pygame.Surface((size_block * global_info.settings[0] + 5 * global_info.settings[0] + 5,
                                        size_block * global_info.settings[0] + 5 * global_info.settings[0] + 5))
        cells = [[pygame.image.load('Images/cell_open.png'),
                  pygame.image.load('Images/cell_close.png'),
                  pygame.image.load('Images/cell_flag.png'),
                  pygame.image.load('Images/cell_question.png')],
                 [pygame.image.load('Images/cell_one_mine.png'),
                  pygame.image.load('Images/cell_two_mines.png'),
                  pygame.image.load('Images/cell_three_mines.png'),
                  pygame.image.load('Images/cell_four_mines.png'),
                  pygame.image.load('Images/cell_five_mines.png'),
                  pygame.image.load('Images/cell_six_mines.png'),
                  pygame.image.load('Images/cell_mine.png')]]
        self.group = []
        id_cell = 0
        for rect in self.rects_cells:
            id_cell += 1
            self.group.append(OneCell(rect,
                                      global_info.matrix[self.rects_cells.index(rect) // global_info.settings[0]]
                                      [self.rects_cells.index(rect) % global_info.settings[0]],
                                      self.game_win, cells, id_cell))
        self.info_board = InfoBoard(win)

    def draw(self, win_blit):
        if self.play:
            self.info_board.update_time()
        self.info_board.time_board()
        self.game_win.fill(pygame.Color('white'))
        for cell in self.group:
            cell.draw()
        win_blit.blit(self.game_win, (0, 95))

    def lose(self):
        self.play = False
        for element in self.group:
            if element.info == 7:
                element.status = 1

    def check_win(self):
        count = 0
        for element in self.group:
            if element.status == 2 and element.info == 7:
                count += 1
        if self.global_info.settings[1] == count:
            for element in self.group:
                if element.info != 7:
                    element.status = 1
            self.play = False

    def active(self, event_cell):
        if self.play:
            for element in self.group:
                id_lake_active = element.active(event_cell)
                if id_lake_active is not None and id_lake_active != -1:
                    for lake in self.id_mass:
                        if id_lake_active in lake:
                            for water in lake:
                                self.group[water - 1].status = 1
                elif id_lake_active == -1:
                    self.lose()
            self.check_win()


class InfoBoard(object):
    def __init__(self, win_board):
        self.win = win_board
        self.start_game = 0
        self.end_game = 0
        self.font = pygame.font.Font('Font/Font.ttf', 60)
        self.image_background = pygame.image.load('Images/background_timer.png')
        self.start()

    def start(self):
        self.start_game = time.time()

    def update_time(self):
        self.end_game = time.time()

    def time_board(self):
        time_now = (self.end_game - self.start_game)
        if time_now >= 5999:
            label = self.font.render('99:59',
                                     True, pygame.Color('gray'))
            print(label.get_width(), label.get_height())
        else:
            label = self.font.render('{0}:{1}'.format(int(time_now // 60),
                                                      int(time_now % 60)),
                                     True, (180, 180, 180))
        self.win.blit(self.image_background, (self.win.get_width() / 2 - self.image_background.get_width() / 2, 10))
        self.win.blit(label, (self.win.get_width() / 2 - label.get_width() / 2, 20))


def menu():
    while True:
        print('1. Easy\n2. Normal\n3. Hard\n')
        mode = int(input('Mode: '))
        if mode in [1, 2, 3]:
            break
    if mode == 1:
        return 'Easy'
    elif mode == 2:
        return 'Normal'
    elif mode == 3:
        return 'Hard'


mode_game = menu()
pygame.init()
field = GameField(mode_game)
width = size_block * field.settings[0] + 5 * field.settings[0] + 5
height = size_block * field.settings[0] + 5 * field.settings[0] + 100
win = pygame.display.set_mode((width, height))
game_cells = GamingGrid(field, win)

while run:
    win.fill(pygame.Color('white'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        game_cells.active(event)

    game_cells.draw(win)
    pygame.display.flip()

pygame.quit()
