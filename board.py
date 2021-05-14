import copy

def display_list(L):
    print("____")
    for i in range(8):
        row = ""
        for j in range(8):
            row += f"{L[(i * 8) + j]} "
        print(row)
    print("____")

class Board:
    def __init__(self, fen):
        self.pieces = [0 for i in range(64) ]
        self.virtual_pieces = copy.copy(self.pieces)
        self.whiteCastling = [False, False]
        self.blackCastling = [False, False]
        self.halfMoves = 0
        self.fullMoves = 0
        self.turn = 1
        self.enPassantIndex = -1
        self.fen = fen
        self.distanceToEdge = self.generate_distances()
        self.slidingOffsets = [-1, 1, -8, 8, -9, -7, 7, 9]
        self.knightOffsets = [-17, -15, -10, -6, 6, 10, 15, 17]
        self.load_fen(fen)

    def get_pieces(self):
        return self.pieces

    def get_turn(self):
        return self.turn

    def make_move(self, piece, i, virtual = False):
        pieces = {True: copy.copy(self.pieces), False: self.pieces}[virtual]

        pieces[piece[0]] = 0
        if pieces[i] != 0 and not virtual:
            self.halfMoves = -1
        pieces[i] = piece[1]
        
        # En passant detection
        if piece[1].lower() == "p":
            if not virtual:
                self.halfMoves = -1
            if i == self.enPassantIndex:
                if self.turn:
                    pieces[i + 8] = 0
                else:
                    pieces[i - 8] = 0
            self.enPassantIndex = -1
            if self.turn and (i == piece[0] - 16):
                self.enPassantIndex = piece[0] - 8
            elif not self.turn and (i == piece[0] + 16):
                self.enPassantIndex = piece[0] + 8
            if self.turn and (i // 8 == 0):
                pieces[i] = "Q"
            elif not self.turn and (i // 8 == 7):
                pieces[i] = "q"
        else:
            self.enPassantIndex = -1

        if piece[1].lower() == "k":
            if ((self.turn and self.whiteCastling[0]) or (not self.turn and self.blackCastling[0])) and (i == piece[0] + 2):
                pieces[piece[0] + 1] = {True: "R", False: "r"}[self.turn]
                pieces[piece[0] + 3] = 0
            if ((self.turn and self.whiteCastling[1]) or (not self.turn and self.blackCastling[1])) and (i == piece[0] - 2):
                pieces[piece[0] - 1] = {True: "R", False: "r"}[self.turn]
                pieces[piece[0] - 4] = 0
            if self.turn and not virtual:
                self.whiteCastling = [False, False]
            elif not virtual:
                self.blackCastling = [False, False]
            
        elif piece[1].lower() == "r":
            if self.whiteCastling[0] and piece[0] == 63:
                self.whiteCastling[0] = False
            elif self.whiteCastling[1] and piece[0] == 56:
                self.whiteCastling[1] = False
            elif self.blackCastling[0] and piece[0] == 7:
                self.blackCastling[0] = False
            elif self.blackCastling[1] and piece[0] == 0:
                self.blackCastling[1] = False

        if not virtual and self.whiteCastling[0] and self.pieces[63] != "R":
            self.whiteCastling[0] = False
        if not virtual and self.whiteCastling[1] and self.pieces[56] != "R":
            self.whiteCastling[1] = False
        if not virtual and self.blackCastling[0] and self.pieces[7] != "r":
            self.blackCastling[0] = False
        if not virtual and self.blackCastling[1] and self.pieces[0] != "r":
            self.blackCastling[1] = False

        if virtual:
            self.virtual_pieces = pieces
        else:
            self.turn = (self.turn + 1) % 2
            if self.turn == 1:
                self.fullMoves += 1
            self.halfMoves += 1
            

    def check_checks(self, virtual = False):
        pieces = {True: self.virtual_pieces, False: copy.copy(self.pieces)}[virtual]
        
        check = [False, False]

        for i, piece in enumerate(pieces):
            if piece != 0:
                moves = self.get_valid_moves((i, piece), True)
                if piece.islower() and "K" in [ pieces[m] for m in moves ]:
                    check[0] = True
                elif piece.isupper() and "k" in [ pieces[m] for m in moves ]:
                    check[1] = True

        return check

    def check_gameover(self):

        # 0 = stalemate
        # 1 = white win (checkmate)
        # 2 = black win (checkmate)
        # 3 = 50 moves draw

        winner = -1
        pieces = self.pieces
        self.virtual_pieces = copy.copy(self.pieces)
        
        canMove = [False, False]
        for i, piece in enumerate(pieces):
            if piece != 0:
                moves = self.get_valid_moves((i, piece))
                if len(moves) > 0:
                    # print(i, piece, moves)
                    pass
                if not canMove[0] and len(moves) > 0 and piece.isupper():
                    canMove[0] = True
                if not canMove[1] and len(moves) > 0 and piece.islower():
                    canMove[1] = True
        self.pieces = pieces
        checks = self.check_checks()
        if not canMove[0]:
            if checks[0]:
                winner = 2
            else:
                winner = 4
        if not canMove[1]:
            if checks[1]:
                winner = 1
            else:
                winner = 0
        if self.halfMoves >= 50 and winner == -1:
            winner = 3
        return winner


    def get_valid_moves(self, piece, virtual = False):
        type = piece[1].lower()
        position = piece[0]
        pieces = {True: self.virtual_pieces, False: self.pieces}[virtual]
        white = piece[1].isupper()
        valid = []

        if type == "q" or type == "b" or type == "r":
            inum = {"q": (0, 8), "r": (0, 4), "b": (4, 8)}[type]
            for i in range(inum[0], inum[1]):
                offset = d = self.slidingOffsets[i]
                for j in range(self.distanceToEdge[position][d]):

                    p = position + (offset * (j + 1))
                    s = pieces[p]

                    if s != 0:
                        if (s.isupper() and white) or (s.islower() and not white):
                            break
                        if (s.isupper() and not white) or (s.islower() and white):
                            valid.append(p)
                            break

                    valid.append(p)
        elif type == "n":
            distances = [ self.distanceToEdge[position][i] for i in self.slidingOffsets[0:4] ]
            for i in range(len(self.knightOffsets)):
                offset = self.knightOffsets[i]
                p = position + offset
                if p >= 0 and p < 64:
                    s = None
                    if 0 <= i < 2 and distances[2] >= 2:
                        if (i == 0 and distances[0] >= 1) or (i == 1 and distances[1] >= 1):
                            s = pieces[p]
                    elif 2 <= i < 4 and distances[2] >= 1:
                        if (i == 2 and distances[0] >= 2) or (i == 3 and distances[1] >= 2):
                            s = pieces[p]
                    elif 4 <= i < 6 and distances[3] >= 1:
                        if (i == 4 and distances[0] >= 2) or (i == 5 and distances[1] >= 2):
                            s = pieces[p]
                    elif 6 <= i < 8 and distances[3] >= 2:
                        if (i == 6 and distances[0] >= 1) or (i == 7 and distances[1] >= 1):
                            s = pieces[p]
                    if s is not None:
                        if s != 0:
                            if not ((s.isupper() and white) or (s.islower() and not white)):
                                valid.append(p)
                        else:
                            valid.append(p)
        elif type == "p":
            if white:
                startRow = 6
                offsets = [self.slidingOffsets[2], self.slidingOffsets[4], self.slidingOffsets[5]]
            else:
                startRow = 1
                offsets = [self.slidingOffsets[3], self.slidingOffsets[6], self.slidingOffsets[7]]
            for i in range(len(offsets)):
                p = position + offsets[i]
                if 0 <= p < 64:
                    s = pieces[p]
                    if i == 0:
                        if s == 0:
                            valid.append(p)
                            if position // 8 == startRow and pieces[p + offsets[i]] == 0:
                                valid.append(p + offsets[i])
                    else:
                        if self.distanceToEdge[position][offsets[i]] > 0:
                            if s != 0 and ((s.isupper() and not white) or (s.islower() and white)):
                                valid.append(p)
                            elif s == 0 and p == self.enPassantIndex:
                                valid.append(p)
        elif type == "k":
            for i in range(0, 8):
                offset = self.slidingOffsets[i]
                if self.distanceToEdge[position][offset] > 0:
                    p = position + offset
                    s = pieces[p]
                    if s != 0:
                        if (s.isupper() and white) or (s.islower() and not white):
                            continue
                    valid.append(p)
            if (white and self.whiteCastling[0]) or (not white and self.blackCastling[0]):
                if not virtual and pieces[position + 1] == 0 and pieces[position + 2] == 0 and pieces[position + 3] != 0 and pieces[position + 3].lower() == "r":
                    self.virtual_pieces = copy.copy(self.pieces)
                    check1 = self.check_checks(True)
                    self.make_move(piece, position + 1, True)
                    check2 = self.check_checks(True)
                    if not check1[{True: 0, False: 1}[white]] and not check2[{True: 0, False: 1}[white]]:
                        valid.append(position + 2)
            if (white and self.whiteCastling[1]) or (not white and self.blackCastling[1]):
                if not virtual and pieces[position - 1] == 0 and pieces[position - 2] == 0 and pieces[position - 3] == 0 and pieces[position - 4] != 0 and pieces[position - 4].lower() == "r" and not virtual:
                    self.virtual_pieces = copy.copy(self.pieces)
                    check1 = self.check_checks(True)
                    self.make_move(piece, position - 1, True)
                    check2 = self.check_checks(True)
                    if not check1[{True: 0, False: 1}[white]] and not check2[{True: 0, False: 1}[white]]:
                        valid.append(position - 2)

        if not virtual:
            invalid = []
            ep = self.enPassantIndex
            c = [ [self.whiteCastling[0], self.whiteCastling[1]], [self.blackCastling[0], self.blackCastling[1]] ]
            for i in range(len(valid)):
                self.make_move(piece, valid[i], True)
                checks = self.check_checks(True)
                if checks[{True: 0, False: 1}[white]]:
                    invalid.append(valid[i])
            valid = [ x for x in valid if x not in invalid]
            self.enPassantIndex = ep
            self.whiteCastling = c[0]
            self.blackCastling = c[1]

        return valid

    def generate_distances(self):
        distances = [ 0 for i in range(64) ]
        for position in range(64):
            pieceBounds = [position % 8, 7 - (position % 8), position // 8, 7 - (position // 8)]
            distances[position] = { -1: pieceBounds[0], 1: pieceBounds[1], 
                                    -8: pieceBounds[2], 8: pieceBounds[3], 
                                    -9: min(pieceBounds[0], pieceBounds[2]),
                                    -7: min(pieceBounds[1], pieceBounds[2]),
                                    7: min(pieceBounds[0], pieceBounds[3]),
                                    9: min(pieceBounds[1], pieceBounds[3]) }
        return distances

    def load_fen(self, fen):
        fen = fen.split(" ")
        rows = fen[0].split("/")
        turn = fen[1]
        castling = fen[2]
        enPassant = fen[3]
        halfMoves = fen[4]
        fullMoves = fen[5]
        
        # PIECES LOADING
        i = 0
        row = 0
        rowCounter = 0
        while i < 64:
            if i // 8 != row:
                row = i // 8
                rowCounter = 0
            p = rows[row][rowCounter]
            if p.isdigit():
                i += int(p)
                rowCounter += 1
            else:
                self.pieces[i] = p
                i += 1
                rowCounter += 1
            
        # TURN LOADING
        if turn == "w":
            self.turn = 1
        else:
            self.turn = 0

        # CASTLING LOADING
        self.whiteCastling = ["K" in castling, "Q" in castling]
        self.blackCastling = ["k" in castling, "q" in castling]

        # EN PASSANT LOADING
        letters = "abcdefgh"
        if enPassant != "-": 
            self.enPassantIndex = (64 - (int(enPassant[1]) * 8)) + letters.index(enPassant[0])
        else:
            self.enPassantIndex = -1

        # MOVE LOADING
        self.halfMoves = int(halfMoves)
        self.fullMoves = int(fullMoves)


    def generate_fen(self):
        fen = ""
        pieces = ""
        t = 0
        for row in range(8):
            for col in range(8):
                if self.pieces[(row * 8) + col] == 0:
                    t += 1
                else:
                    if t > 0:
                        pieces += str(t)
                        t = 0
                    pieces += self.pieces[(row * 8) + col]
            if t > 0:
                pieces += str(t)
                t = 0
            pieces += "/"
        pieces = pieces[:-1]

        turn = {1:"w", 0:"b"}[self.turn]

        castling = ""
        castling += {True:"K", False:""}[self.whiteCastling[0]]
        castling += {True:"Q", False:""}[self.whiteCastling[1]]
        castling += {True:"k", False:""}[self.blackCastling[0]]
        castling += {True:"q", False:""}[self.blackCastling[1]]
        if castling == "":
            castling = "-"

        enpassant = ""
        if self.enPassantIndex == -1:
            enpassant = "-"
        else:
            enpassant += ["a", "b", "c", "d", "e", "f", "g", "h"][self.enPassantIndex % 8]
            enpassant += str(8 - (self.enPassantIndex // 8))

        moves = f"{self.halfMoves} {self.fullMoves}"

        fen = f"{pieces} {turn} {castling} {enpassant} {moves}"

        return fen