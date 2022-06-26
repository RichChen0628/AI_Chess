# This class is responsible for storing all the information
# about the current state of a chess game.
# It will also be responsible for determining the valid moves at the current state.
# It will also keep a move log.

class GameState():
    def __init__(self):
        # Board is an 8x8 2D list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'B', 'N', 'R' or 'p'
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = ()   # coordinates for the square where en passant capture is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        # castling rights
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]



        # Takes a move as a parameter and executes it
    # This will not work for castling, pawn promotion and en-passant
    def makeMove(self, move):
        #print("makeMove")
        self.board[move.startRow][move.startCol] = "--"   # clear the moved piece
        self.board[move.endRow][move.endCol] = move.pieceMoved   # set the moved piece to new location
        self.moveLog.append(move)   # log the move so we can undo it later if we need
        self.whiteToMove = not self.whiteToMove   # swap player
        # update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # if pawn moves 2 squares, next move can capture en passant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # if an en passant move, must update the board to capture the pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'   # capturing the pawn

        # pawn promotion
        if move.isPawnPromotion:
            #promotedPiece = input("Promote to Q, R, B, or N:")   # we can make this part of the UI later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # castle move
        if move.isCastleMove:
            if (move.endCol - move.startCol) == 2:  # king-side castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]   # move the rook
                self.board[move.endRow][move.endCol+1] = '--'   # erase the old rook
            else:   # queen-side castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]   # move the rook
                self.board[move.endRow][move.endCol-2] = '--'   # erase the old rook

        self.enPassantPossibleLog.append(self.enPassantPossible)

        # update castling rights - whenever it is a rook or a king move
        #print(move.pieceMoved)
        self.updateCastleRights(move)
        #print(move.pieceMoved)

        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))



    # Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0:   # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove   # switch turns back
            # update the king's location if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'   # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # give back castle rights if move took them away
            self.castleRightsLog.pop()   # get rid of the new castle rights from the move we are undoing
            #self.currentCastlingRight = self.castleRightsLog[-1]   # set the current castle rights to the last one in the list
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            #for log in self.castleRightsLog:
            #    print(log.wks, log.bks, log.wqs, log.bqs, end=", ")
            #print()

            # undo castle move
            if move.isCastleMove:
                if (move.endCol - move.startCol) == 2:  # king-side castle move
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]   # move the rook back
                    self.board[move.endRow][move.endCol-1] = '--'   # erase the new rook
                else:   # queen-side castle move
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]   # move the rook back
                    self.board[move.endRow][move.endCol+1] = '--'   # erase the new rook

            # add for "findBestMove"
            self.checkmate = False
            self.stalemate = False


    def updateCastleRights(self, move):
        # append and set "currentCastlingRight" to the last [-1] of "castleRightsLog", otherwise "castleRightsLog" [-2] would be updated
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        self.currentCastlingRight = self.castleRightsLog[-1]
        #for log in self.castleRightsLog:
        #    print(log.wks, log.bks, log.wqs, log.bqs, end=", ")
        #print()
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:   # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:   # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:   # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:   # right rook
                    self.currentCastlingRight.bks = False

        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

        #for log in self.castleRightsLog:
        #    print(log.wks, log.bks, log.wqs, log.bqs, end=", ")
        #print()



    # All moves considering checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:   # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check, you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]   # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]   # enemy piece causing the check
                validSquares = []   # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)   # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:   # once you get to piece end checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):   # go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K':   # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:   # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:   # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:   # not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves


