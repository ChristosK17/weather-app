# data_bible.py

import urllib, urllib.request, urllib.error, socket, os, ssl, webbrowser
from dateutil import parser
from datetime import datetime
from tkinter import messagebox

class GetData:
    loading = 0

    # Αποθήκευση του κωδικού API και του URL για να είναι εφικτή η λήψη δεδομένων από το MyWeather
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=el"
    API = "a7c502158f1ab652bb2ac41c6de4bc9f"

    # Αποθήκευση των πόλεων του cities.txt σε λίστα cities
    with open("cities.txt", "r", encoding="utf-8") as f:
        data = f.read()
        cities = data.split(",")
        try: cities.remove("")
        except: pass

    jdir= "JSONforecasts"
    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    crash = False
    socket.setdefaulttimeout(10)

    def __init__(self):
        """Δημιουργία φακέλου JSONforecasts εφόσον δεν υπάρχει"""
        try: os.mkdir(self.jdir)
        except: pass

    @staticmethod
    def set_ssl():
        """Η Python όταν κάνει request κάποια δεδομένα από το internet, προσπαθεί να κάνει access ένα database
        (το οποίο συνήθως υπάρχει σε ένα σύστημα) που έχει όλα τα πρωτόκολλα. Σε μερικά παλιά συστήματα δεν υπάρχει
        τέτοια τοποθεσία με αποτέλεσμα κατά την διάρκεια του handshake με τον ιστότοπο να σηκώνει error.
        Άρα για να λυθεί αυτό ορίζεται ένα καινούριο μονοπάτι προσθέτοντας μία νέα συνάρτηση
        ssl._create_default_https_context, η οποία είναι ίδια με το ssl.create_default_context. Έτσι, το http.client
        μπορεί να αντικαταστήσει την χρήση του ssl._create_stdlib_context με το ssl._create_default_https_context
        και να ανακτήσει επιτυχώς τα δεδομένα.

        ΠΡΟΣΟΧΗ: Η μέθοδος αυτή παρακάμπτει τα πρωτόκολλα ασφάλειας με αποτέλεσμα να δημιουργεί κενά ασφάλειας για τον
        υπολογιστή του χρήστη. Σε αυτήν την εφαρμογή δεν υπάρχει πρόβλημα ασφάλειας αλλά καλό είναι αυτή η μέθοδος
        να χρησιμοποιείται με ιδιαίτερη προσοχή σε άλλα προγράμματα."""
        global crash
        answer = messagebox.askquestion("Προσοχή", """Αυτή η καθογήγηση-διαδικασία απευθύνεται κυρίως σε διαχειρηστές συστημάτων (system administrators), οι οποίοι δουλεύουν με νεότερες εκδόσεις της Python, οι οποίες εφαρμόζουν το ίδιο PEP σε παλαιότερα περιβάλλοντα που δεν υποστηρίζουν επαλήθευση πιστοποιητικού σε συνδέσεις HTTPS (certificate verification on HTTPS connections).\n Θέλετε να γίνουν οι απαραίτητες αλλαγές? Αν όχι δυστυχώς είναι αδύνατη η ανάκτηση δεδομένων καιρού.""",)
        webbrowser.open("https://www.python.org/dev/peps/pep-0476/")
        if answer == "yes":
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError as e:
                messagebox.showinfo("Προσοχή", "Η έκδοση της Python δεν επαληθεύει τα πιστοποιητικά HTTPS από προεπιλογή.")
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
        else:
            messagebox.showinfo("Προσοχή", "Αδυναμία ανάκτησης δεδομένων")

    def get_data(self):
        """Συνάρτηση που κατεβάζει δεδομένα από το API"""
        crash = False
        lista = next(os.walk(os.path.join(self.jdir, '.')))[2]

        # Ελέγχει αν υπάρχει JSON αρχείο για τις πόλεις του cities.txt
        # Αν δεν υπάρχει το δημιουργεί
        for city in self.cities:
            if "{}-forecast-{}.json".format(city, str(datetime.now().date())) not in lista:
                try:
                    # Request στο API και συγγραφή αρχείου JSON
                    raw_data = urllib.request.urlopen(urllib.request.Request(self.url.format(city, self.API), headers=self.headers))
                    data = raw_data.read().decode(raw_data.headers.get_content_charset())
                    with open(os.path.join(self.jdir, "{}-forecast-{}".format(city, str(datetime.now().date())+".json")), "w", encoding=raw_data.headers.get_content_charset()) as f:
                        f.write(data)
                except urllib.error.HTTPError as e:
                    # φάλμα πρωτόκολλου μεταφοράς υπερκειμένου
                    messagebox.showinfo("HTTP ERROR", "Σφάλμα πρωτόκολλου μεταφοράς υπερκειμένου")
                    break
                except urllib.error.URLError as e:
                    # Αποτυχία σύνδεσης στην ιστοσελίδα
                    if "<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed" in e:
                        self.root.destroy()
                        if crash:
                            break
                else: pass

    def get_data_by_coords(self, LAT, LON):
        """Αναζήτηση καιρικών συνθηκών για ζητούμενη πόλη με γεωγραφικές συντεταγμένες"""
        self.LAT = LAT
        self.LON = LON
        url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric&lang=el"
        try:
            # Ανάκτηση δεδομένων καιρού
            with urllib.request.urlopen(url.format(LAT, LON, self.API)) as forecast:
                return forecast.read().decode("utf-8")
        except urllib.error.URLError as e:
            # Αποτυχία σύνδεσης στην ιστοσελίδα
            if "<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed" in e:
                my_data.set_ssl()
            else:
                messagebox.showinfo("Αποτυχία σύνδεσης", " Αποτυχία σύνδεσης στην ιστοσελίδα λόγω:\n {}".format(e.reason))
        except urllib.error.HTTPError as e:
            # Σφάλμα πρωτόκολλου μεταφοράς υπερκειμένου
            messagebox.showinfo("HTTP ERROR", f"Σφάλμα πρωτόκολλου μεταφοράς υπερκειμένου\n {e.code}")
        except Exception as e:
            # Άλλο σφάλμα
            messagebox.showinfo("Σφάλμα", e)

    def get_data_by_name(self, name):
        """Αναζήτηση καιρικών συνθηκών για ζητούμενη πόλη με όνομα"""
        lista = next(os.walk(os.path.join(self.jdir, '.')))[2]

        # Αν υπάρχει ήδη JSON αρχείο για την ζητούμενη πόλη, ανακτούνται πληροφορίες από το αρχείο
        # και όχι από το API
        if "{}-forecast-{}.json".format(name, str(datetime.now().date())) in lista:
            with open("JSONforecasts/{}-forecast-{}.json".format(name, str(datetime.now().date())), "r", encoding="utf-8") as f:
                return f.read()
        else:
            self.name = name
            try:
                # Ανάκτηση δεδομένων καιρού
                forecast = urllib.request.urlopen(self.url.format(name, self.API))
                return forecast.read().decode("utf-8")
            except urllib.error.HTTPError:
                # Σφάλμα πρωτόκολλου μεταφοράς υπερκειμένου
                messagebox.showinfo("HTTP ERROR", "Σφάλμα πρωτόκολλου μεταφοράς υπερκειμένου")
            except urllib.error.URLError as e:
                # Αποτυχία σύνδεσης στην ιστοσελίδα
                if "<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed" in e:
                    GetData.set_ssl()
                else:
                    messagebox.showinfo("Αποτυχία σύνδεσης", "Αποτυχία σύνδεσης στην ιστοσελίδα λόγω:\n {}".format(e.reason))
            except NameError as e:
                # Λανθασμένο όνομα πόλης
                messagebox.showinfo("Αποτυχία ανάκτησης δεδομένων", "Αποτυχία ανάκτησης δεδομένων λόγω:\n {}".format(e.reason))
            except Exception as e:
                # Άλλο σφάλμα
                messagebox.showinfo("Σφάλμα", e)


class Checker:
    def __init__(self, filename, last_up_to=30):
        self.filename = filename
        self.last_up_to = last_up_to

        # Ελέγχει την ημερομηνία των αρχείων JSON
        # Αν η ημερομηνία τους είναι μια μέρα νωρίτερα ή παραπάνω διαγράφονται
        if not ".json" in filename:
            pass
        else:
            try:
                filename = filename.replace(".json", "")
            except: pass
            try:
                exp_date = int(str(datetime.now().date() - parser.parse(filename[-10:].replace("-", " ")).date())[:2])
                if exp_date > self.last_up_to:
                    os.remove(os.path.join(GetData.jdir, "{}.json".format(filename)))
            except: pass


if __name__ == "__main__":
    my_data = GetData()
    lista = next(os.walk(os.path.join(my_data.jdir, '.')))[2]
    for file in lista:
        Checker(file)
    try:
        my_data.get_data()
    except:
        my_data.set_ssl()
        my_data.get_data()
