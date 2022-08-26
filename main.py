from random import randrange
import pygame
import os
import time

pygame.font.init()

WIDTH, HEIGHT = 700, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MineSweeper")

font = pygame.font.SysFont(None, 96)
font_small = pygame.font.SysFont(None, 48)

FPS = 60

NUMBER_COLORS = {
    1 : "blue",
    2 : "green",
    3 : "red",
    4 : "purple",
    5 : "maroon",
    6 : "turquoise",
    7 : "black",
    8 : "darkgray"
}

class Field():
    def __init__(self, rows, cols, number_of_mines, border_size):
        self.rows = rows
        self.cols = cols
        self.number_of_mines = number_of_mines
        self.square_size = WIDTH/rows
        self.border_size = border_size
        self.bomb_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bomb.png")), (self.square_size-(self.border_size*2), self.square_size-(self.border_size*2)))
        self.flag_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "flag.png")), (self.square_size-(self.border_size*2), self.square_size-(self.border_size*2)))
        self.mine_field = [[0 for x in range(self.rows)] for y in range(self.cols)] 
        self.mine_positions = []
        self.covered_fields = [[True for x in range(self.rows)] for y in range(self.cols)]
        self.font = pygame.font.SysFont(None, int(self.square_size))
        self.flags = 0

    def generate_field(self, clicked_x, clicked_y):
        self.flags = 0
        self.covered_fields = [[True for x in range(self.rows)] for y in range(self.cols)]
        field = [[0 for x in range(self.rows)] for y in range(self.cols)] 
        self.mine_field = field
        locations_of_mines = []
        while len(locations_of_mines) < self.number_of_mines:
            x = randrange(0, self.rows)
            y = randrange(0, self.cols)
            if not ((x, y) in locations_of_mines):
                if ((clicked_x,clicked_y) in self.get_neighbours(x, y)) or (clicked_x == x and clicked_y == y):
                    continue

                locations_of_mines.append((x, y))
                field[y][x] = -1
                for neighbour in self.get_neighbours(x, y):
                    if field[neighbour[1]][neighbour[0]] != -1:
                        field[neighbour[1]][neighbour[0]] += 1
        
        self.mine_positions = locations_of_mines
        return field

    def get_neighbours(self, row, col):
        neighbours = []
        if row > 0:  # left
            neighbours.append((row - 1, col))

        if row < self.rows - 1:  # right
            neighbours.append((row + 1, col))

        if col > 0:  # up
            neighbours.append((row, col - 1))

        if col < self.cols - 1:  # down
            neighbours.append((row, col + 1))
        
        if col > 0 and row > 0: # up left
            neighbours.append((row - 1, col - 1))

        if col > 0 and row < self.rows - 1: # up right
            neighbours.append((row + 1, col - 1))

        if col < self.cols - 1 and row > 0: # down left
            neighbours.append((row - 1, col + 1))
        
        if col < self.cols - 1 and row < self.rows - 1: # down right
            neighbours.append((row + 1, col + 1))
        
        return neighbours

    def draw(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = row * self.square_size
                y = col * self.square_size
                pygame.draw.rect(WIN, "black", (x, y, self.square_size, self.square_size))

                if self.covered_fields[col][row] == False:
                    if(self.mine_field[col][row] > 0): 
                        pygame.draw.rect(WIN, "lightgray", (x + self.border_size, y + self.border_size, self.square_size - 2*self.border_size, self.square_size - 2*self.border_size))
                        text = self.font.render(f"{self.mine_field[col][row]}", 1, NUMBER_COLORS[self.mine_field[col][row]])
                        WIN.blit(text, (x + (self.square_size/2) - (text.get_width()/2), y + (self.square_size/2) - (text.get_height()/2)))
                    elif self.mine_field[col][row] == 0:
                        pygame.draw.rect(WIN, "lightgray", (x + self.border_size, y + self.border_size, self.square_size - 2*self.border_size, self.square_size - 2*self.border_size))
                    else:
                        pygame.draw.rect(WIN, "lightgray", (x + self.border_size, y + self.border_size, self.square_size - 2*self.border_size, self.square_size - 2*self.border_size))
                        WIN.blit(self.bomb_image, (x + self.border_size, y + self.border_size))
                else:
                    if self.mine_field[col][row] == -2:
                        pygame.draw.rect(WIN, (140,140,140), (x + self.border_size, y + self.border_size, self.square_size - 2*self.border_size, self.square_size - 2*self.border_size))
                        WIN.blit(self.flag_image, (x + self.border_size, y + self.border_size))
                    else:
                        pygame.draw.rect(WIN, (140,140,140), (x + self.border_size, y + self.border_size, self.square_size - 2*self.border_size, self.square_size - 2*self.border_size))
    
    def uncover(self, row, col):
        if self.mine_field[col][row] == -2:
            return
        
        if self.mine_field[col][row] == 0:
            self.reveal_multiple(row, col)
        else:
            self.covered_fields[col][row] = False
    
    def flag(self, row, col):
        if self.covered_fields[col][row] == False:
            return

        if not (self.mine_field[col][row] == -2):
            if self.flags >= self.number_of_mines:
                return
            self.flags += 1
            self.mine_field[col][row] = -2
        else:
            self.flags -= 1
            if (row, col) in self.mine_positions:
                self.mine_field[col][row] = -1
            else:
                self.mine_field[col][row] = self.calculate_cell_number(row, col)

    def calculate_cell_number(self, row, col):
        number = 0
        for neighbour in self.get_neighbours(row, col):
            if neighbour in self.mine_positions:
                number += 1
        return number

    def reveal_multiple(self, row, col):
        if(self.covered_fields[col][row] == True):
            self.covered_fields[col][row] = False
            for neighbour in self.get_neighbours(row, col):
                if (self.mine_field[neighbour[1]][neighbour[0]] > 0):
                    self.covered_fields[neighbour[1]][neighbour[0]] = False

                elif(self.mine_field[neighbour[1]][neighbour[0]] == 0):
                    self.reveal_multiple(neighbour[0], neighbour[1])

    def get_cell_from_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        if (mx > 700 or mx < 0) or (my > 700 or my < 0):
            return (-1, -1)
        
        row = int(mx // self.square_size)
        col = int(my // self.square_size)
        return (row, col)
    
    def check_for_win(self):

        uncovered_mine = False
        for mine_pos in self.mine_positions:
            if self.mine_field[mine_pos[1]][mine_pos[0]] != -2:
                uncovered_mine = True

        if uncovered_mine == False:
            for x in range(self.rows):
                for y in range(self.cols):
                    if self.mine_field[y][x] >= 0:
                        self.uncover(x,y)
            return True

        covered_number = False
        for x in range(self.rows):
            for y in range(self.cols):
                if (self.covered_fields[y][x] == True) and (self.mine_field[y][x] != -1):
                    covered_number = True

        if covered_number == False:
            return True
        
        return False

def draw(game_started, field, game_over, start_time, end_time):
    WIN.fill("white")
    field.draw()
    if game_over == -1:
        text = font.render("Game Over", 1, "red")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))

        time_text = font_small.render(f"Time: {round(end_time - start_time)}", 1, "black")
        WIN.blit(time_text, ((30 , ((HEIGHT-700)/2 + 700) - time_text.get_height()/2)))

        flags_text = font_small.render(f"Flags: {field.number_of_mines - field.flags}", 1, "black")
        WIN.blit(flags_text, ((WIDTH - 50 - flags_text.get_width(), ((HEIGHT-700)/2 + 700) - flags_text.get_height()/2)))
    if game_over == 1:
        text = font.render("WIN", 1, "green")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))

        time_text = font_small.render(f"Time: {round(end_time - start_time)}", 1, "black")
        WIN.blit(time_text, ((30 , ((HEIGHT-700)/2 + 700) - time_text.get_height()/2)))

        flags_text = font_small.render(f"Flags: {field.number_of_mines - field.flags}", 1, "black")
        WIN.blit(flags_text, ((WIDTH - 50 - flags_text.get_width(), ((HEIGHT-700)/2 + 700) - flags_text.get_height()/2)))
    if game_over == 0 and game_started:
        time_text = font_small.render(f"Time: {round(end_time - start_time)}", 1, "black")
        WIN.blit(time_text, ((30 , ((HEIGHT-700)/2 + 700) - time_text.get_height()/2)))

        flags_text = font_small.render(f"Flags: {field.number_of_mines - field.flags}", 1, "black")
        WIN.blit(flags_text, ((WIDTH - 50 - flags_text.get_width(), ((HEIGHT-700)/2 + 700) - flags_text.get_height()/2)))
    pygame.display.update()

    
