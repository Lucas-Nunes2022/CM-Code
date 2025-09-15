import os
import tempfile
import wx
import pygame
import variaveis
from m_pro import m_pro
from soundloader import SoundLoader

class ConfigMenu:
    def __init__(self, screen, savedata):
        self.screen = screen
        self.savedata = savedata
        self.loader = SoundLoader()
        self._music_temp_path = None
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

    def _cleanup_music_temp(self):
        if self._music_temp_path and os.path.exists(self._music_temp_path):
            try:
                os.remove(self._music_temp_path)
            except Exception:
                pass
        self._music_temp_path = None

    def refresh(self):
        player_name = self.savedata.get_player_name() or "Não definido"
        ask_on_play = self.savedata.get_setting("ask_on_play", True)
        default_size = self.savedata.get_setting("default_size", 0)
        music_on = self.savedata.get_setting("menu_music_enabled", True)
        ask_txt = "Sim" if ask_on_play else "Não"
        size_txt = str(default_size) if default_size and default_size >= 3 else "Não definido"
        music_txt = "Ativa" if music_on else "Inativa"
        self.menu.options[0]["text"] = f"Nome do jogador: {player_name} (pressione Enter para alterar)"
        self.menu.options[0]["tts"] = f"Nome do jogador {player_name}. Pressione Enter para alterar"
        self.menu.options[1]["text"] = f"Perguntar tamanho ao jogar: {ask_txt}"
        self.menu.options[1]["tts"] = f"Perguntar tamanho ao jogar {ask_txt}"
        self.menu.options[2]["text"] = f"Tamanho padrão: {size_txt}"
        self.menu.options[2]["tts"] = f"Tamanho padrão {size_txt}"
        self.menu.options[3]["text"] = f"Música do menu: {music_txt}"
        self.menu.options[3]["tts"] = f"Música do menu {music_txt}"

    def change_player_name(self):
        from menu import NameDialog
        dialog = NameDialog(player_name=self.savedata.get_player_name(), modo="alterar")
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            new_name = dialog.get_name()
            if self.savedata.set_player_name(new_name):
                self.menu.speech.speak(f"Nome alterado para {new_name}")
                self.refresh()
        dialog.Destroy()
        return None

    def toggle_ask_on_play(self):
        current = self.savedata.get_setting("ask_on_play", True)
        new_val = not current
        self.savedata.set_setting("ask_on_play", new_val)
        if not new_val:
            dialog = wx.TextEntryDialog(None, "Digite o tamanho padrão (3 a 15):", "Configuração obrigatória")
            if dialog.ShowModal() == wx.ID_OK:
                try:
                    tamanho = int(dialog.GetValue())
                    if 3 <= tamanho <= 15:
                        self.savedata.set_setting("default_size", tamanho)
                        variaveis.qtd_linhas_colunas = tamanho
                        self.menu.speech.speak(f"Tamanho padrão definido para {tamanho}")
                    else:
                        wx.MessageBox("Digite um valor entre 3 e 15.", "Erro", wx.OK | wx.ICON_ERROR)
                        self.savedata.set_setting("ask_on_play", True)
                except ValueError:
                    wx.MessageBox("Digite apenas números.", "Erro", wx.OK | wx.ICON_ERROR)
                    self.savedata.set_setting("ask_on_play", True)
            else:
                self.savedata.set_setting("ask_on_play", True)
            dialog.Destroy()
        self.refresh()
        status = "Sim" if new_val else "Não"
        self.menu.speech.speak(f"Perguntar tamanho ao jogar: {status}")

    def set_default_size(self):
        dialog = wx.TextEntryDialog(None, "Digite o tamanho padrão (3 a 15):", "Configuração")
        if dialog.ShowModal() == wx.ID_OK:
            try:
                tamanho = int(dialog.GetValue())
                if 3 <= tamanho <= 15:
                    self.savedata.set_setting("default_size", tamanho)
                    variaveis.qtd_linhas_colunas = tamanho
                    self.refresh()
                    self.menu.speech.speak(f"Tamanho padrão definido para {tamanho}")
                else:
                    wx.MessageBox("Digite um valor entre 3 e 15.", "Erro", wx.OK | wx.ICON_ERROR)
            except ValueError:
                wx.MessageBox("Digite apenas números.", "Erro", wx.OK | wx.ICON_ERROR)
        dialog.Destroy()

    def toggle_menu_music(self):
        enabled = self.savedata.get_setting("menu_music_enabled", True)
        enabled = not enabled
        self.savedata.set_setting("menu_music_enabled", enabled)
        try:
            if not enabled:
                pygame.mixer.music.stop()
                self._cleanup_music_temp()
            else:
                pygame.mixer.music.stop()
                data = self.loader.raw_data.get("mm1.ogg")
                if data:
                    tmp_path = os.path.join(tempfile.gettempdir(), "cm_menu_music.ogg")
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass
                    with open(tmp_path, "wb") as f:
                        f.write(data)
                    self._music_temp_path = tmp_path
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
        except Exception:
            pass
        self.refresh()
        status = "ativa" if enabled else "inativa"
        self.menu.speech.speak(f"Música do menu {status}")
