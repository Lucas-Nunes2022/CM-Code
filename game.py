import os
import tempfile
import pygame
import variaveis
from speech import Speech
from core import Board
from soundloader import SoundLoader

TILE = 40
MARGIN = 20

COL_BG = (15, 15, 18)
COL_GRID = (35, 35, 40)
COL_COVER = (70, 70, 80)
COL_OPEN = (200, 200, 210)
COL_FLAG = (220, 70, 70)
COL_BOMB = (30, 30, 30)
COL_TEXT = (20, 20, 25)
COL_NUM = {
    1: (0, 90, 200),
    2: (0, 130, 90),
    3: (200, 60, 60),
    4: (120, 50, 200),
    5: (160, 60, 40),
    6: (0, 140, 140),
    7: (30, 30, 30),
    8: (100, 100, 100),
}

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.speech = Speech()
        self.loader = SoundLoader()
        self.size = max(3, int(variaveis.qtd_linhas_colunas or 9))
        self.reset_board()

        w = MARGIN * 2 + TILE * self.size
        h = MARGIN * 2 + TILE * self.size + 60
        self.surface = pygame.Surface((w, h))
        self.font = pygame.font.SysFont(None, 28)
        self.big = pygame.font.SysFont(None, 40)
        self.running = True

        self.sounds = {
            "click": self.loader.get_sound("game_click.ogg"),
            "near": self.loader.get_sound("bomba_proxima.ogg"),
            "win": self.loader.get_sound("vitoria.ogg"),
            "lose": self.loader.get_sound("derrota.ogg"),
        }

        self.music_file = "musica_partida.ogg"
        self._music_temp_path = None

    def reset_board(self):
        self.size = max(3, int(variaveis.qtd_linhas_colunas or 9))
        bombs = int(self.size * self.size * 0.35)
        self.board = Board(self.size, bombs)
        self.cursor_r, self.cursor_c = 0, 0

    def play_sound(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()

    def _prepare_music_file(self):
        """Cria o arquivo temporário apenas uma vez e reutiliza."""
        if not self._music_temp_path or not os.path.exists(self._music_temp_path):
            data = self.loader.raw_data.get(self.music_file)
            if data:
                tmp_path = os.path.join(tempfile.gettempdir(), "cm_game_music.ogg")
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
                with open(tmp_path, "wb") as f:
                    f.write(data)
                    f.flush()            # garante que o buffer Python foi escrito
                    os.fsync(f.fileno()) # força o SO a gravar em disco
                self._music_temp_path = tmp_path

    def play_music(self):
        try:
            self._prepare_music_file()
            if self._music_temp_path:
                pygame.mixer.music.load(self._music_temp_path)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def cleanup(self):
        """Chamada apenas quando sair do jogo de vez."""
        self.stop_music()
        if self._music_temp_path and os.path.exists(self._music_temp_path):
            try:
                os.remove(self._music_temp_path)
            except Exception:
                pass
        self._music_temp_path = None

    def speak_cell(self, r, c):
        cell = self.board.grid[r][c]
        pos_txt = f"Linha {r+1}, coluna {c+1}, "
        if cell.bomb and self.board.lost:
            self.speech.speak(pos_txt + "Bomba.")
            return
        if cell.flag:
            self.speech.speak(pos_txt + "Marcada.")
            return
        if not cell.revealed:
            self.speech.speak(pos_txt + "Fechada.")
            return
        if cell.adj == 0:
            self.speech.speak(pos_txt + "Vazia.")
        else:
            self.speech.speak(pos_txt + f"{cell.adj} bombas ao redor.")

    def draw_cell(self, surf, r, c):
        x = MARGIN + c * TILE
        y = MARGIN + r * TILE
        cell = self.board.grid[r][c]
        rect = pygame.Rect(x, y, TILE-1, TILE-1)

        pygame.draw.rect(surf, COL_GRID, (x, y, TILE, TILE))
        if cell.revealed:
            pygame.draw.rect(surf, COL_OPEN, rect)
            if cell.bomb:
                pygame.draw.circle(surf, COL_FLAG, rect.center, TILE//4)
                pygame.draw.circle(surf, COL_BOMB, rect.center, TILE//6)
            elif cell.adj > 0:
                num = self.big.render(str(cell.adj), True, COL_NUM.get(cell.adj, (60,60,60)))
                surf.blit(num, num.get_rect(center=rect.center))
        else:
            pygame.draw.rect(surf, COL_COVER, rect)
            if cell.flag:
                pygame.draw.polygon(
                    surf, COL_FLAG,
                    [(x+TILE*0.3, y+TILE*0.7), (x+TILE*0.3, y+TILE*0.2), (x+TILE*0.75, y+TILE*0.35)]
                )
                pygame.draw.line(surf, COL_TEXT, (x+TILE*0.3, y+TILE*0.2), (x+TILE*0.3, y+TILE*0.75), 2)

        if r == self.cursor_r and c == self.cursor_c:
            pygame.draw.rect(surf, (255, 255, 0), rect, 3)

    def draw_hud(self, surf):
        if self.board.lost:
            msg = "Você perdeu!"
        elif self.board.victory():
            msg = "Você venceu!"
        else:
            msg = "Campo Minado"

        text = self.font.render(msg, True, (235, 235, 240))
        surf.blit(text, (MARGIN, MARGIN + TILE*self.size + 12))

        if self.board.lost or self.board.victory():
            s2 = self.font.render("Enter joga novamente | ESC volta ao menu", True, (220, 200, 200))
        else:
            s2 = self.font.render("Setas movem | Enter abre | Espaço marca | ESC volta", True, (180, 180, 190))

        surf.blit(s2, (MARGIN, MARGIN + TILE*self.size + 34))

    def reveal_all(self):
        for r in range(self.size):
            for c in range(self.size):
                self.board.grid[r][c].revealed = True

    def open_cell(self, r, c):
        opened = self.board.reveal(r, c)
        if self.board.lost:
            self.reveal_all()
            self.stop_music()
            self.play_sound("lose")
            self.speech.speak("Você explodiu uma bomba. Pressione Enter para jogar novamente ou Escape para voltar ao menu.")
        elif opened:
            self.play_sound("click")
            self.speak_cell(r, c)
            if any(self.board.grid[i][j].adj > 0 for i, j in opened):
                self.play_sound("near")
        if self.board.victory():
            self.reveal_all()
            self.stop_music()
            self.play_sound("win")
            self.speech.speak("Parabéns! Você venceu. Pressione Enter para jogar novamente ou Escape para voltar ao menu.")

    def toggle_flag(self, r, c):
        self.board.toggle_flag(r, c)
        self.speech.speak("Marcada." if self.board.grid[r][c].flag else "Desmarcada.")

    def run(self):
        self.speech.speak(f"Iniciando tabuleiro {self.size} por {self.size}.")
        self.play_music()
        self.speak_cell(self.cursor_r, self.cursor_c)
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cleanup()
                        return "back"
                    if event.key == pygame.K_RETURN:
                        if self.board.lost or self.board.victory():
                            self.reset_board()
                            self.play_music()
                            self.speech.speak("Novo jogo iniciado.")
                            self.speak_cell(self.cursor_r, self.cursor_c)
                        else:
                            self.open_cell(self.cursor_r, self.cursor_c)
                    elif event.key == pygame.K_SPACE:
                        if not (self.board.lost or self.board.victory()):
                            self.toggle_flag(self.cursor_r, self.cursor_c)
                    elif event.key == pygame.K_UP and self.cursor_r > 0:
                        self.cursor_r -= 1
                        self.speak_cell(self.cursor_r, self.cursor_c)
                    elif event.key == pygame.K_DOWN and self.cursor_r < self.size-1:
                        self.cursor_r += 1
                        self.speak_cell(self.cursor_r, self.cursor_c)
                    elif event.key == pygame.K_LEFT and self.cursor_c > 0:
                        self.cursor_c -= 1
                        self.speak_cell(self.cursor_r, self.cursor_c)
                    elif event.key == pygame.K_RIGHT and self.cursor_c < self.size-1:
                        self.cursor_c += 1
                        self.speak_cell(self.cursor_r, self.cursor_c)

            self.surface.fill(COL_BG)
            for r in range(self.size):
                for c in range(self.size):
                    self.draw_cell(self.surface, r, c)
            self.draw_hud(self.surface)
            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)
        self.cleanup()
        return "back"

def start_game(screen):
    g = Game(screen)
    return g.run()
