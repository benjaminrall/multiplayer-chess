from typing import cast


class Board:

    pieceTypes =   {"K": 1, "P": 2, "N": 3, "B": 4, "R": 5, "Q": 6,
                    1: "K", 2: "P", 3: "N", 4: "B", 5: "R", 6: "Q"}

    def __init__(self, fen):
        self.pieces = [0 for i in range(64) ]
        self.whiteCastling = [False, False]
        self.blackCastling = [False, False]
        self.halfMoves = 0
        self.fullMoves = 0
        self.turn = 1
        self.enPassantIndex = -1
        self.fen = fen
        self.load_fen(fen)

    def get_pieces(self):
        return self.pieces

    def get_turn(self):
        return self.turn

    def make_move(self, piece, i):
        self.pieces[piece[0]] = 0
        self.pieces[i] = piece[1]
        self.turn = (self.turn + 1) % 2

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
        self.whiteCastling[0] = "K" in castling
        self.whiteCastling[1] = "Q" in castling
        self.blackCastling[0] = "k" in castling
        self.blackCastling[1] = "q" in castling

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
