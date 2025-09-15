import variaveis
from m_pro import m_pro
import pygame
import wx
from savedata import SaveData
from config_menu import ConfigMenu
from soundloader import SoundLoader

class NameDialog(wx.Dialog):
    def __init__(self, player_name="", modo="boasvindas"):
        super().__init__(None, title="Campo Minado")
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        if modo == "boasvindas":
            sizer.Add(wx.StaticText(panel, label=f'Bem-vindo ao {variaveis.nome_do_jogo}, versão {variaveis.versao}!'),
                      0, wx.ALL | wx.CENTER, 10)
            instruction = "Por favor, digite seu nome:"
        else:
            instruction = "Digite o novo nome do jogador:"
        sizer.Add(wx.StaticText(panel, label=instruction), 0, wx.ALL | wx.CENTER, 10)
        self.name_input = wx.TextCtrl(panel, value=player_name)
        sizer.Add(self.name_input, 0, wx.ALL | wx.EXPAND, 10)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn, cancel_btn = wx.Button(panel, label="&OK"), wx.Button(panel, label="&Cancelar")
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        panel.SetSizer(sizer)
        sizer.Fit(self)

    def on_ok(self, event):
        if self.name_input.GetValue().strip():
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox("Por favor, digite um nome para continuar.", "Erro", wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def get_name(self):
        return self.name_input.GetValue().strip()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.savedata = SaveData()
        self.loader = SoundLoader()
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
            self.main_menu.speech.speak(
                f"Iniciando jogo com tabuleiro {default_size} por {default_size}"
            )
            return "start_game"
        else:
            choices = ["3x3", "5x5", "10x10", "Personalizado"]
            dialog = wx.SingleChoiceDialog(
                None, "Escolha o tamanho do tabuleiro:", "Configuração", choices
            )
            if dialog.ShowModal() == wx.ID_OK:
                escolha = dialog.GetStringSelection().strip()
                if not escolha:
                    wx.MessageBox(
                        "Você deve selecionar um tamanho de tabuleiro para continuar.",
                        "Erro", wx.OK | wx.ICON_ERROR
                    )
                    dialog.Destroy()
                    play_menu_sound("close")
                    return None

                play_menu_sound("click")
                if escolha == "3x3":
                    variaveis.qtd_linhas_colunas = 3
                elif escolha == "5x5":
                    variaveis.qtd_linhas_colunas = 5
                elif escolha == "10x10":
                    variaveis.qtd_linhas_colunas = 10
                elif escolha == "Personalizado":
                    tamanho_dialog = wx.TextEntryDialog(
                        None, "Digite o tamanho (3 a 15):", "Personalizado"
                    )
                    if tamanho_dialog.ShowModal() == wx.ID_OK:
                        valor = tamanho_dialog.GetValue().strip()
                        if not valor:
                            wx.MessageBox(
                                "Digite um valor numérico para o tamanho.",
                                "Erro", wx.OK | wx.ICON_ERROR
                            )
                            tamanho_dialog.Destroy()
                            dialog.Destroy()
                            play_menu_sound("close")
                            return None
                        try:
                            tamanho = int(valor)
                            if 3 <= tamanho <= 15:
                                variaveis.qtd_linhas_colunas = tamanho
                                play_menu_sound("enter")
                            else:
                                wx.MessageBox(
                                    "Digite um valor entre 3 e 15.",
                                    "Erro", wx.OK | wx.ICON_ERROR
                                )
                                return None
                        except ValueError:
                            wx.MessageBox(
                                "Digite apenas números.", "Erro", wx.OK | wx.ICON_ERROR
                            )
                            return None
                    else:
                        # Cancel no personalizado
                        tamanho_dialog.Destroy()
                        dialog.Destroy()
                        play_menu_sound("close")
                        return None
                    tamanho_dialog.Destroy()
                dialog.Destroy()
                self.main_menu.speech.speak(
                    f"Iniciando jogo com tabuleiro {variaveis.qtd_linhas_colunas} "
                    f"por {variaveis.qtd_linhas_colunas}"
                )
                return "start_game"
            else:
                dialog.Destroy()
                play_menu_sound("close")
                return None

    def show_menu(self):
        if not self.savedata.get_player_name():
            wx.Yield()
            dialog = NameDialog(modo="boasvindas")
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                player_name = dialog.get_name()
                self.savedata.set_player_name(player_name)
                self.main_menu.speech.speak(f"Nome definido como {player_name}")
                self.main_menu = self.create_main_menu()
                self.config_menu = ConfigMenu(self.screen, self.savedata).menu
                self.main_menu.add_item("Iniciar Jogo", action=self.start_game)
                self.main_menu.add_item("Configurações", submenu=self.config_menu)
                self.main_menu.add_item("Sair", action="exit")
            dialog.Destroy()
            if result != wx.ID_OK:
                return "exit"

        self.main_menu.speech.speak(self.main_menu.title_message)
        if self.savedata.get_setting("menu_music_enabled", True):
            try:
                with self.loader.get_file("mm1.ogg") as music_path:
                    if music_path:
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.set_volume(0.7)
                        pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Erro ao tocar música do menu: {e}")
        else:
            try:
                pygame.mixer.music.fadeout(500)  # <<< suaviza em 500ms
            except Exception:
                pass
        return self.main_menu.show(is_main_menu=True)