def main():
    game_started = False
    run = True
    field = Field(20, 20, 75, 2)
    game_over = 0

    start_time = 0
    end_time = 0
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if game_over == 0:
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if(game_started):
                            mouse_pos = field.get_cell_from_mouse_pos()
                            if(mouse_pos == (-1, -1)):
                                continue
                            else:
                                if(field.mine_field[mouse_pos[1]][mouse_pos[0]] == -1):
                                    game_started = False
                                    game_over = -1
                                
                                if(field.covered_fields[mouse_pos[1]][mouse_pos[0]]):
                                    field.uncover(*mouse_pos)
                                else:
                                    flags_nearby = 0
                                    for neighbour in field.get_neighbours(mouse_pos[0], mouse_pos[1]):
                                        if field.mine_field[neighbour[1]][neighbour[0]] == -2:
                                            flags_nearby += 1
                                    if flags_nearby == field.mine_field[mouse_pos[1]][mouse_pos[0]]:
                                        for neighbour in field.get_neighbours(mouse_pos[0], mouse_pos[1]):
                                            if field.covered_fields[neighbour[1]][neighbour[0]]:
                                                if(field.mine_field[neighbour[1]][neighbour[0]] == -1):
                                                    game_started = False
                                                    game_over = -1

                                                if(field.covered_fields[neighbour[1]][neighbour[0]]):
                                                    field.uncover(*neighbour)

                        else:
                            game_started = True
                            start_time = time.time()
                            mouse_pos = field.get_cell_from_mouse_pos()
                            field.mine_field = field.generate_field(*mouse_pos)
                            if(mouse_pos == (-1, -1)):
                                continue
                            else:
                                field.uncover(*mouse_pos)

                    if event.button == 3:
                        if(game_started):
                            mouse_pos = field.get_cell_from_mouse_pos()
                            if(mouse_pos == (-1, -1)):
                                continue
                            else:
                                field.flag(*mouse_pos)
                    if field.check_for_win():
                        game_started = False
                        game_over = 1
                end_time = time.time()
            else:
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        game_over = 0
                        field.generate_field(-1, -1)

        draw(game_started, field, game_over, start_time, end_time)
    pygame.quit()


if __name__ == "__main__":
    main()
