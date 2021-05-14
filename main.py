from pygame import draw
from network import Network
import pygame
import os
import random
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
STARTING_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Multiplayer Chess")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()
pygame.mixer.init() 

# Objects
cam = Camera(win, 0, 0, 1)
boardSurface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
boardSurface.fill((255, 255, 255))
overlaySurface = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
overlaySurface.fill((255, 255, 255, 0))
for x in range(8):
    for y in range(8):
        if (x + y) % 2 == 0:
            pygame.draw.rect(boardSurface, BOARD_COLOURS[0], (x * (BOARD_SIZE / 8), y * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        else:
            pygame.draw.rect(boardSurface, BOARD_COLOURS[1], (x * (BOARD_SIZE / 8), y * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
board = Board(STARTING_POSITION)
sprites = Spritesheet(pygame.transform.scale(pygame.image.load(os.path.join("imgs","spritesheet.png")).convert_alpha(), SIZE), 6, 2)

ip = "86.135.152.108"
n = Network(ip)
playerID = int(n.getP())
if playerID < 0:
    print("Server Full")
else:
    print(f"Successfully Connected with ID {playerID}")


# Subroutines
def combine(L):
    s = ""
    for i in L:
        s += i + " "
    return s

def draw_pieces(p, pieces, heldPiece, validSquares):
    if p == 1:
        for i in range(len(pieces)):
            if pieces[i] != 0 and i != heldPiece[0]:
                cam.blit(sprites.get_piece(pieces[i]), ((i % 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2), 
                                                                (i // 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2)))
        overlaySurface.fill((0, 0, 0, 0))
        for i in validSquares:
            pygame.draw.rect(overlaySurface,  (255, 60, 0, 100), ((i % 8) * (BOARD_SIZE / 8), (i // 8) * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        cam.blit(overlaySurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

        if heldPiece[0] != -1:
            m = cam.get_world_coord(pygame.mouse.get_pos())
            cam.blit(sprites.get_piece(heldPiece[1]), (m[0] - (SCALE / 2), m[1] - (SCALE / 2)))
    else:
        for i in range(len(pieces)):
            if pieces[i] != 0 and i != heldPiece[0]:
                cam.blit(sprites.get_piece(pieces[i]), ((i % 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2), 
                                                                (7 - (i // 8)) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2)))

        overlaySurface.fill((0, 0, 0, 0))
        for i in validSquares:
            pygame.draw.rect(overlaySurface,  (255, 60, 0, 100), ((i % 8) * (BOARD_SIZE / 8), (7 - (i // 8)) * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        cam.blit(overlaySurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

        if heldPiece[0] != -1:
            m = cam.get_world_coord(pygame.mouse.get_pos())
            cam.blit(sprites.get_piece(heldPiece[1]), (m[0] - (SCALE / 2), m[1] - (SCALE / 2)))

def find_index(p, m):
    if p == 1:
        i = int((m[1] * 8) + m[0])
    else:
        i = int(((7 - m[1]) * 8) + m[0])
    return i

# Variables
running = True
randomise = False 
positionsSeen = {combine(STARTING_POSITION.split(" ")[0:-2]): 1}
repetitionLoss = False
heldPiece = (-1, "")
validSquares = []
currentFen = STARTING_POSITION
ticks = 0
dropSound = pygame.mixer.Sound(os.path.join("audio", "dropPiece.wav"))

# Main Loop
if __name__ == '__main__':
    while running:

        clock.tick({False: FRAMERATE, True: FRAMERATE}[randomise])

        pieces = board.get_pieces()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and board.get_turn() == playerID:
                if event.button == 1:
                    m = cam.get_world_coord(pygame.mouse.get_pos())
                    if m[0] > -BOARD_SIZE / 2 and m[0] < BOARD_SIZE / 2 and m[1] > -BOARD_SIZE / 2 and m[1] < BOARD_SIZE / 2:
                        m = ((m[0] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8), (m[1] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8))
                        i = find_index(playerID, m)
                        piece = pieces[i]
                        if piece != 0 and ((board.get_turn() and piece.isupper()) or not (board.get_turn() or piece.isupper())):
                            heldPiece = (i, piece)
                            validSquares = board.get_valid_moves(heldPiece)
            elif event.type == pygame.MOUSEBUTTONUP and board.get_turn() == playerID:
                if event.button == 1 and heldPiece[0] != -1:
                    m = cam.get_world_coord(pygame.mouse.get_pos())
                    if m[0] > -BOARD_SIZE / 2 and m[0] < BOARD_SIZE / 2 and m[1] > -BOARD_SIZE / 2 and m[1] < BOARD_SIZE / 2:
                        m = ((m[0] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8), (m[1] + (BOARD_SIZE / 2)) // (BOARD_SIZE // 8))
                        i = find_index(playerID, m)
                        if i != heldPiece[0] and i in validSquares:
                            board.make_move(heldPiece, i)
                            newFen = board.generate_fen()
                            newFenKey = combine(newFen.split(" ")[0:-2])
                            if newFenKey in positionsSeen:
                                positionsSeen[newFenKey] += 1
                            else:
                                positionsSeen[newFenKey] = 1
                            pygame.mixer.Sound.play(dropSound)
                            n.send(f"play~{newFen}")
                    heldPiece = (-1, "")
                    validSquares = []

        if randomise:     
            randomPieces = []
            for i in range(len(pieces)):
                piece = pieces[i]
                if piece != 0 and ((board.get_turn() and piece.isupper()) or not (board.get_turn() or piece.isupper())):
                    randomPieces.append(i)
            while True and board.check_gameover() == -1 and not repetitionLoss:
                random.shuffle(randomPieces)
                i = randomPieces[0]
                piece = pieces[i]
                usedPiece = (i, piece)
                validSquares = board.get_valid_moves(usedPiece)
                random.shuffle(validSquares)
                if len(validSquares) > 0:
                    square = validSquares[0]
                    board.make_move(usedPiece, square)
                    new_fen = combine(board.generate_fen().split(" ")[0:-2])
                    if new_fen in positionsSeen:
                        positionsSeen[new_fen] += 1
                    else:
                        positionsSeen[new_fen] = 1
                    for key in positionsSeen:
                        if positionsSeen[key] >= 5:
                            repetitionLoss = True
                    validSquares = []
                    break

        win.fill((255, 255, 255))
        cam.blit(boardSurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

        draw_pieces(playerID, pieces, heldPiece, validSquares)

        pygame.display.update()

        for key in positionsSeen:
            if positionsSeen[key] >= 5:
                repetitionLoss = True

        if board.check_gameover() >= 0:
            print("GAME OVER ", {0: "Black Stalemated", 1: "Black checkmated", 2: "White checkmated", 3: "50 Moves draw", 4: "White stalemated"}[board.check_gameover()])
            input()
            board = Board(STARTING_POSITION)

        if repetitionLoss:
            print("GAME OVER BY REPETITION")
            break

        if board.get_turn() != playerID and ticks > 60:
            gotFen = n.send("get")
            if gotFen != currentFen and gotFen != "empty":
                board = Board(gotFen)
                currentFen = gotFen
                pygame.mixer.Sound.play(dropSound)
            ticks = 0

        ticks += 1
