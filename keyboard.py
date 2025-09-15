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
        " ": "Space",
        ".": "Dot",
        ",": "Comma",
        "?": "Question mark",
        "!": "Exclamation mark",
        ";": "Semicolon",
        ":": "Colon",
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text

                elif event.key == pygame.K_BACKSPACE:
                    if cursor_pos > 0:
                        if select_all:
                            input_text, cursor_pos, select_all = "", 0, False
                        else:
                            input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                            cursor_pos -= 1
                        speak("Backspace")

                elif event.key == pygame.K_DELETE:
                    if cursor_pos < len(input_text):
                        if select_all:
                            input_text, cursor_pos, select_all = "", 0, False
                        else:
                            input_text = input_text[:cursor_pos] + input_text[cursor_pos+1:]
                        speak("Delete")

                elif event.key == pygame.K_LEFT and cursor_pos > 0:
                    cursor_pos -= 1
                    if cursor_pos < len(input_text):
                        speak(input_text[cursor_pos])

                elif event.key == pygame.K_RIGHT and cursor_pos < len(input_text):
                    cursor_pos += 1
                    if cursor_pos < len(input_text):
                        speak(input_text[cursor_pos])

                elif event.key == pygame.K_HOME:
                    cursor_pos = 0
                    if input_text:
                        speak(input_text[0])

                elif event.key == pygame.K_END:
                    cursor_pos = len(input_text)
                    if input_text:
                        speak(input_text[-1])

                elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    select_all = True
                    speak("Text selected")

                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    clipboard_text = pyperclip.paste()
                    input_text = input_text[:cursor_pos] + clipboard_text + input_text[cursor_pos:]
                    cursor_pos += len(clipboard_text)
                    speak(f"Text pasted: {clipboard_text}")

                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB,
                                   pygame.K_LSHIFT, pygame.K_RSHIFT,
                                   pygame.K_LCTRL, pygame.K_RCTRL,
                                   pygame.K_LALT, pygame.K_RALT):
                    pass

                else:
                    if select_all:
                        input_text, cursor_pos, select_all = event.unicode, 1, False
                    else:
                        input_text = input_text[:cursor_pos] + event.unicode + input_text[cursor_pos:]
                        cursor_pos += 1
                    speak(specials.get(event.unicode, event.unicode))

                cursor_pos = max(0, min(cursor_pos, len(input_text)))

        screen.fill((0, 0, 0))
        render_text(screen, font, prompt, pos, color)
        render_text(screen, font, input_text, (pos[0], pos[1] + 50), color)
        render_text(screen, font, "Press Enter to submit", (pos[0], pos[1] + 100), color)
        pygame.display.flip()
