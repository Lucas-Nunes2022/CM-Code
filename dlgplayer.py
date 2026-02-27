import pygame
import time

class DlgPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play_audio(self, audio_path):
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            pygame.mixer.music.fadeout(1000)
                            time.sleep(1)
                            return
                time.sleep(0.1)
        except pygame.error:
            pass
        finally:
            pygame.mixer.music.stop()