import pygame
import ctypes
import pyperclip

pygame.init()

try:
    nvda = ctypes.cdll.LoadLibrary("./nvdaControllerClient.dll")
    nvda.nvdaController_speakText.restype = None
    nvda.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
except OSError:
    nvda = None

def speak(text: str):
    if nvda and text:
        try:
            nvda.nvdaController_speakText(ctypes.c_wchar_p(text))
        except Exception as e:
            print(f"Erro NVDA: {e}")

def render_text(screen, font, text, pos, color=(255, 255, 255)):
    surface = font.render(text, True, color)
    screen.blit(surface, pos)

def text_input(screen, font, prompt, pos, color=(255, 255, 255)):
    input_text = ""
    cursor_pos = 0
    select_all = False
    speak(prompt)

    specials = {
        " ": "Espaço",
        ".": "Ponto",
        ",": "Vírgula",
        "?": "Interrogação",
        "!": "Exclamação",
        ";": "Ponto e vírgula",
        ":": "Dois pontos",
        "\n": "Nova linha",
        "\\": "Barra invertida",
        "/": "Barra",
        "-": "Hífen",
        "_": "Underline",
        "@": "Arroba"
    }

    def speak_char_at_cursor():
        if cursor_pos < len(input_text):
            char = input_text[cursor_pos]
            speak(specials.get(char, char))
        else:
            speak("Em branco")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    speak("Cancelado")
                    return None

                elif event.key == pygame.K_RETURN:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        input_text = input_text[:cursor_pos] + "\n" + input_text[cursor_pos:]
                        cursor_pos += 1
                        speak("Nova linha")
                    else:
                        return input_text

                elif event.key == pygame.K_BACKSPACE:
                    if cursor_pos > 0:
                        if select_all:
                            input_text, cursor_pos, select_all = "", 0, False
                            speak("Texto apagado")
                        else:
                            deleted_char = input_text[cursor_pos-1]
                            input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                            cursor_pos -= 1
                            speak(specials.get(deleted_char, deleted_char))
                            
                        if not input_text:
                            speak("Em branco")

                elif event.key == pygame.K_DELETE:
                    if cursor_pos < len(input_text):
                        if select_all:
                            input_text, cursor_pos, select_all = "", 0, False
                            speak("Texto apagado")
                        else:
                            deleted_char = input_text[cursor_pos]
                            input_text = input_text[:cursor_pos] + input_text[cursor_pos+1:]
                            speak(specials.get(deleted_char, deleted_char))
                            
                        if not input_text:
                            speak("Em branco")

                elif event.key == pygame.K_LEFT:
                    if cursor_pos > 0:
                        cursor_pos -= 1
                    speak_char_at_cursor()

                elif event.key == pygame.K_RIGHT:
                    if cursor_pos < len(input_text):
                        cursor_pos += 1
                    speak_char_at_cursor()

                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    speak(prompt)

                elif event.key == pygame.K_HOME:
                    cursor_pos = 0
                    speak_char_at_cursor()

                elif event.key == pygame.K_END:
                    cursor_pos = len(input_text)
                    speak_char_at_cursor()

                elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    select_all = True
                    speak("Texto selecionado")

                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    try:
                        clipboard_text = pyperclip.paste()
                        input_text = input_text[:cursor_pos] + clipboard_text + input_text[cursor_pos:]
                        cursor_pos += len(clipboard_text)
                        speak(f"Colado")
                    except Exception:
                        speak("Área de transferência vazia")

                elif event.key in (pygame.K_TAB, pygame.K_LSHIFT, pygame.K_RSHIFT,
                                   pygame.K_LCTRL, pygame.K_RCTRL,
                                   pygame.K_LALT, pygame.K_RALT):
                    pass

                elif event.unicode:
                    if select_all:
                        input_text, cursor_pos, select_all = event.unicode, 1, False
                    else:
                        input_text = input_text[:cursor_pos] + event.unicode + input_text[cursor_pos:]
                        cursor_pos += 1
                    speak(specials.get(event.unicode, event.unicode))

                cursor_pos = max(0, min(cursor_pos, len(input_text)))

        screen.fill((0, 0, 0))
        render_text(screen, font, prompt, pos, color)
        
        y_offset = pos[1] + 50
        for line in input_text.split("\n"):
            render_text(screen, font, line, (pos[0], y_offset), color)
            y_offset += 30
            
        render_text(screen, font, "Enter confirma | ESC cancela", (pos[0], y_offset + 20), (150, 150, 150))
        pygame.display.flip()