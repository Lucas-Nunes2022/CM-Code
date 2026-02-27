import pygame
import variaveis
from menu import Menu
from game import start_game

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.display.set_caption(f"{variaveis.nome_do_jogo} - v{variaveis.versao}")
    screen = pygame.display.set_mode((800, 700))

    menu = Menu(screen)

    running = True
    while running:
        result = menu.show_menu()
        if result == "start_game":
            r = start_game(screen)
            if r == "exit":
                running = False
        elif result == "exit" or result is None:
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()