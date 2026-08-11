from chess.chessPiece import ChessPiece, Color
from chess.chessPosition import ChessPosition
from chess.chessMatch import ChessMatch
from chess.chessException import ChessException
from colorama import Fore, Back, Style, init
import os

init() # para iniciar o colorama

class UI:
    """Classe responsável pela exibição do tabuleiro de xadrez."""

    @staticmethod
    def clearScreen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def readChessPosition():
        """Lê e converte a entrada do utilizador numa posição de xadrez"""
        # Lê uma linha de input e tenta convertê-la para ChessPosition
        return UI.parseChessPosition(input())
   
    @staticmethod
    def parseChessPosition(text: str):
        """Converte texto do utilizador numa ChessPosition.

        Devolve None se o texto não for uma posição válida.
        """

        # Se não houver texto, não há posição válida
        if text is None:
            return None

        try:
            # Remove espaços e converte para minúsculas
            s = text.strip().lower()

            # O primeiro caractere é a coluna: a-h
            column = s[0]

            # O resto é a linha: 1-8
            row = int(s[1:])

            # Cria e devolve a posição de xadrez
            return ChessPosition(column, row)

        except (ValueError, IndexError, ChessException):
            # Entrada inválida ou posição fora dos limites
            return None
        
    @staticmethod
    def printMatch(chessMatch: ChessMatch, captured: list):
        """Exibe o estado atual da partida, incluindo o turno e o jogador atual."""
        UI.printBoard(chessMatch.getPieces())
        print()
        UI.printCapturedPieces(captured)
        print()
        print(f"\nTurn: {chessMatch.turn}")

        # 🔹 Fim de jogo por checkmate
        if chessMatch.checkMate:
            print("CHECKMATE!")
            print(f"Winner: {chessMatch.currentPlayer.value}")

        # 🔹 Fim de jogo por stalemate
        elif chessMatch.staleMate:
            print("STALEMATE!")
            print("Draw")

        # 🔹 Fim de jogo por empate
        elif chessMatch.draw:
            print("DRAW!")
            print(chessMatch.drawReason)

        # 🔹 Jogo ainda em curso
        else:
            print(f"Waiting player: {chessMatch.currentPlayer.value}")

            if chessMatch.check:
                print("CHECK")
    
    @staticmethod
    def printCapturedPieces(captured: list[ChessPiece]):
        """Mostra as peças capturadas por cor"""
        white = " ".join(str(piece) for piece in captured if piece.color == Color.WHITE)
        black = " ".join(str(piece) for piece in captured if piece.color == Color.BLACK)

        print("Captured pieces:")
        print(f"{Fore.WHITE}White: {white}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Black: {black}{Style.RESET_ALL}")

    @staticmethod
    def printBoard(pieces, possibleMoves=None):
        """Imprime o tabuleiro com coordenadas numéricas e letras, mostrando movimentos disponíveis."""
        for i in range(len(pieces)):  # Itera sobre as linhas
            print(f"{8 - i} ", end="")  # Numeração das linhas (8 a 1)
            for j in range(len(pieces[i])):  # Itera sobre as colunas
                background = possibleMoves is not None and possibleMoves[i][j]
                UI.printPiece(pieces[i][j], background)
            print()  # Nova linha após cada linha do tabuleiro
        print("  a b c d e f g h")  # Letras das colunas

    @staticmethod
    def printPiece(piece: ChessPiece, background=False):
        """Imprime uma peça de xadrez colorida ou um espaço vazio, destacando movimentos disponíveis."""
        if background:
            print(Back.BLUE, end="") # Destaca casas onde há movimentos possíveis
        
        if piece is None:
            print("-", end= " ") # Mostra um traço para espaços vazios
        else:
            color = Fore.WHITE if piece.color == Color.WHITE else Fore.YELLOW
            print(f"{color}{piece}{Style.RESET_ALL}", end=" ")
        print(Style.RESET_ALL, end="") # Realiza o reset da cor após a exibição da peça

    @staticmethod
    def askYesNo(prompt: str) -> bool:
        """Pergunta ao utilizador uma questão de sim/não.

        Devolve True se o utilizador responder sim.
        Devolve False se o utilizador responder não.
        """

        while True:
            answer = input(prompt).strip().lower()

            # Aceita respostas em inglês e português
            if answer in ["y", "yes", "s", "sim"]:
                return True

            if answer in ["n", "no", "nao", "não"]:
                return False

            print("Please answer y/n or s/n.")