#    # All moves considering checks
#    def getValidMoves(self):
#        #for log in self.castleRightsLog:
#        #    print(log.wks, log.bks, log.wqs, log.bqs, end=", ")
#        #print()
#        tempEnpassantPossible = self.enPassantPossible
#        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
#                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
#
#        # 1). generate all possible moves
#        moves = self.getAllPossibleMoves()
#        if self.whiteToMove:
#            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
#        else:
#            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
#        # 2). for each move, make the move
#        for i in range(len(moves) - 1, -1, -1):  # when removing from a list, go backward through that list
#            self.makeMove(moves[i])
#            # 3). generate all opponent's moves
#            # 4). for each of your opponent's moves, see if they attack you king
#            self.whiteToMove = not self.whiteToMove  # switch turns back because makeMove switch the turn
#            if self.inCheck():
#                moves.remove(moves[i])  # 5). if they do attack your king, not a valid move
#            self.whiteToMove = not self.whiteToMove
#            self.undoMove()
#
#        if len(moves) == 0:  # either checkmate or stalemate
#            if self.inCheck():
#                self.checkmate = True
#            else:
#                self.stalemate = True
#
#        self.enPassantPossible = tempEnpassantPossible
#        self.currentCastlingRight = tempCastleRights
#
#        return moves
#


    # determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    # determine if the enemy can attack the square (r, c)
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove   # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove   # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:   # square under attack
                return True
        return False


    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):   # number of rows
            for c in range(len(self.board[r])):   # number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)   # call the appropriate move function based on piece type
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKingLocation[0]
            start_col = self.blackKingLocation[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks



    # Get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--":   # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":   # 2 square moves
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        if c - 1 >= 0:   # capture to left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:   # king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:   # king is right of the pawn
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":   # some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if seqare[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):   # attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassantMove=True))
        if c+1 <= 7:   # capture to right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:   # king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:  # king is right of the pawn
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":  # some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if seqare[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):  # attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassantMove=True))

#
#        if self.whiteToMove:   # white pawn move
#            if self.board[r-1][c] == "--":   # 1 square pawn advance
#                moves.append(Move((r, c), (r-1, c), self.board))
#                if r == 6 and self.board[r-2][c] == "--":   # 2 squares pawn advance
#                    moves.append(Move((r, c), (r-2, c), self.board))
#            if c-1 >= 0:   # captures to the left enemy piece
#                if self.board[r-1][c-1][0] == 'b':   # enemy piece to capture
#                    moves.append(Move((r, c), (r-1, c-1), self.board))
#                elif (r-1, c-1) == self.enPassantPossible:
#                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
#            if c+1 <= 7:   # captures to the right enemy piece
#                if self.board[r-1][c+1][0] == 'b':   # enemy piece to capture
#                    moves.append(Move((r, c), (r-1, c+1), self.board))
#                elif (r-1, c+1) == self.enPassantPossible:
#                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
#        else:   # black pawn move
#            if self.board[r+1][c] == "--":   # 1 square pawn advance
#                moves.append(Move((r, c), (r+1, c), self.board))
#                if r == 1 and self.board[r+2][c] == "--":   # 2 squares pawn advance
#                    moves.append(Move((r, c), (r+2, c), self.board))
#            if c-1 >= 0:   # captures to the left enemy piece
#                if self.board[r+1][c-1][0] == 'w':   # enemy piece to capture
#                    moves.append(Move((r, c), (r+1, c-1), self.board))
#                elif (r+1, c-1) == self.enPassantPossible:
#                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
#            if c+1 <= 7:   # captures to the right enemy piece
#                if self.board[r+1][c+1][0] == 'w':   # enemy piece to capture
#                    moves.append(Move((r, c), (r+1, c+1), self.board))
#                elif (r+1, c+1) == self.enPassantPossible:
#                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
#


    # Get all the rook moves for the pawn located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))   # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:   # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":   # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:   # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:   # friendly piece invalid
                        break
                else:   # off board
                    break


    # Get all the knight moves for the knight located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:   # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    # Get all the bishop for the bishop located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))   # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):   # bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:   # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":   # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:   # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:   # friendly piece invalid
                        break
                else:   # off board
                    break


    # Get all the queen for the queen located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # Get all the king moves for the king located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:   # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:   # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    # Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return   # can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)


    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    # Generate queenside castle moves for the king at (r, c).
    # This method will only be called if player still has castle rights queenside.
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))



class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # map keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCapture = self.pieceCaptured != '--'
        # castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False



    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


    # overriding the str() function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

            # pawn promotion

        # two of the same type of piece moving to a square, Nbd2 if both knights can move to d2

        # also adding + for check move, and # for checkmate move



        # piece move
        moveString = self.pieceMoved
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare




