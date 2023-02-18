# TTS.py

from gtts import gTTS
import playsound
import os


class Speak:
    def __init__(self, text, language):
        """Όταν καλείται η κλάση με παραμέτρους το κείμενο και την γλώσσα
        η gTTS το απαγγέλει στα ελληνικά"""
        self.text = text
        self.language = language
        output = gTTS(text=self.text, lang=self.language, slow=False)
        try:
            # Διαγραφή προηγουμένου αρχείου ομιλίας, εφόσον υπάρχει
            os.remove("output.mp3")
        except:
            pass

        # Αποθήκευση και εκτέλεση αρχείου ομιλίας
        output.save("output.mp3")
        playsound.playsound("output.mp3")


if __name__ == "__main__":
    Speak("Γειά", "el")
