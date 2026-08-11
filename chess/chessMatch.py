from boardgame.board import Board
from boardgame.position import Position
from boardgame.piece import Piece
from chess.color import Color
from chess.chessPiece import ChessPiece
from chess.chessPosition import ChessPosition
from chess.chessException import ChessException
from chess.pieces.rook import Rook
from chess.pieces.king import King
from chess.pieces.bishop import Bishop
from chess.pieces.knight import Knight
from chess.pieces.queen import Queen
from chess.pieces.pawn import Pawn

# Classe que vai conter as "Regras" do Jogo de Xadrez

class ChessMatch:

    def __init__(self):
        self._board = Board(8, 8)
        self._turn = 1
        self._currentPlayer = Color.WHITE
        self._check = False
        self._checkMate = False
        self._staleMate = False
        self._enPassantVulnerable: ChessPiece = None
        self._promoted: ChessPiece = None
        self._capturedPieces: list[Piece] = []
        self._piecesOnTheBoard: list[Piece] = []
        self._pendingPromotion = False
        self._pendingSource = None
        self._pendingTarget = None
        # 🔹 Estados de empate
        self._draw = False
        self._drawReason = ""
        self._initialSetup()

    @property
    def check(self):
        """Indica se o jogador atual está em Check"""
        return self._check
    
    @property
    def checkMate(self):
        """Indica se a partida terminou em Checkmate"""
        return self._checkMate

    @property
    def staleMate(self):
        """Indica se a partida terminou por stalemate."""
        return self._staleMate

    @property
    def turn(self):
        """Retorna o turno atual"""
        return self._turn

    @property
    def currentPlayer(self) -> Color:
        """Retorna o jogador atual (branco ou preto)."""
        return self._currentPlayer
    
    @property
    def enPassantVulnerable(self) -> ChessPiece:
        return self._enPassantVulnerable
    
    @property
    def promoted(self) -> ChessPiece:
        """Retorna a peça promovida."""
        return self._promoted

    @property
    def draw(self) -> bool:
        """Indica se a partida terminou em empate."""
        return self._draw

    @property
    def drawReason(self) -> str:
        """Indica o motivo do empate."""
        return self._drawReason

    """ Método que Cria a Matriz 8x8 com as peças do tabuleiro """
    def getPieces(self):
        return [[self._board.piece(row, col) for col in range(self._board.columns)] 
            for row in range(self._board.rows)]
    
    def possibleMoves(self, sourcePosition: ChessPosition):
        """Retorna uma matriz booleana com os possíveis movimentos da peça na posição escolhida."""
        # Se houver uma promoção pendente, é preciso confirmá-la antes de continuar
        if self._pendingPromotion:
            raise ChessException("Promotion must be confirmed first.")

        position = sourcePosition.toPosition()
        self._validateSourcePosition(position)  # Certifica-se de que a posição inicial é válida
        return self._board.pieceByPosition(position).possibleMoves()  # Retorna movimentos possíveis da peça

    def performChessMove(self, sourcePosition: ChessPosition, targetPosition: ChessPosition) -> ChessPiece:
        """Executa um movimento de peça"""

        if self._pendingPromotion:
            raise ChessException("Promotion must be confirmed first.")
        
        source = sourcePosition.toPosition()
        target = targetPosition.toPosition()

        if not self._board.positionExists(source) or not self._board.positionExists(target):
            raise ChessException("Invalid Source or Target position.")

        """Valida se a peça pode ser movida"""
        self._validateSourcePosition(source)
        self._validateTargetPosition(source, target)

        """Realiza o movimento e armazena a peça capturada, se houver"""
        capturedPiece = self._makeMove(source, target)
        
        """Efetua a verificação de Auto-Check
        (um jogador não pode realizar uma jogada que o deixe a si próprio em check)
        """
        if self._testCheck(self.currentPlayer):
            self._undoMove(source, target, capturedPiece)
            raise ChessException("You can't put yourself in Check!")
        
        """movedPiece armazena a peça que se encontra na posição de destino. Isto é NECESSÁRIO para as regras de EnPassant e Promoção do Peão"""
        movedPiece: ChessPiece = self._board.pieceByPosition(target)

        """ 🔹 Implementação da promoção do Peão: quando ele chega à última linha, o turno fica pendente. """
        if isinstance(movedPiece, Pawn):
            promoted = ((movedPiece.color == Color.WHITE and target.row == 0) or (movedPiece.color == Color.BLACK and target.row == 7))

            if promoted:
                self._promoted = movedPiece
                self._pendingPromotion = True
                self._pendingSource = source
                self._pendingTarget = target
                self._enPassantVulnerable = None
                return capturedPiece

        self._finishTurn(source, target, movedPiece)
        return capturedPiece

    def _finishTurn(self, source: Position, target: Position, movedPiece: ChessPiece):
        """Termina a jogada: atualiza en passant, check, checkmate, stalemate e turno."""

        """ 🔹 Implementação da Verificação En Passant
        Quando um Peão avança Duas Casas, ele fica vulnerável à captura En Passant. """
        if isinstance(movedPiece, Pawn) and abs(target.row - source.row) == 2:
            self._enPassantVulnerable = movedPiece      # A variável movedPiece vai "marcar" esse peão como vulnerável
        else:
            self._enPassantVulnerable = None

        opponent = self._opponent(self.currentPlayer)

        """Testa se o rei do adversário está em Check. Se Sim, então self._check atualiza para True"""
        self._check = self._testCheck(opponent)

        """Testa as condições de Checkmate, Stalemate e Material Insuficiente no tabuleiro, 
        para decidir se o jogo termina ou se avança para o turno seguinte."""
        if self._testCheckMate(opponent):
            self._checkMate = True
        elif self._testStaleMate(opponent):
            self._staleMate = True
        elif self._hasInsufficientMaterial():
            self._draw = True
            self._drawReason = "Draw by insufficient material"
        else:
            self._nextTurn()

    def confirmPromotion(self, type: str):
        """Confirma a peça escolhida para promoção e termina a jogada."""

        if not self._pendingPromotion or self._promoted is None:
            raise ChessException("There is no pending promotion.")

        self._replacePromotedPiece(type)

        source = self._pendingSource
        target = self._pendingTarget

        self._promoted = None
        self._pendingPromotion = False
        self._pendingSource = None
        self._pendingTarget = None

        movedPiece = self._board.pieceByPosition(target)
        self._finishTurn(source, target, movedPiece)

    def drawByAgreement(self):
        """Marca a partida como empatada por acordo entre os jogadores."""

        # Se o jogo já terminou, não faz sentido marcar empate
        if self._checkMate or self._draw:
            return

        # Empate depois de staleMate é impossível
        if getattr(self, "_staleMate", False):
            return

        self._draw = True
        self._drawReason = "Draw by agreement"
    
    def _replacePromotedPiece(self, type: str) -> ChessPiece:
        """Substitui o peão promovido pela peça escolhida."""

        if self._promoted is None:
            raise ChessException("There is no piece to be promoted")
        
        if type not in ["B", "N", "R", "Q"]:
            raise ChessException("Invalid promotion type")
        
        pos = self._promoted._position
        color = self._promoted.color

        p = self._board.removePiece(pos)
        self._piecesOnTheBoard.remove(p)

        newPiece = self._newPiece(type, color)
        self._board.placePiece(newPiece, pos)
        self._piecesOnTheBoard.append(newPiece)

        self._promoted = newPiece
        return newPiece
    

    def _newPiece(self, type: str, color: Color) -> ChessPiece:
        """Este método CRIA dinamicamente uma nova peça de acordo com a escolha do jogador."""
        if type == "B":
            return Bishop(self._board, color)
        if type == "N":
            return Knight(self._board, color)
        if type == "Q":
            return Queen(self._board, color)
        return Rook(self._board, color)  # Por padrão, se for inválido, retorna uma Torre
    

    def _makeMove(self, source: Position, target: Position) -> Piece:
        """Executa um movimento, removendo a peça da origem e colocando-a no destino."""
        
        piece: ChessPiece = self._board.removePiece(source)  # Remove a peça da origem
        piece._increaseMoveCount()  # Incrementa a contagem de movimentos
        
        capturedPiece = self._board.removePiece(target)  # Captura a peça do destino, se houver
        self._board.placePiece(piece, target)  # Move a peça para o destino

        # Se aplicável, vai chamar a lógica do movimento Roque (Castling)
        self._handleSpecialMoveCastling(piece, source, target)

        if capturedPiece:
            self._piecesOnTheBoard.remove(capturedPiece)  # Remove a peça capturada do tabuleiro
            self._capturedPieces.append(capturedPiece)  # Adiciona à lista de peças capturadas

        # 🔹 **Implementação do En Passant**
        if isinstance(piece, Pawn):
            if source.column != target.column and capturedPiece is None:
                pawnPosition = Position( # Define a posição do peão capturado em En Passant, consoante se trate de um peão de Cor Branca ou Preta.
                    target.row + 1 if piece.color == Color.WHITE else target.row - 1,
                    target.column
                )

                enPassantPawn = self._board.removePiece(pawnPosition) # O peão capturado é removido
                if enPassantPawn is not None:
                    capturedPiece = enPassantPawn
                    self._capturedPieces.append(capturedPiece)  # Adiciona-o à lista de peças capturadas
                    self._piecesOnTheBoard.remove(capturedPiece) # Remove da lista de peças em jogo

        return capturedPiece


    def _handleSpecialMoveCastling(self, piece: ChessPiece, source: Position, target: Position, undo = False):
        """Executa ou anula o movimento especial de Roque (Castling) consoante seja necessário"""
        
        if not isinstance(piece, King):
            return  # Apenas o Rei pode realizar o Roque

        if target.column == source.column + 2:  # Roque pelo lado do Rei (Kingside)
            sourceT = Position(source.row, source.column + 3)
            targetT = Position(source.row, source.column + 1)

        elif target.column == source.column - 2:  # Roque pelo lado da Rainha (Queenside)
            sourceT = Position(source.row, source.column - 4)
            targetT = Position(source.row, source.column - 1)

        else:
            return  # Se não for Roque, sai do método

        # Decide se está a executar ou desfazer o movimento do Roque
        if undo:
            rook: ChessPiece = self._board.removePiece(targetT)
            self._board.placePiece(rook, sourceT)
            rook._decreaseMoveCount()
        else:
            rook: ChessPiece = self._board.removePiece(sourceT)
            self._board.placePiece(rook, targetT)
            rook._increaseMoveCount()


    def _undoMove(self, source: Position, target: Position, capturedPiece: Piece):
        """Desfaz um movimento, restaurando a peça à sua posição original e devolvendo a peça capturada."""
        
        piece: ChessPiece = self._board.removePiece(target)  # Remove a peça da posição de destino
        piece._decreaseMoveCount()  # Reduz a contagem de movimentos
        
        self._board.placePiece(piece, source)  # Devolve a peça para a posição original

        self._handleSpecialMoveCastling(piece, source, target, undo=True)
        
        # 🔹 **Implementação do Undo para En Passant**
        if (isinstance(piece, Pawn) and
            source.column != target.column and
            capturedPiece is not None and
            capturedPiece is self.enPassantVulnerable):
            pawnPosition = Position(  # Define a posição correta para restaurar o peão capturado por En Passant
                3 if piece.color == Color.WHITE else 4,  # Se peão branco, volta para Linha 3; se preto, volta para Linha 4
                target.column  # Mantém a coluna da peça capturada
            )
            self._board.placePiece(capturedPiece, pawnPosition) # Restaura o peão à sua posição original
            self._capturedPieces.remove(capturedPiece)  # Remove o peão da lista de peças capturadas
            self._piecesOnTheBoard.append(capturedPiece) # Devolve o peão à lista de peças em jogo

        # Undo de captura normal
        elif capturedPiece:
            self._board.placePiece(capturedPiece, target)  # Recoloca a peça capturada no tabuleiro
            self._capturedPieces.remove(capturedPiece)  # Remove da lista de peças capturadas
            self._piecesOnTheBoard.append(capturedPiece)  # Devolve à lista de peças em jogo


    def _validateSourcePosition(self, position: Position):
        """Verifica se a peça pode ser movimentada pelo jogador atual."""
        if not self._board.thereIsAPiece(position):
            raise ChessException("There is no piece on source position.")
        
        piece: ChessPiece = self._board.pieceByPosition(position)
        if self.currentPlayer != piece.color:
            raise ChessException("The chosen piece is not yours.")
        
        if not piece.isThereAnyPossibleMove():
            raise ChessException("There are no possible moves for the chosen piece.")
        
        
    def _validateTargetPosition(self, source: Position, target: Position):
        """Verifica se a peça pode mover-se para a posição de destino.
    
        Se a peça na posição de origem não puder mover-se para o destino, dispara uma exceção.
        """

        # Valida se a posição de destino existe
        if not self._board.positionExists(target):
            raise ChessException("Target position is invalid.")

        piece: Piece = self._board.pieceByPosition(source)
        targetPiece = self._board.pieceByPosition(target)

        # Impede auto-captura
        if targetPiece is not None and targetPiece.color == piece.color:
            raise ChessException("You cannot capture your own piece.")

        # Impede captura do rei
        if isinstance(targetPiece, King):
            raise ChessException("You cannot capture the king!")
        
        # Confirma se a peça em específico se pode mover para o alvo
        if not piece.possibleMove(target):  
            raise ChessException("The chosen piece can't move to the target position")


    def _isSquareAttacked(self, position: Position, byColor: Color) -> bool:
        """Verifica se uma casa está atacada por peças de uma determinada cor."""

        row = position.row
        col = position.column

        for piece in self._piecesOnTheBoard:
            if not isinstance(piece, ChessPiece):
                continue

            if piece.color != byColor:
                continue

            if piece.position is None:
                continue

            # Peões atacam sempre na diagonal, independentemente de a casa estar vazia
            if isinstance(piece, Pawn):
                direction = -1 if piece.color == Color.WHITE else 1
                if piece.position.row + direction == row and abs(piece.position.column - col) == 1:
                    return True

            # O rei ataca as casas adjacentes
            elif isinstance(piece, King):
                if max(abs(piece.position.row - row), abs(piece.position.column - col)) == 1:
                    return True

            # As restantes peças usam os movimentos possíveis
            else:
                moves = piece.possibleMoves()
                if moves[row][col]:
                    return True

        return False


    def _nextTurn(self):
        """Avança para o próximo turno e troca o jogador."""
        self._turn += 1
        self._currentPlayer = Color.BLACK if self._currentPlayer == Color.WHITE else Color.WHITE


    def _opponent(self, color: Color):
        """Retorna a cor do jogador adversário"""
        return Color.BLACK if color == Color.WHITE else Color.WHITE


    def _king(self, color: Color) -> ChessPiece:
        """Retorna a peça do Rei de determinada cor. Lança exceção se não houver Rei."""
        
        for piece in self._piecesOnTheBoard:
            if isinstance(piece, King) and piece.color == color:
                return piece
        raise ChessException(f"Critical Error: {color} king not found.")


    def _testCheck(self, color: Color) -> bool:
        """Verifica se o jogador está em 'Check'."""

        # Verifica a existência do Rei
        try:
            king = self._king(color)
        except ChessException:
            return False  # Evita erro se rei não for encontrado (impossível)

        # Verifica se a posição do Rei no tabuleiro está em risco por peças do adversário
        return self._isSquareAttacked(king.position, self._opponent(color))


    def _testCheckMate(self, color: Color) -> bool:
        """Verifica se o jogador está em Checkmate.
        
        O Checkmate ocorre quando:
        - O jogador já está em 'Check'.
        - Nenhuma peça desse jogador tem um movimento possível que remova o Check.
        """
        if not self._testCheck(color):  # Se não estiver em Check, não é Checkmate
            return False

        return not self._hasAnyLegalMove(color)


    def _hasAnyLegalMove(self, color: Color) -> bool:
        """Verifica se o jogador de uma cor tem alguma jogada legal."""

        # Obtém todas as peças do jogador atual
        playerPieces: list[ChessPiece] = [
            p for p in self._piecesOnTheBoard
            if isinstance(p, ChessPiece) and p.color == color
        ]

        # Testa cada peça para ver se algum movimento é possível, nomeadamente movimentos que removem
        # o estado de Check
        for piece in playerPieces:
            possibleMoves = piece.possibleMoves()
            source = piece.getChessPosition().toPosition()

            for row in range(self._board.rows):
                for col in range(self._board.columns):
                    if not possibleMoves[row][col]:
                        continue

                    target = Position(row, col)
                    targetPiece = self._board.pieceByPosition(target)

                    # Não permitir capturar o rei
                    if isinstance(targetPiece, King):
                        continue

                    # Não permitir capturar peça própria
                    if targetPiece is not None and targetPiece.color == color:
                        continue

                    capturedPiece = self._makeMove(source, target)
                    stillInCheck = self._testCheck(color)
                    self._undoMove(source, target, capturedPiece)

                    if not stillInCheck: # Se algum movimento puder remover o Check, não é Checkmate
                        return True

        return False # Quando é Falso: Checkmate ou Stalemate


    def _testStaleMate(self, color: Color) -> bool:
        """Verifica se o jogador está em stalemate."""

        if self._testCheck(color):
            return False

        return not self._hasAnyLegalMove(color)

    def _hasInsufficientMaterial(self) -> bool:
        """Verifica algumas situações de material (peças) insuficientes para
        atingir o Checkmate

        Considera empate nos casos mais comuns:
        - Rei contra Rei
        - Rei + peça menor contra Rei
        - Rei + Bispo contra Rei + Bispo, com bispos na mesma cor de casa

        Outras situações mais complexas não são automaticamente consideradas empate.
        """

        # Peças que ainda estão no tabuleiro
        pieces = self._piecesOnTheBoard

        # Por segurança, o jogo deve ter exatamente dois reis
        kings = [piece for piece in pieces if isinstance(piece, King)]
        if len(kings) != 2:
            return False

        # Se existir algum peão, ainda existe possibilidade de promoção
        for piece in pieces:
            if isinstance(piece, Pawn):
                return False

        # Rainhas e torres são material suficiente para checkmate
        for piece in pieces:
            if isinstance(piece, Queen) or isinstance(piece, Rook):
                return False

        # Peças menores: bispos e cavalos
        minors = [piece for piece in pieces if isinstance(piece, (Bishop, Knight))]

        # Se houver alguma peça que não seja rei ou peça menor,
        # por segurança não marcamos empate automático
        if len(kings) + len(minors) != len(pieces):
            return False

        # Rei contra rei
        if len(minors) == 0:
            return True

        # Rei + uma peça menor contra rei
        # Exemplo: K+B vs K ou K+N vs K
        if len(minors) == 1:
            return True

        # Rei + bispo contra rei + bispo, com bispos na mesma cor de casa
        if len(minors) == 2:
            whiteMinors = [piece for piece in minors if piece.color == Color.WHITE]
            blackMinors = [piece for piece in minors if piece.color == Color.BLACK]

            # Tem de existir exatamente uma peça menor de cada lado
            if len(whiteMinors) == 1 and len(blackMinors) == 1:
                whitePiece = whiteMinors[0]
                blackPiece = blackMinors[0]

                # Só consideramos este empate se ambas forem bispos
                if isinstance(whitePiece, Bishop) and isinstance(blackPiece, Bishop):

                    # Por segurança, as peças devem estar posicionadas
                    if whitePiece.position is None or blackPiece.position is None:
                        return False

                    # A cor da casa é determinada pela paridade da soma linha + coluna.
                    # Se a paridade for igual, os bispos estão em casas da mesma cor.
                    whiteSquareColor = (whitePiece.position.row + whitePiece.position.column) % 2
                    blackSquareColor = (blackPiece.position.row + blackPiece.position.column) % 2

                    # Bispos na mesma cor de casa normalmente não permitem mate forçado
                    if whiteSquareColor == blackSquareColor:
                        return True

        # Outras combinações não são consideradas insuficientes nesta implementação
        return False


    def _placeNewPiece(self, column: str, row: int, piece: ChessPiece):
        self._board.placePiece(piece, ChessPosition(column, row).toPosition())
        self._piecesOnTheBoard.append(piece)


    def _initialSetup(self):
        """Posiciona todas as peças no tabuleiro utilizando _placeNewPiece()."""

        # 🔹 Peças Brancas
        self._placeNewPiece('a', 1, Rook(self._board, Color.WHITE))
        self._placeNewPiece('b', 1, Knight(self._board, Color.WHITE))
        self._placeNewPiece('c', 1, Bishop(self._board, Color.WHITE))
        self._placeNewPiece('d', 1, Queen(self._board, Color.WHITE))
        self._placeNewPiece('e', 1, King(self._board, Color.WHITE, self))
        self._placeNewPiece('f', 1, Bishop(self._board, Color.WHITE))
        self._placeNewPiece('g', 1, Knight(self._board, Color.WHITE))
        self._placeNewPiece('h', 1, Rook(self._board, Color.WHITE))

        for col in "abcdefgh":
            self._placeNewPiece(col, 2, Pawn(self._board, Color.WHITE, self))

        # 🔹 Peças Negras
        self._placeNewPiece('a', 8, Rook(self._board, Color.BLACK))
        self._placeNewPiece('b', 8, Knight(self._board, Color.BLACK))
        self._placeNewPiece('c', 8, Bishop(self._board, Color.BLACK))
        self._placeNewPiece('d', 8, Queen(self._board, Color.BLACK))
        self._placeNewPiece('e', 8, King(self._board, Color.BLACK, self))
        self._placeNewPiece('f', 8, Bishop(self._board, Color.BLACK))
        self._placeNewPiece('g', 8, Knight(self._board, Color.BLACK))
        self._placeNewPiece('h', 8, Rook(self._board, Color.BLACK))

        for col in "abcdefgh":
            self._placeNewPiece(col, 7, Pawn(self._board, Color.BLACK, self))