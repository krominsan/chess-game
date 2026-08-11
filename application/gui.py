# Correr com "python -m application.gui"

import tkinter as tk
from tkinter import messagebox

from chess.chessMatch import ChessMatch
from chess.chessPosition import ChessPosition
from chess.chessException import ChessException
from chess.color import Color


class ChessGUI:
    """Interface gráfica do jogo de xadrez.

    O ChessMatch (módulo 'chess') é o modelo. Esta classe funciona como
    vista + controlador: nenhuma regra de xadrez é implementada aqui.
    """

    # Constantes de apresentação

    SQUARE = 72                 # lado de cada casa (px)
    COLS = "abcdefgh"

    LIGHT = "#F0D9B5"           # casa clara
    DARK = "#B58863"            # casa escura
    SELECTED = "#F7EC74"        # casa de origem selecionada
    LAST_MOVE = "#F5F682"       # origem/destino da última jogada
    MOVE_DOT = "#646F40"        # ponto verde em casa vazia jogável
    CAPTURE_RING = "#C62828"    # anel vermelho em casa capturável
    BG = "#2B2B2B"              # fundo da janela

    GLYPHS = {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"}
    PIECE_FONT = ("Segoe UI Symbol", 42)
    UI_FONT = ("Segoe UI", 12)


    # Construção da janela

    def __init__(self):
        self.match = ChessMatch()          # o Modelo do Jogo
        self.captured = []                 # peças capturadas
        self.selected = None               # ChessPosition de origem
        self.possible = None               # matriz bool de movimentos possíveis
        self.lastMove = None               # (Position, Position) da última jogada
        self.pieces = self.match.getPieces()

        self.root = tk.Tk()
        self.root.title("Xadrez — Python POO")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        # Barra de estado (turno, check, fim de jogo)
        self.status = tk.Label(self.root, font=(self.UI_FONT[0], 13, "bold"),
                               bg=self.BG, fg="#EEEEEE", anchor="w", padx=12, pady=8)
        self.status.pack(fill="x")

        # Tabuleiro
        size = self.SQUARE * 8
        self.canvas = tk.Canvas(self.root, width=size, height=size,
                                bg=self.BG, highlightthickness=0)
        self.canvas.pack(padx=12, pady=(0, 8))
        self.canvas.bind("<Button-1>", self.on_click)

        # Peças capturadas
        self.capturedLabel = tk.Label(self.root, font=self.UI_FONT,
                                      bg=self.BG, fg="#CCCCCC", anchor="w", padx=12)
        self.capturedLabel.pack(fill="x")

        # Ações
        bar = tk.Frame(self.root, bg=self.BG)
        bar.pack(pady=10)
        tk.Button(bar, text="Propor empate", font=self.UI_FONT,
                  command=self.propose_draw).pack(side="left", padx=4)
        tk.Button(bar, text="Novo jogo", font=self.UI_FONT,
                  command=self.new_game).pack(side="left", padx=4)

        self.refresh()

    def run(self):
        self.root.mainloop()


    # Interação (cliques)

    def square_to_chess(self, x, y):
        """Pixéis → ChessPosition"""
        return ChessPosition(self.COLS[x // self.SQUARE], 8 - (y // self.SQUARE))

    def piece_at(self, pos):
        # Usa a matriz cached do último refresh
        matrixPos = pos.toPosition()
        return self.pieces[matrixPos.row][matrixPos.column]

    def on_click(self, event):
        # Jogo terminado ou promoção pendente → tabuleiro bloqueado
        if self.match.checkMate or self.match.staleMate or self.match.draw:
            return
        if self.match.promoted is not None:
            return

        pos = self.square_to_chess(event.x, event.y)

        if self.selected is None:
            self.try_select(pos)                       # 1º clique: escolher origem
        elif str(self.selected) == str(pos):
            self.selected = None                       # clique na origem: desselecionar
            self.possible = None
            self.refresh()
        else:
            self.try_move(pos)                         # 2º clique: mover

    def try_select(self, pos):
        if self.piece_at(pos) is None:
            return                                     # clique em casa vazia: ignorar
        try:
            self.possible = self.match.possibleMoves(pos)
            self.selected = pos
        except ChessException as e:
            messagebox.showwarning("Origem inválida", str(e))
        self.refresh()

    def try_move(self, pos):
        try:
            captured = self.match.performChessMove(self.selected, pos)
            if captured:
                self.captured.append(captured)
            self.lastMove = (self.selected.toPosition(), pos.toPosition())
            self.selected = None
            self.possible = None
            self.refresh()

            if self.match.promoted is not None:        # promoção pendente → diálogo
                self.ask_promotion()

        except ChessException as e:
            piece = self.piece_at(pos)
            if piece is not None and piece.color == self.match.currentPlayer:
                self.try_select(pos)                   # clicar noutra peça própria: trocar seleção
            else:
                messagebox.showwarning("Jogada inválida", str(e))


    # Diálogos

    def ask_promotion(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Promover peão")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()                              # bloqueia a janela principal
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)   # obriga a escolher

        tk.Label(dialog, text="Promover peão a:", font=self.UI_FONT).pack(pady=(12, 4))
        frame = tk.Frame(dialog)
        frame.pack(pady=(0, 12), padx=12)

        color = self.match.promoted.color
        for code in ("Q", "R", "N", "B"):
            # Contraste: peça branca em botão escuro, peça preta em botão claro
            bg = "#3E3E3E" if color == Color.WHITE else "#EDEDED"
            fg = "#FFFFFF" if color == Color.WHITE else "#1F1F1F"
            tk.Button(frame, text=self.GLYPHS[code], width=3,
                      font=("Segoe UI Symbol", 30), bg=bg, fg=fg,
                      command=lambda c=code, d=dialog: self.confirm_promotion(c, d)
                      ).pack(side="left", padx=4)

        dialog.wait_window()                           # bloqueia até à escolha

    def confirm_promotion(self, code, dialog):
        dialog.destroy()
        self.match.confirmPromotion(code)
        self.refresh()

    def propose_draw(self):
        if messagebox.askyesno("Empate por acordo", "Ambos os jogadores aceitam o empate?"):
            self.match.drawByAgreement()
            self.refresh()

    def new_game(self):
        self.match = ChessMatch()
        self.captured = []
        self.selected = None
        self.possible = None
        self.lastMove = None
        self.refresh()


    # Renderização

    def refresh(self):
        self.canvas.delete("all")
        self.pieces = self.match.getPieces()
        selectedPos = self.selected.toPosition() if self.selected else None

        for i in range(8):
            for j in range(8):
                x0, y0 = j * self.SQUARE, i * self.SQUARE
                x1, y1 = x0 + self.SQUARE, y0 + self.SQUARE
                isLight = (i + j) % 2 == 0
                fill = self.LIGHT if isLight else self.DARK

                # Destaque da última jogada (origem e destino)
                if self.lastMove:
                    src, tgt = self.lastMove
                    if (src.row, src.column) == (i, j) or (tgt.row, tgt.column) == (i, j):
                        fill = self.LAST_MOVE

                # A seleção sobrepõe-se ao destaque
                if selectedPos and (selectedPos.row, selectedPos.column) == (i, j):
                    fill = self.SELECTED

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

                # Coordenadas: números na 1ª coluna, letras na última linha
                coordColor = self.DARK if isLight else self.LIGHT
                if j == 0:
                    self.canvas.create_text(x0 + 9, y0 + 10, text=str(8 - i),
                                            font=(self.UI_FONT[0], 10, "bold"), fill=coordColor)
                if i == 7:
                    self.canvas.create_text(x1 - 9, y1 - 9, text=self.COLS[j],
                                            font=(self.UI_FONT[0], 10, "bold"), fill=coordColor)

                # Indicadores de movimentos possíveis
                if self.possible and self.possible[i][j]:
                    if self.pieces[i][j] is None:
                        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                        self.canvas.create_oval(cx - 9, cy - 9, cx + 9, cy + 9,
                                                fill=self.MOVE_DOT, outline="")
                    else:
                        self.canvas.create_oval(x0 + 4, y0 + 4, x1 - 4, y1 - 4,
                                                outline=self.CAPTURE_RING, width=4)

                piece = self.pieces[i][j]
                if piece is not None:
                    self.draw_piece((x0 + x1) // 2, (y0 + y1) // 2, piece)

        self.update_status()
        self.update_captured()

    def draw_piece(self, cx, cy, piece):
        glyph = self.GLYPHS[str(piece)]
        fill = "#FFFFFF" if piece.color == Color.WHITE else "#1F1F1F"

        self.canvas.create_text(cx + 2, cy + 2, text=glyph, font=self.PIECE_FONT, fill="#3A3A3A")
        self.canvas.create_text(cx, cy, text=glyph, font=self.PIECE_FONT, fill=fill)

    def update_status(self):
        if self.match.checkMate:
            text = f"CHECKMATE! Vencedor: {self.match.currentPlayer.value}"
        elif self.match.staleMate:
            text = "STALEMATE — Empate"
        elif self.match.draw:
            text = f"EMPATE — {self.match.drawReason}"
        else:
            text = f"Turno {self.match.turn} · a jogar: {self.match.currentPlayer.value}"
            if self.match.check:
                text += "   ·   CHECK!"
        self.status.config(text=text)

    def update_captured(self):
        white = " ".join(self.GLYPHS[str(p)] for p in self.captured if p.color == Color.WHITE)
        black = " ".join(self.GLYPHS[str(p)] for p in self.captured if p.color == Color.BLACK)
        self.capturedLabel.config(text=f"Capturadas — Brancas: {white}    Pretas: {black}")


def main():
    ChessGUI().run()


if __name__ == "__main__":
    main()