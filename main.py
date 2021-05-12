import pygame
import os
from personallib.camera import Camera
from board import Board
from spritesheet import Spritesheet

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 120
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

BOARD_SIZE = min(WIN_WIDTH, WIN_HEIGHT) * (3/4)
SCALE = BOARD_SIZE // 9
SIZE = (int(SCALE * 6), int(SCALE * 2))
BOARD_COLOURS = [(215, 161, 113), (138, 80, 31)]
STARTING_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq a3 0 1"

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Multiplayer Chess")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()

# Objects
cam = Camera(win, 0, 0, 1)
boardSurface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
boardSurface.fill((255, 255, 255))
for x in range(8):
    for y in range(8):
        if (x + y) % 2 == 0:
            pygame.draw.rect(boardSurface, BOARD_COLOURS[0], (x * (BOARD_SIZE / 8), y * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        else:
            pygame.draw.rect(boardSurface, BOARD_COLOURS[1], (x * (BOARD_SIZE / 8), y * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
board = Board(STARTING_POSITION)
board.generate_fen()
sprites = Spritesheet(pygame.transform.scale(pygame.image.load(os.path.join("imgs","spritesheet.png")).convert_alpha(), SIZE), 6, 2)
heldPiece = (-1, "")

# Variables
running = True

# Main Loop
if __name__ == '__main__':
    while running:

        clock.tick(FRAMERATE)

        pieces = board.get_pieces()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    m = cam.get_world_coord(pygame.mouse.get_pos())
                    if m[0] > -BOARD_SIZE / 2 and m[0] < BOARD_SIZE / 2 and m[1] > -BOARD_SIZE / 2 and m[1] < BOARD_SIZE / 2:
                        m = ((m[0] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8), (m[1] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8))
                        i = int((m[1] * 8) + m[0])
                        piece = pieces[i]
                        if piece != 0 and ((board.get_turn() and piece.isupper()) or not (board.get_turn() or piece.isupper())):
                            heldPiece = (i, piece)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and heldPiece[0] != -1:
                    m = cam.get_world_coord(pygame.mouse.get_pos())
                    if m[0] > -BOARD_SIZE / 2 and m[0] < BOARD_SIZE / 2 and m[1] > -BOARD_SIZE / 2 and m[1] < BOARD_SIZE / 2:
                        m = ((m[0] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8), (m[1] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8))
                        i = int((m[1] * 8) + m[0])
                        if i != heldPiece[0]:
                            board.make_move(heldPiece, i)
                    heldPiece = (-1, "")
                    
        win.fill((255, 255, 255))
        cam.blit(boardSurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))
        for i in range(len(pieces)):
            if pieces[i] != 0 and i != heldPiece[0]:
                cam.blit(sprites.get_piece(pieces[i]), ((i % 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2), 
                                                                (i // 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2)))
        if heldPiece[0] != -1:
            m = cam.get_world_coord(pygame.mouse.get_pos())
            cam.blit(sprites.get_piece(heldPiece[1]), (m[0] - (SCALE / 2), m[1] - (SCALE / 2)))

        pygame.display.update()