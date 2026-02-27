import pygame
from speech import Speech

class Dialog:
    def __init__(self):
        self.speech = Speech()
        self.message = ""
        self.title = ""
        
    def show(self, message, title="Mensagem"):
        self.message = message
        self.title = title
        
        self._speak_full_message()
        
        waiting = True
        result = False
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        result = True
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        result = False
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, 
                                      pygame.K_LEFT, pygame.K_RIGHT):
                        self._speak_full_message()
        
        return result
    
    def _speak_full_message(self):
        self.speech.speak(f"{self.title}. {self.message}")
    
    def error(self, error_message):
        return self.show(error_message, "Erro")
    
    def info(self, info_message):
        return self.show(info_message, "Informação")