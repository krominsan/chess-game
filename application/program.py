
# Correr com "python -m application.program"

from chess.chessMatch import ChessMatch
from chess.chessException import ChessException
from application.UI import UI

def main():

    chessMatch = ChessMatch() # Instancia um jogo de xadrez

    captured = [] # Lista para armazenar peças capturadas

    while (not chessMatch.checkMate and not chessMatch.staleMate and not chessMatch.draw):
        try:
            UI.clearScreen()
            UI.printMatch(chessMatch, captured) # Imprime o tabuleiro de jogo
            source = None
            while source is None:  # Repete até que uma entrada válida seja fornecida
                print("\nSource (or 'draw' to propose a draw): ")
                command = input().strip().lower()

                # O utilizador pode propor empate antes de escolher a origem
                if command == "draw":
                    if UI.askYesNo("Both players agree to draw? (y/n): "):
                        chessMatch.drawByAgreement()
                        break
                    else:
                        # Se não houver acordo, volta a pedir a origem
                        continue

                # Tenta converter o texto para uma posição de xadrez
                source = UI.parseChessPosition(command)
                if source is None:  # Se a entrada for inválida, volta a pedir
                    print("Invalid Input. Valid inputs are between 'a1' and 'h8' or 'draw'")

            # Se os jogadores aceitaram empate, sai do loop principal
            if chessMatch.draw:
                break

            possibleMoves = chessMatch.possibleMoves(source) # Obtém movimentos possíveis da peça

            UI.clearScreen()
            UI.printBoard(chessMatch.getPieces(), possibleMoves)

            target = None
            while target is None:
                print("\nTarget: ")
                target = UI.readChessPosition()

                if target is None:
                    print("Invalid Input. Valid inputs are between 'a1' and 'h8'")

            # Realiza o movimento da peça e guarda a peça capturada
            capturedPiece = chessMatch.performChessMove(source, target)
            if capturedPiece:
                captured.append(capturedPiece)

            # Promoção - Verifica se houve um Peão promovido
            if chessMatch.promoted is not None:
                promotion_type = input("Enter piece for promotion (B/N/R/Q): ").upper()
                while type not in ["B", "N", "R", "Q"]:
                    promotion_type = input("Invalid value! Enter piece for promotion (B/N/R/Q): ").upper()

                chessMatch.confirmPromotion(promotion_type)

        except ChessException as e:
            print(e)
            input()
        except ValueError as e:
            print(e)
            input()

    # Quando o jogo termina, mostra o estado final
    UI.clearScreen()
    UI.printMatch(chessMatch, captured)

if __name__ == "__main__":
    main()

