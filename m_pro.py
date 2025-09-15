import pygame
from speech import Speech
from soundloader import SoundLoader

class m_pro:
    def __init__(self, title="Menu", use_sounds=False, screen=None):
        if screen is None:
            raise ValueError("A instância de 'screen' deve ser fornecida!")

        self.speech = Speech()
        self.title = title
        self.use_sounds = use_sounds
        self.screen = screen

        self.options = []
        self.selected = 0
        self.sounds = {}
        self.title_message = "Selecione uma opção com as setas e pressione Enter para selecionar."
        self.background_music = None
        self.music_volume = 0.7
        self.fade_duration = 2000

        self.title_font = pygame.font.SysFont(None, 48)
        self.option_font = pygame.font.SysFont(None, 36)

        self.loader = SoundLoader()

    def set_background_music(self, music_file, volume=0.7):
        self.background_music = music_file
        self.music_volume = volume
        if self.background_music:
            try:
                sound = self.loader.data[self.background_music]
                raw = pygame.mixer.Sound(file=self.loader.get_file(self.background_music))
                pygame.mixer.music.load(self.loader.get_file(self.background_music))
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Erro ao carregar música {self.background_music}: {e}")

    def stop_background_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(self.fade_duration)

    def load_sounds(self, sound_dict):
        for sound_name, sound_file in sound_dict.items():
            try:
                self.sounds[sound_name] = self.loader.get_sound(sound_file)
            except Exception as e:
                print(f"Erro ao carregar som {sound_file}: {e}")
                self.sounds[sound_name] = None

    def set_title_message(self, message):
        self.title_message = message

    def add_item(self, text, tts_text=None, action=None, submenu=None):
        if tts_text is None:
            tts_text = text
        self.options.append({
            "text": text,
            "tts": tts_text,
            "action": action,
            "submenu": submenu
        })

    def play_sound(self, sound_name):
        if self.use_sounds and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def handle_navigation(self, key):
        if key in [pygame.K_UP, pygame.K_LEFT]:
            if self.selected > 0:
                self.selected -= 1
                self.speech.speak(self.options[self.selected]["tts"])
                self.play_sound("click")
        elif key in [pygame.K_DOWN, pygame.K_RIGHT]:
            if self.selected < len(self.options) - 1:
                self.selected += 1
                self.speech.speak(self.options[self.selected]["tts"])
                self.play_sound("click")
        elif key == pygame.K_HOME:
            if self.selected != 0:
                self.selected = 0
                self.speech.speak(self.options[self.selected]["tts"])
                self.play_sound("click")
        elif key == pygame.K_END:
            last = len(self.options) - 1
            if self.selected != last:
                self.selected = last
                self.speech.speak(self.options[self.selected]["tts"])
                self.play_sound("click")
        else:
            return False
        return True

    def handle_selection(self):
        self.play_sound("enter")
        selected_option = self.options[self.selected]

        if selected_option["submenu"]:
            result = selected_option["submenu"].show()
            if result == "back":
                self.selected = 0
                self.speech.speak(self.title_message)
                if self.options:
                    self.speech.speak(self.options[self.selected]["tts"])
                self.play_sound("click")
                return ("back", "submenu")
            return (result, "submenu")

        if selected_option["action"]:
            if selected_option["action"] == "exit":
                self.stop_background_music()
                pygame.time.wait(self.fade_duration)
                return ("exit", "action")
            if selected_option["action"] == "back":
                return ("back", "action")
            if isinstance(selected_option["action"], str):
                return (selected_option["action"], "action")
            else:
                r = selected_option["action"]()
                return (r, "action")

        return (None, "action")

    def show(self, is_main_menu=False):
        self.speech.speak(self.title_message)
        if self.options:
            self.speech.speak(self.options[self.selected]["tts"])

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_background_music()
                    pygame.quit()
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if self.handle_navigation(event.key):
                        continue

                    if event.key in [pygame.K_PAGEUP, pygame.K_PAGEDOWN]:
                        delta = 0.1 if event.key == pygame.K_PAGEUP else -0.1
                        self.music_volume = max(0.0, min(1.0, self.music_volume + delta))
                        try:
                            pygame.mixer.music.set_volume(self.music_volume)
                        except Exception:
                            pass

                    elif event.key == pygame.K_RETURN:
                        result, source = self.handle_selection()
                        if result == "back" and source == "submenu":
                            continue
                        if result is not None:
                            return result

                    elif event.key == pygame.K_ESCAPE:
                        self.play_sound("close")
                        if is_main_menu:
                            self.stop_background_music()
                            pygame.time.wait(self.fade_duration)
                            return "exit"
                        else:
                            return "back"

            self.screen.fill((0, 0, 0))
            title_text = self.title_font.render(self.title, True, (255, 255, 255))
            self.screen.blit(title_text, (50, 20))

            for i, option in enumerate(self.options):
                color = (255, 255, 255) if i == self.selected else (128, 128, 128)
                text = self.option_font.render(option["text"], True, color)
                self.screen.blit(text, (50, 70 + i * 40))

            pygame.display.flip()
