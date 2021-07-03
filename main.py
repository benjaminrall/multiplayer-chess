from pygame import draw
from network import Network
import pygame
import os
from personallib.camera import Camera
from board import Board
from spritesheet import Spritesheet

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 60
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
pygame.font.init()

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

ip = input("Enter the IP of the server: ")
n = Network(ip)
playerID = int(n.getP())
if playerID < 0:
    print("Server Full")
    exit()    
else:
    print(f"Successfully Connected with ID {playerID}")


# Subroutines
def combine(L):
    s = ""
    for i in L:
        s += i + " "
    return s

def draw_pieces(p, pieces, heldPiece, validSquares, otherHeldPiece):
    if p == 1:
        for i in range(len(pieces)):
            if pieces[i] != 0 and i != heldPiece[0] and i != otherHeldPiece[0]:
                cam.blit(sprites.get_piece(pieces[i]), ((i % 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2), 
                                                                (i // 8) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2)))
        overlaySurface.fill((0, 0, 0, 0))
        for i in validSquares:
            pygame.draw.rect(overlaySurface,  (255, 60, 0, 100), ((i % 8) * (BOARD_SIZE / 8), (i // 8) * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        cam.blit(overlaySurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

        if heldPiece[0] != -1:
            m = cam.get_world_coord(pygame.mouse.get_pos())
            n.send(f"pos~{heldPiece[0]} {heldPiece[1]} {m[0]} {m[1]}")
            cam.blit(sprites.get_piece(heldPiece[1]), (m[0] - (SCALE / 2), m[1] - (SCALE / 2)))
    else:
        for i in range(len(pieces)):
            if pieces[i] != 0 and i != heldPiece[0] and i != otherHeldPiece[0]:
                cam.blit(sprites.get_piece(pieces[i]), ((7 - (i % 8)) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2), 
                                                                (7 - (i // 8)) * (BOARD_SIZE / 8) - (BOARD_SIZE / 2) + (((BOARD_SIZE / 8) - SCALE) / 2)))

        overlaySurface.fill((0, 0, 0, 0))
        for i in validSquares:
            pygame.draw.rect(overlaySurface,  (255, 60, 0, 100), ((7 - (i % 8)) * (BOARD_SIZE / 8), (7 - (i // 8)) * (BOARD_SIZE / 8), (BOARD_SIZE / 8), (BOARD_SIZE / 8)))
        cam.blit(overlaySurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

        if heldPiece[0] != -1:
            m = cam.get_world_coord(pygame.mouse.get_pos())
            n.send(f"pos~{heldPiece[0]} {heldPiece[1]} {m[0]} {m[1]}")
            cam.blit(sprites.get_piece(heldPiece[1]), (m[0] - (SCALE / 2), m[1] - (SCALE / 2)))

def draw_other_held_piece(p, piece, pos):
    pos = (-pos[0] - (SCALE / 2), -pos[1] - (SCALE / 2))
    cam.blit(sprites.get_piece(piece[1]), pos)

def find_index(p, m):
    if p == 1:
        i = int((m[1] * 8) + m[0])
    else:
        i = int(((7 - m[1]) * 8) + (7 - m[0]))
    return i

# Variables
running = True
randomise = False 
positionsSeen = {combine(STARTING_POSITION.split(" ")[0:-2]): 1}
repetitionLoss = False
heldPiece = (-1, "")
otherHeldPiece = (-1, "")
validSquares = []
currentFen = STARTING_POSITION
dropSound = pygame.mixer.Sound(os.path.join("audio", "dropPiece.wav"))
font = pygame.font.SysFont("georgia", 50)
selfWins = 0
opponentWins = 0
selfWinsText = font.render(str(selfWins), 1, (0, 0, 0))
opponentWinsText = font.render(str(opponentWins), 1, (0, 0, 0))

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
                            currentFen = newFen
                            newFenKey = combine(newFen.split(" ")[0:-2])
                            if newFenKey in positionsSeen:
                                positionsSeen[newFenKey] += 1
                            else:
                                positionsSeen[newFenKey] = 1
                            n.send(f"play~{newFen}")
                            pygame.mixer.Sound.play(dropSound)
                    heldPiece = (-1, "")
                    n.send("pos~none")
                    validSquares = []

        win.fill((255, 255, 255))
        cam.blit(boardSurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))
        cam.blit(selfWinsText, (350 - (selfWinsText.get_width() // 2), 300 - selfWinsText.get_height()))
        cam.blit(opponentWinsText, (350 - (opponentWinsText.get_width() // 2), -300))

        draw_pieces(playerID, pieces, heldPiece, validSquares, otherHeldPiece)

        if board.get_turn() != playerID:
            data = n.send("get").split("~")
            gotFen = data[0]
            otherHeldPieceData = data[1]
            if gotFen != currentFen and gotFen != "none":
                board = Board(gotFen)
                newFenKey = combine(gotFen.split(" ")[0:-2])
                if newFenKey in positionsSeen:
                    positionsSeen[newFenKey] += 1
                else:
                    positionsSeen[newFenKey] = 1
                currentFen = gotFen
                pygame.mixer.Sound.play(dropSound)
            if otherHeldPieceData != "none":
                pieceData = otherHeldPieceData.split(" ")
                otherHeldPiece = (int(pieceData[0]), pieceData[1])
                pos = (float(pieceData[2]), float(pieceData[3]))
                draw_other_held_piece(playerID, otherHeldPiece, pos)
            else:
                otherHeldPiece = (-1, "")

        pygame.display.update()

        if board.check_gameover() >= 0 or repetitionLoss:
            gameoverCondition = board.check_gameover()
            print("GAME OVER ", {-1: "Repetition", 0: "Black Stalemated", 1: "Black checkmated", 2: "White checkmated", 3: "50 Moves draw", 4: "White stalemated"}[gameoverCondition])
            winMsg = ""
            if gameoverCondition in [0, 3, 4] or repetitionLoss:
                winMsg = "Draw!"
            elif gameoverCondition == 1:
                winMsg = "White wins!"
                if playerID == 1:
                    selfWins += 1
                else:
                    opponentWins += 1
            elif gameoverCondition == 2:
                winMsg = "Black wins!"
                if playerID == 1:
                    opponentWins += 1
                else:
                    selfWins += 1

            win.fill((255, 255, 255))
            cam.blit(boardSurface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))
            
            draw_pieces(playerID, board.get_pieces(), heldPiece, validSquares, otherHeldPiece)

            x1, y1 = 0, -350
            x2, y2 = 0, 350
            winText = font.render(winMsg, 1, (0, 0, 0))
            restartText = font.render("Press 'R' to restart", 1, (0, 0, 0))
            cam.blit(winText, (x1 - (winText.get_width() // 2), y1 - (winText.get_height() // 2)))
            cam.blit(restartText, (x2 - (restartText.get_width() // 2), y2 - (restartText.get_height() // 2)))

            selfWinsText = font.render(str(selfWins), 1, (0, 0, 0))
            opponentWinsText = font.render(str(opponentWins), 1, (0, 0, 0))
            cam.blit(selfWinsText, (350 - (selfWinsText.get_width() // 2), 300 - selfWinsText.get_height()))
            cam.blit(opponentWinsText, (350 - (opponentWinsText.get_width() // 2), -300))

            pygame.display.update()

            restarted = False
            while not restarted:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            playerID = (playerID + 1) % 2
                            board = Board(STARTING_POSITION)
                            positionsSeen = None
                            positionsSeen = {combine(STARTING_POSITION.split(" ")[0:-2]): 1}
                            repetitionLoss = False
                            heldPiece = (-1, "")
                            otherHeldPiece = (-1, "")
                            validSquares = []
                            currentFen = STARTING_POSITION
                            restarted = True
                            n.send("over")

        for key in positionsSeen:
            if positionsSeen[key] >= 5:
                print(key)
                repetitionLoss = True