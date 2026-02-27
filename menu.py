import io
import pygame
import keyboard
import variaveis
from m_pro import m_pro
from savedata import SaveData
from config_menu import ConfigMenu
from soundloader import SoundLoader

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.savedata = SaveData()
        self.loader = SoundLoader()
        self._menu_music_stream = None 
        self.main_menu = self.create_main_menu()
        self.config_menu = ConfigMenu(self.screen, self.savedata).menu
        self.main_menu.add_item("Iniciar Jogo", action=self.start_game)
        self.main_menu.add_item("Configurações", submenu=self.config_menu)
        self.main_menu.add_item("Sair", action="exit")

    def create_main_menu(self):
        menu = m_pro("Campo Minado", use_sounds=True, screen=self.screen)
        menu.set_title_message(
            "Menu principal. Use as setas para selecionar e pressione Enter para confirmar. "
            "Use as teclas Page Up e Page Down para ajustar o volume da música."
        )
        menu.sounds = {
            "click": self.loader.get_sound("menuclick.ogg"),
            "enter": self.loader.get_sound("menuenter.ogg"),
            "close": self.loader.get_sound("menuclose.ogg")
        }
        return menu

    def start_game(self):
        ask_on_play = self.savedata.get_setting("ask_on_play", True)
        default_size = self.savedata.get_setting("default_size", 0)

        def play_menu_sound(name):
            s = self.loader.get_sound(name)
            if s:
                s.play()

        if not ask_on_play and default_size >= 3:
            variaveis.qtd_linhas_colunas = default_size
            play_menu_sound("enter")
            self.main_menu.speech.speak(f"Iniciando jogo com tabuleiro {default_size} por {default_size}")
            pygame.mixer.music.fadeout(800)
            pygame.time.wait(800)
            return "start_game"

        size_menu = m_pro("Escolha o tamanho", use_sounds=True, screen=self.screen)
        size_menu.set_title_message("Escolha o tamanho do tabuleiro para esta partida.")
        size_menu.sounds = self.main_menu.sounds

        def make_action(size):
            def action():
                variaveis.qtd_linhas_colunas = size
                return "start_game"
            return action

        size_menu.add_item("3x3", action=make_action(3))
        size_menu.add_item("5x5", action=make_action(5))
        size_menu.add_item("10x10", action=make_action(10))
        size_menu.add_item("15x15", action=make_action(15))
        size_menu.add_item("Voltar", action="back")

        result = size_menu.show()
        if result == "start_game":
            play_menu_sound("enter")
            self.main_menu.speech.speak(f"Iniciando jogo com tabuleiro {variaveis.qtd_linhas_colunas} por {variaveis.qtd_linhas_colunas}")
            pygame.mixer.music.fadeout(800)
            pygame.time.wait(800)
            return "start_game"
        else:
            play_menu_sound("close")
            return None

    def play_menu_music(self):
        if self.savedata.get_setting("menu_music_enabled", True):
            data = self.loader.raw_data.get("mm1.ogg")
            if data:
                try:
                    self._menu_music_stream = io.BytesIO(data)
                    pygame.mixer.music.load(self._menu_music_stream)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Erro música: {e}")
        else:
            try:
                pygame.mixer.music.fadeout(500)
            except Exception:
                pass

    def show_menu(self):
        if not self.savedata.get_player_name():
            font = pygame.font.SysFont(None, 40)
            player_name = keyboard.text_input(
                self.screen, font, 
                "Bem-vindo! Digite seu nome:", 
                (50, 200)
            )
            if player_name and player_name.strip():
                self.savedata.set_player_name(player_name.strip())
                self.main_menu.speech.speak(f"Nome definido como {player_name}")
                self.main_menu = self.create_main_menu()
                self.config_menu = ConfigMenu(self.screen, self.savedata).menu
                self.main_menu.add_item("Iniciar Jogo", action=self.start_game)
                self.main_menu.add_item("Configurações", submenu=self.config_menu)
                self.main_menu.add_item("Sair", action="exit")
            else:
                return "exit"

        self.main_menu.speech.speak(self.main_menu.title_message)
        self.play_menu_music()
        return self.main_menu.show(is_main_menu=True)