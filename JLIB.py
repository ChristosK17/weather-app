# JLIB.py

import json
import time
from tkinter import messagebox
import better_text as bt


class ParseData:
    def __init__(self, data, type):
        """Καταχώρηση δεδομένων σε αρχείο JSON"""
        self.data = data
        self.type = type

        # Λεξικό που έχει κλειδιά none σε περίπτωση που υπάρξει σφάλμα, έτσι ώστε να μην εμφανιστούν
        # λανθασμένες καιρικές συνθήκες
        self.nonedic = {"coord": {"lon": None, "lat": None},
                 "weather": [{"id": None, "main": None, "description": None, "icon": None}],
                 "base": "stations", "main": {
                    "temp": None, "feels_like": None, "temp_min": None, "temp_max": None, "pressure": None,
                    "humidity": None},
                 "visibility": None, "wind": {"speed": None, "deg": None, "gust": None}, "clouds": {"all": None},
                 "dt": 0,
                 "sys": {"type": None, "id": None, "country": "None", "sunrise": None, "sunset": None},
                 "timezone": None,
                 "id": None, "name": "None", "cod": None}
        try:
            if self.type == "f":
                # Αν τα δεδομένα είναι υπό την μορφή αρχείου json μεταφέρονται στην μνήμη
                # με την χρήση της βιβλιοθήκης json
                with open(self.data, 'r', encoding='utf-8') as json_file:
                    self.d = json.load(json_file)
            elif self.type == "d":
                # Αν είναι λεξικό τότε φορτώνεται σε μια ξεχωριστή μεταβλητή
                self.d = eval(self.data)
            else:
                # Αλλιώς βγάζει σφάλμα
                self.d = self.nonedic
                raise IndexError
        except TypeError:
            # Αν γίνει τυπογραφικό σφάλμα ενημερώνεται ο χρήστης
            messagebox.showinfo("Προσοχή", "Τυπογραφικό σφάλμα")
            self.d = self.nonedic

        # Δεδομένου ότι όλα πήγαν καλά δημιουργούνται ξεχωριστές μεταβλητές για κάθε τιμή του λεξικού
        self.description = self.d['weather'][0]['description']
        self.temp = self.d['main']['temp']
        self.name = self.d['name']
        self.lon, self.lat = self.d['coord']['lon'], self.d['coord']['lat']
        self.humidity = self.humidity = self.d['main']['humidity']
        self.dt = time.ctime(int(self.d['dt']))
        self.icon = self.d['weather'][0]['icon']

    def simplified_forecast(self):
        """Συνάρτηση που επιστρέφει ένα κείμενο με συνοπτική περιγραφή του καιρού"""
        s = ""
        s += f"Συνοπτικά:\nΟ καιρός {bt.Improve.city_name(self.name)} σήμερα είναι {self.description} με θερμοκρασία {self.temp} °C.\n\n" if self.name != "None" else f"Δεν βρέθηκαν δεδομένα για το μέρος {self.name}"
        return s

    def detailed_forecast(self):
        """Συνάρτηση που επιστρέφει ένα κείμενο με αναλυτική περιγραφή του καιρού"""
        s = ""
        if self.name != "None":
            # Η πρόγνωση του καιρού στην πόλη είναι αυτή που αναγράφεται στην self.description
            s += f'Αναλυτικά:\nΗ κατάσταση του καιρού {bt.Improve.city_name(self.name)} είναι {self.description}. \n'

            # και έπειτα επισημαίνεται η θερμοκρασία
            s += f'Αναλυτικότερα, η θερμοκρασία είναι {self.temp} °C'

            # Αν υπάρχει δεδομένο αισθητής θερμοκρασίας αναγράφεται παρακάτω, αλλιώς παραλείπεται
            try:
                self.feels_like = self.d['main']['feels_like']
                s += f',ενώ η πραγματική αίσθηση θερμοκρασίας είναι {self.feels_like} °C. \n'
            except: s += '. \n'

            # Αν υπάρχει δεδομένο διακύμανσης θερμοκρασίας αναγράφεται παρακάτω, αλλιώς παραλείπεται
            try:
                self.temp_min = self.d['main']['temp_min']
                self.temp_max = self.d['main']['temp_max']
                Dtemp = f"θα παραμείνει σταθερή στους {self.temp_max}" if self.temp_min == self.temp_max else f"θα κυμανθεί μεταξύ {self.temp_min} °C και {self.temp_max} °C"
                s += f'Η θερμοκρασία {Dtemp}\n'
            except: pass

            # Αν υπάρχουν δεδομένα ατμοσφαιρικής πίεσης και υγρασίας αναγράφονται παρακάτω, αλλιώς παραλείπονται
            try:
                self.pressure = self.d['main']['pressure']
                s += f'Η ατμοσφαιρική πίεση είναι {self.pressure} hPa'
                try:
                    s += f' και η υγρασία {self.humidity} %. \n'
                except: s += '. \n'
            except: pass

            # Αν υπάρχει δεδομένο ορατότητας αναγράφεται παρακάτω, αλλιώς παραλείπεται
            try:
                self.visibility = float(self.d['visibility'])/1000
                s += f'Η ορατότητα είναι {self.visibility} km. \n'
            except: pass

            # Αν υπάρχουν δεδομένα ανέμου αναγράφονται παρακάτω, αλλιώς παραλείπονται
            try:
                self.speed = self.d['wind']['speed']
                s += f'Ο άνεμος κινείται με ταχύτητα {self.speed} m/s'
                try:
                    self.deg = self.d['wind']['deg']
                    s += f' και κατεύθυνση {self.deg} μοίρες'
                    try:
                        self.gust = self.d['wind']['gust']
                        s += f', ενώ ριπές φτάνουν έως και {self.gust} m/s. \n'
                    except: s += '. \n'
                except: s += '. \n'
            except: pass

            # Αν υπάρχουν δεδομένα βροχής αναγράφονται παρακάτω, αλλιώς παραλείπονται
            try:
                self.rain1h = self.d['rain']['1h']
                s += f'Ο όγκος βροχής την τελευταία 1 ώρα είναι {self.rain1h} mm'
                try:
                    self.rain3h = self.d['rain']['3h']
                    s += f', ενώ τις τελευταίες 3 ώρες {self.rain3h} mm. \n'
                except: s += '. \n'
            except: pass

            # Αν υπάρχουν δεδομένα χιονιού αναγράφονται παρακάτω, αλλιώς παραλείπονται
            try:
                self.snow1h = self.d['snow']['1h']
                s += f'Ο όγκος χιονιού την τελευταία 1 ώρα είναι {self.snow1h} mm'
                try:
                    self.snow3h = self.d['snow']['3h']
                    s += f', ενώ τις τελευταίες 3 ώρες {self.snow3h} mm. \n'
                except: s += '. \n'
            except: pass

            try: self.dt = time.ctime(int(self.d['dt']))
            except: pass

            # Αν δωθούν ώρες ανατολής και δύσης αναγράφονται παρακάτω, αλλιώς παραλείπονται
            try:
                self.sunrise = time.ctime(int(self.d['sys']['sunrise']))
                self.sunset = time.ctime(int(self.d['sys']['sunset']))
                s += f'Οι ώρες ανατολής και δύσης είναι {self.sunrise} και {self.sunset} αντίστοιχα.'
            except: pass
        else: s += f"Δεν βρέθηκαν δεδομένα για το μέρος {self.name}"
        return s

    def raw_data(self):
        """Επιστροφή λεξικού που περιέχει κάποια βασικά χαρακτηριστικά του καιρού της πόλης"""
        return {'Name': self.name, 'Latitude': self.lat, 'Longtitude': self.lon, 'Humidity': self.humidity,
                'Temperature': self.temp, 'Dt': self.dt, "Icon": self.icon}

    def my_dict(self):
        """Δημιουργία λεξικού που αναγράφει συνοπτικά καθώς και αναλυτικά τις καιρικές συνθήκες"""
        self.mydict = {"Αναλυτικά": self.detailed_forecast(), "Συνοπτικά": self.simplified_forecast()}

    def save(self):
        """Αποθήκευση καιρικών συνοπτικών και αναλυτικών καιρικών συνθηκων σε αρχείο text"""
        with open("file.txt", "w", encoding="utf-8") as f:
            f.write(self.mydict["Συνοπτικά"])
            f.write(self.mydict["Αναλυτικά"])
            f.close()

if __name__ == "main":
    s = ParseData('file.json')
    s.my_dict()
    s.save()
