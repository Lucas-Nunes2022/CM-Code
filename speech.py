import ctypes
import threading
import win32com.client
import psutil
import time

class Speech:
    def __init__(self):
        self.speech_lock = threading.Lock()
        self.NVDA_AVAILABLE = self._load_nvda()
        self.nvda_active = False
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self._update_nvda_status()
        threading.Thread(target=self._monitor_nvda, daemon=True).start()

    def _load_nvda(self):
        try:
            self.nvda = ctypes.cdll.LoadLibrary('./nvdaControllerClient.dll')
            self.nvda.nvdaController_speakText.restype = None
            self.nvda.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
            return True
        except OSError:
            return False

    def _is_nvda_running(self):
        for process in psutil.process_iter(attrs=['name']):
            if process.info['name'] and 'nvda.exe' in process.info['name'].lower():
                return True
        return False

    def _update_nvda_status(self):
        self.nvda_active = self.NVDA_AVAILABLE and self._is_nvda_running()

    def _monitor_nvda(self):
        while True:
            self._update_nvda_status()
            time.sleep(5)

    def speak_with_sapi(self, text):
        if not self.speaker:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")

        def speak_async():
            with self.speech_lock:
                try:
                    self.speaker.Speak(text, 1)
                except Exception:
                    self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    self.speaker.Speak(text, 1)

        self.speaker.Speak("", 2)
        threading.Thread(target=speak_async, daemon=True).start()

    def speak(self, text):
        if not text:
            return
        if self.nvda_active:
            try:
                self.nvda.nvdaController_speakText(ctypes.c_wchar_p(text))
            except Exception:
                self.speak_with_sapi(text)
        else:
            self.speak_with_sapi(text)
