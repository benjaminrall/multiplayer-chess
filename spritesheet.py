import pygame

class Spritesheet:
    def __init__(self, spritesheet, cols, rows):
        self.spritesheet = spritesheet
        self.cols = cols
        self.rows = rows
        self.totalCells = cols * rows

        self.rect = self.spritesheet.get_rect()
        self.cellWidth = self.rect.width / cols
        self.cellHeight = self.rect.height / rows

        self.cells = [ ((index % cols) * self.cellWidth, (index // cols) * self.cellHeight ) for index in range(self.totalCells) ]
        self.sprites = [ pygame.Surface((self.cellWidth, self.cellHeight), pygame.SRCALPHA) for i in range(self.totalCells) ] 
        for i in range(len(self.sprites)):
            self.sprites[i].blit(self.spritesheet, (0, 0), self.get_area(i))

        self.pieces =  {"K": self.sprites[0], "Q": self.sprites[1], "B": self.sprites[2], "N": self.sprites[3], "R": self.sprites[4], "P": self.sprites[5],
                        "k": self.sprites[6], "q": self.sprites[7], "b": self.sprites[8], "n": self.sprites[9], "r": self.sprites[10], "p": self.sprites[11]}

    def get_area(self, i):
        return (self.cells[i][0], self.cells[i][1], self.cellWidth, self.cellHeight)

    def get_img(self, i):
        return self.sprites[i]

    def get_piece(self, p):
        return self.pieces[p]