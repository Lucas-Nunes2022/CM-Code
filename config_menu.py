import io
import pygame
import keyboard
import variaveis
from m_pro import m_pro
from soundloader import SoundLoader

class ConfigMenu:
    def __init__(self, screen, savedata):
        self.screen = screen
        self.savedata = savedata
        self.loader = SoundLoader()
        self._menu_music_stream = None
        self.menu = m_pro("Configurações", use_sounds=True, screen=self.screen)
        self.menu.set_title_message("Configurações do jogo. Use as setas e Enter.")
        self.menu.sounds = {
            "click": self.loader.get_sound("menuclick.ogg"),
            "enter": self.loader.get_sound("menuenter.ogg"),
            "close": self.loader.get_sound("menuclose.ogg"),
        }
        self.menu.add_item("", action=self.change_player_name)
        self.menu.add_item("", action=self.toggle_ask_on_play)
        self.menu.add_item("", action=self.set_default_size)
        self.menu.add_item("", action=self.toggle_menu_music)
        self.menu.add_item("Voltar", action="back")
        self.refresh()

    def refresh(self):
        player_name = self.savedata.get_player_name() or "Não definido"
        ask_on_play = self.savedata.get_setting("ask_on_play", True)
        default_size = self.savedata.get_setting("default_size", 0)
        music_on = self.savedata.get_setting("menu_music_enabled", True)
        ask_txt = "Sim" if ask_on_play else "Não"
        size_txt = str(default_size) if default_size and default_size >= 3 else "Não definido"
        music_txt = "Ativa" if music_on else "Inativa"
        self.menu.options[0]["text"] = f"Nome do jogador: {player_name}"
        self.menu.options[0]["tts"] = f"Nome do jogador {player_name}. Pressione Enter para alterar"
        self.menu.options[1]["text"] = f"Perguntar tamanho ao jogar: {ask_txt}"
        self.menu.options[1]["tts"] = f"Perguntar tamanho ao jogar {ask_txt}"
        self.menu.options[2]["text"] = f"Tamanho padrão: {size_txt}"
        self.menu.options[2]["tts"] = f"Tamanho padrão {size_txt}"
        self.menu.options[3]["text"] = f"Música do menu: {music_txt}"
        self.menu.options[3]["tts"] = f"Música do menu {music_txt}"

    def change_player_name(self):
        font = pygame.font.SysFont(None, 40)
        new_name = keyboard.text_input(
            self.screen, font,
            "Digite o novo nome do jogador:",
            (50, 200)
        )
        
        if new_name is None:
            self.menu.speech.speak(f"Cancelado. {self.menu.options[0]['tts']}")
        elif new_name.strip() == "":
            self.menu.speech.speak(f"O nome não pode ser vazio. {self.menu.options[0]['tts']}")
        else:
            if self.savedata.set_player_name(new_name.strip()):
                self.refresh()
                self.menu.speech.speak(f"Nome alterado para {new_name}. {self.menu.options[0]['tts']}")
                
        return None

    def toggle_ask_on_play(self):
        new_val = not self.savedata.get_setting("ask_on_play", True)
        self.savedata.set_setting("ask_on_play", new_val)
        if not new_val and self.savedata.get_setting("default_size", 0) < 3:
            self.savedata.set_setting("default_size", 9)
            variaveis.qtd_linhas_colunas = 9
        self.refresh()
        status = "Sim" if new_val else "Não"
        self.menu.speech.speak(f"Perguntar tamanho ao jogar: {status}")

    def set_default_size(self):
        size_menu = m_pro("Tamanho Padrão", use_sounds=True, screen=self.screen)
        size_menu.set_title_message("Selecione o tamanho padrão do tabuleiro.")
        size_menu.sounds = self.menu.sounds

        def make_action(size):
            def action():
                self.savedata.set_setting("default_size", size)
                variaveis.qtd_linhas_colunas = size
                return "back"
            return action

        size_menu.add_item("3x3", action=make_action(3))
        size_menu.add_item("5x5", action=make_action(5))
        size_menu.add_item("10x10", action=make_action(10))
        size_menu.add_item("15x15", action=make_action(15))
        size_menu.add_item("Voltar", action="back")

        size_menu.show()
        self.refresh()
        self.menu.speech.speak(f"Tamanho padrão alterado para {self.savedata.get_setting('default_size')}")

    def toggle_menu_music(self):
        enabled = not self.savedata.get_setting("menu_music_enabled", True)
        self.savedata.set_setting("menu_music_enabled", enabled)
        
        if not enabled:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.stop()
            data = self.loader.raw_data.get("mm1.ogg")
            if data:
                try:
                    self._menu_music_stream = io.BytesIO(data)
                    pygame.mixer.music.load(self._menu_music_stream)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass
                    
        self.refresh()
        status = "ativa" if enabled else "inativa"
        self.menu.speech.speak(f"Música do menu {status}")