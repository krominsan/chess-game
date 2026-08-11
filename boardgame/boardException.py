class BoardException(Exception):

    '''Exceção personalizada para erros do tabuleiro de xadrez'''
    def __init__(self, msg: str):
        super().__init__(msg)