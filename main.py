# main.py

from tkinter import *
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import os
from tkinter import messagebox
import data_bible
import collapsible_menu
import TTS
import JLIB as jlib
import sqlite_demo as SQD
from playsound import playsound
from multiprocessing import Process



class GUI:
    # Φόρτωμα λεξικού που μεταφράζει πόλεις από greeklish σε ελληνικά
    with open("cities_dict.txt", "r", encoding="utf-8") as cities:
        cities = cities.read()
        cities = eval(cities)

    OPTIONS = [i for i in cities.values()]
    available_cities = []
    done = True
    x_old, y_old = 0, 0
    jdir = "JSONforecasts"

    def __init__(self, root):
        # self.variable για να γίνει global
        self.root = root
        self.x = 0
        self.y = 0
        self.offset = 10
        self.images = []
        
        # Set bg color, lock resizability, give title and set appropriate window size
        root.configure(background='#e6e3e3')
        root.resizable(False, False)
        root.title("Ο καιρός της Ελλάδας σήμερα")
        screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
        inch = ((screen_w*0.0104166667)**2 + (screen_h*0.0104166667)**2)**0.5
        self.size = int(38.3928*inch-67.58824)
        self.scale = self.size/800

        # Λεξικό που τοποθετεί τις πόλεις του cities.txt πάνω στον χάρτη
        self.citycoords = {"athens":(364*self.scale,412*self.scale), "thessaloniki":(299*self.scale,128*self.scale),
                  "patra": (196*self.scale, 384*self.scale), "ioannina":(126*self.scale,238*self.scale),
                  "kalamata":(227*self.scale,513*self.scale), "alexandroupoli":(542*self.scale, 101*self.scale),
                  "chania":(358*self.scale,676*self.scale), "heraklion":(489*self.scale,694*self.scale),
                  "florina":(173.43493717641545*self.scale, 110.13709424669821*self.scale),
                  "larisa":(255*self.scale,234*self.scale),
                  "naxos":(491.8235614768711*self.scale, 510.8167221120252*self.scale),
                  "rodos":(699.6827637914597*self.scale, 595.6796302948583*self.scale),
                  "samos":(600.724153037398*self.scale, 439.3002170959124*self.scale),
                  "mytilene":(589.522435350222*self.scale, 291.37023963848605*self.scale)}

        # Tkinter based variables
        checkBoxA = BooleanVar()
        self.checkBoxA = checkBoxA

        # Progress Bar commands
        self.progress = Progressbar(root, orient=HORIZONTAL, length=100, mode='indeterminate')
        
        # Set collapsible menu
        cpane = collapsible_menu.CollapsibleMenu(root, '^', 'MENU')
        cpane.grid(row=1, column=0, sticky="n" + "w")

        # Menu buttons
        # master == το widget στο οποίο θα μπεί με΄σα το button
        self.b1 = Button(cpane.frame, text="Add city", height=2, width=10, command=self.add_city)
        self.b1.grid(row=1, column=1, pady=5)
        self.b2 = Button(cpane.frame, text="Weather by\ncity", command=self.get_city, height=2, width=10)
        self.b2.grid(row=2, column=1, pady=5)
        self.b3 = Button(cpane.frame, text="Weather by\ncoords", command=self.get_cords, height=2, width=10)
        self.b3.grid(row=3, column=1, pady=5)
        self.b4 = Button(cpane.frame, text="Weather\nprogress", command=self.city_plot, height=2, width=10)
        self.b4.grid(row=4, column=1, pady=5)
        self.cb1 = Checkbutton(cpane.frame, text="TTS", variable=checkBoxA, command=self.enable_tts, onvalue=True, offvalue=False)
        self.cb1.grid(row=5, column=1, pady=5)

        # Short description of what you are supposed to do
        text = Label(root, text="Κάνε κλικ στον χάρτη για να επιλέξεις περιοχή", bg='#e6e3e3')
        text.grid(row=0, column=0, columnspan=2, ipadx=0, ipady=0)

        # Text that displays when the app is launched
        info_frame = Frame(root, height=50, width=100)
        info_frame.grid(row=2, column=0, columnspan=2)
        self.forecast_l = Label(info_frame, text="Εδω οι καλές πληροφορίες",bg="#e6e3e3",font="Arial 12")
        self.forecast_l.pack()
        
        # Canvas widget displaying map of Greece
        og_img = Image.open("IMG/OXARTHS_5.PNG")
        og_pin = Image.open("IMG/pin.png")
        img_size = og_img.size
        self.width = int(self.size) # 1031 #
        self.height = int((self.size * img_size[1]) / img_size[0]) # 958 #
        img = ImageTk.PhotoImage(og_img.resize((self.width, self.height)))
        pin = ImageTk.PhotoImage(og_pin.resize((20,30)))
        self.canvas = Canvas(root, bg="skyblue", width=self.width, height=self.height)
        self.canvas.grid(row=1, column=1)
        self.canvas.create_image(0, 0, anchor=NW, image=img)
        self.lepin = self.canvas.create_image(-5, -5, image=pin)
        self.canvas.bind("<Button-1>", self.callback)

        # calling function that draws icons across the map
        self.draw_icons()
        playsound("Startupsound.mp3")
        mainloop()

    def draw_icons(self):
        """Βάζει όλα τα εικονίδια που περιγράφουν τον καιρό στις μεγάλες πόλεις"""
        for city in data_bible.GetData.cities:
            # Με το eval μετατρέπω το str που μου επιστρέφει η παρακάτω εντολή σε λεξικό
            forecast = jlib.ParseData(data_bible.GetData.get_data_by_name(data_bible.GetData, city), "d")
            icon = forecast.raw_data()["Icon"]
            for c in self.citycoords:
                if city == c:
                    # Για κάθε πόλη στο self.citycoords δημιουργείται αντίστοιχο κείμενο
                    # και εικονίδιο που περιγράφει τον καιρό, έπειτα το αντικείμενο της εικόνας προστίθεται
                    # σε μια λίστα για να αποφυγεί το Python Garbage Collecting
                    self.da_img = ImageTk.PhotoImage(Image.open(f"IMG/{icon}.png").resize((30, 30)))
                    self.canvas.create_image(self.citycoords[c][0] + len(c) * 6 if len(c) <= 6 else self.citycoords[c][0],
                                            self.citycoords[c][1], image=self.da_img)
                    self.canvas.create_text(self.citycoords[c][0],
                                            self.citycoords[c][1] if len(c) <=6 else self.citycoords[c][1]-15,
                                            fill="black", font="arial 12", text=self.cities[str(c.capitalize())])
                    self.canvas.update()
                    self.images.append(self.da_img)

    def translate(self, x, y):
        """Γίνεται μετάφραση συντεταγμένων, από  x,y του κανβά με έναν απλό τύπο σε γεωραφικό πλάτοσ και μήκος"""
        # Αυτό γτ στο canvas το Δx>0 από αριστερά προς δεξιά και Δy>0 από πάνω προς τα κάτω
        # ενώ εγώ θέλω από Δy>0 από κάτω προς τα πάνω αρα το αντιστρέφω
        self.y = self.height - y
        self.x = x

        # Αρχικές συντεταγμένες για τις πράξεις
        lon_min = 19.240501
        lon_max = 29.144982
        lat_min = 34.892627
        lat_max = 41.807543

        # Μετατροπή από x,y σε γεωγραφικές συντεταγμένες
        lat = lat_min + (self.y*(lat_max-lat_min))/self.height
        lon = lon_min + (self.x*(lon_max-lon_min))/self.width
        
        return lat, lon

    def reverse_translate(self, lat, lon):
        """Γίνεται μετάφραση γεωγραφικών συντεταγμένων σε συντεταγμένες του καμβά"""
        self.lat = float(lat)
        self.lon = float(lon)

        # Αρχικές συντεταγμένες για τις πράξεις
        lon_min = 19.240501
        lon_max = 29.144982
        lat_min = 34.892627
        lat_max = 41.807543

        # Μετατροπή από x,y σε γεωγραφικές συντεταγμένες
        y = self.height * ((self.lat - lat_min) / (lat_max - lat_min))
        x = self.width * ((self.lon - lon_min) / (lon_max - lon_min))

        return x, self.height - y

    def enable_tts(self):
        """Δίνει την άδεια να τρέξει η εντολή για την μετατροπή κειμένου σε ομιλία μέσω της υπηρεσίας gTTS της
        Google. """
        # Ανάλογα την τιμή της μεταβλητής ενεργοποιείται/απενεργοποιείται το Text To Speech
        state = self.checkBoxA.get()  # True if  else False

        return state
    
    def callback(self, event):
        """Όταν ο χρήστης κάνει κλικ σε ένα σημείο στον καμβά ψάχνει τον καιρό στο σημείο αυτό"""
        if self.done:
            self.x_old, self.y_old = 0, 0
        self.done = False
        x, y = event.x, event.y

        # Τοποθετεί μια εικόνα πινέζας στο σημείο που ο χρήστης κάνει κλικ
        self.canvas.move(self.lepin, -self.x_old-self.offset, -self.y_old-self.offset)
        self.canvas.move(self.lepin, x+self.offset, y+self.offset)
        self.x_old, self.y_old = x, y

        # Μετάφραση σε γεωγραφικές συντεταγμένες μέσω της translate
        lat, lon = self.translate(x, y)

        # Λήψη καιρικών συνθηκών μέσω της βιβλιοθληκης data_bible
        forecast = jlib.ParseData(data_bible.GetData.get_data_by_coords(data_bible.GetData, lat, lon), "d")
        self.forecast_l.configure(text=forecast.detailed_forecast())

        # Αν ο χρήστης έχει ανοίξει το TTS, το πρόγραμμα λέει τον καιρό
        if self.enable_tts(): TTS.Speak(forecast.simplified_forecast(), "el")

    def get_cords(self):
        """Αναζήτηση καιρού σε τοποθεσία με εισαγωγή συντεταγμένων"""
        def close():
            """Συνάρτηση που κλείνει το παράθυρο Get coordinates και τερματίζει τις κατάλληλες διαδικασίες"""
            # Προβολή καιρικών συνθηκών στο Label που βρίσκεται κάτω από τον καμβά
            forecast = jlib.ParseData(data_bible.GetData.get_data_by_coords(data_bible.GetData, lat.get(), long.get()), "d")
            try:
                x, y = self.reverse_translate(lat.get(), long.get())
                print(x, y)
                if self.done:
                    self.x_old, self.y_old = 0, 0
                self.done = False

                # Τοποθετεί μια εικόνα πινέζας στο σημείο που ο χρήστης κάνει κλικ
                self.canvas.move(self.lepin, -self.x_old - self.offset, -self.y_old - self.offset)
                self.canvas.move(self.lepin, x + self.offset, y + self.offset)
                self.x_old, self.y_old = x, y
                self.forecast_l.configure(text=forecast.detailed_forecast())
            except TypeError:
                pass

            self.forecast_l.configure(text=forecast.detailed_forecast())

            # Κλείσιμο παραθύρου
            newWindow.destroy()

            # Αν ο χρήστης έχει ανοίξει το TTS, το πρόγραμμα λέει τον καιρό
            if self.enable_tts(): TTS.Speak(forecast.simplified_forecast(), "el")

        # Δημιουργία νέου παραθύρου
        newWindow = Toplevel(self.root)
        newWindow.title("Give coordinates")
        newWindow.geometry("250x200")

        # Αποτρέπει τον χρήστη από το να πατήσει X για να βγει από το παράθυρο έτσι ώστε να μην υπάρξουν προβλήματα
        newWindow.protocol("WM_DELETE_WINDOW", self.__callback)

        # Οδηγίες που λένε στον χρήστη τι να κάνει
        Label(newWindow, text="Give the coordinates").pack()

        # Widget εισόδου και Label για εισαγωγή συντεταγμένων και κουμπί Ok για καταχώρηση δεδομένων
        Label(newWindow, text="Latitude").pack()
        lat = Entry(newWindow)
        lat.pack()
        Label(newWindow, text="Longitude").pack()
        long = Entry(newWindow)
        long.pack()
        Button(newWindow, text="Ok", command=close).pack()

    # Πάρε όνομα πόλης που σου δίνει ο χρήστης
    def get_city(self):
        """Αναζήτηση καιρού σε τοποθεσία με εισαγωγή ονόματος πόλης"""
        def close():
            """Συνάρτηση που κλείνει το παράθυρο Get city και τερματίζει τις κατάλληλες διαδικασίες"""
            # Προβολή καιρικών συνθηκών στο Label που βρίσκεται κάτω από τον καμβά
            forecast = jlib.ParseData(data_bible.GetData.get_data_by_name(data_bible.GetData, city.get()), "d")
            fdic = eval(str(forecast.raw_data()))
            try:
                x, y = self.reverse_translate(fdic["Latitude"], fdic["Longtitude"])
                print(x, y)
                if self.done:
                    self.x_old, self.y_old = 0, 0
                self.done = False

                # Τοποθετεί μια εικόνα πινέζας στο σημείο που ο χρήστης κάνει κλικ
                self.canvas.move(self.lepin, -self.x_old - self.offset, -self.y_old - self.offset)
                self.canvas.move(self.lepin, x + self.offset, y + self.offset)
                self.x_old, self.y_old = x, y
                self.forecast_l.configure(text=forecast.detailed_forecast())
            except TypeError:
                pass

            # Κλείσιμο παραθύρου
            newWindow.destroy()

            # Αν ο χρήστης έχει ανοίξει το TTS, το πρόγραμμα λέει τον καιρό
            if self.enable_tts(): TTS.Speak(forecast.simplified_forecast(), "el")

        # Δημιουργία νέου παραθύρου
        newWindow = Toplevel(self.root)
        newWindow.title("Give city name")
        newWindow.geometry("250x100")

        # Αποτρέπει τον χρήστη από το να πατήσει X για να βγει από το παράθυρο έτσι ώστε να μην υπάρξουν προβλήματα
        newWindow.protocol("WM_DELETE_WINDOW", self.__callback)

        # Οδηγίες που λένε στον χρήστη τι να κάνει
        Label(newWindow, text="City name").pack()

        # Widget εισόδου και Label για εισαγωγή ονόματος πόλης και κουμπί Ok για καταχώρηση δεδομένων
        city = Entry(newWindow)
        city.pack()
        Button(newWindow, text="Ok", command=close).pack()

    def city_plot(self):
        """Δημιουργία γραφήματος αποθηκευμένων πόλεων χρησιμοποιώντας την βιβλιοθήκη matplotlib"""
        # Δημιουργία λίστας με πόλεις για τις οποίες υπάρχει αρχείο JSON
        lista = next(os.walk(os.path.join(self.jdir, '.')))[2]

        # Δημιουργία λίστας με πόλεις που υπάρχουν στο cities.txt
        with open("cities.txt", "r", encoding="utf-8") as f:
            data = f.read()
            self.available_cities = data.split(",")
            try: self.available_cities.remove("")
            except: pass

        def close():
            """Κλείσιμο παραθύρου city plot"""
            name = str(variable.get()).lower()
            for k, v in self.cities.items():
                if v == name.capitalize():
                    name = k.lower()
                    break
            newWindow.destroy()
            city_files = [file for file in lista if name in file]

            if len(city_files) == 0:
                # Αν δεν υπάρχουν δεδομένα για την πόλη, εμφανίζεται το κατάλληλο error
                messagebox.showinfo("Warning", "There is no data for this city. :(\nTry restarting the app.")
            else:
                # Ανάγνωση δεδομένων καιρού απο το database με SQLite
                temp, hum, time = [], [], []
                d = SQD.Database()
                for forecast in d.get_all():
                    if str(self.cities[name.capitalize()]) == forecast[0] or str(name.capitalize()) == forecast[0]:
                        # Καταχώρηση δεδομένων του database
                        time.append(forecast[3][:10])
                        temp.append(forecast[7])
                        hum.append(forecast[6])

                # Δημιουργία του γραφήματος
                fig, (ax1, ax2) = plt.subplots(2)
                fig.suptitle(self.cities[name.capitalize()])
                ax1.plot(time, temp, 'o-')
                ax1.set_ylabel('Θερμοκρασία (C)')
                ax2.plot(time, hum, '.-')
                ax2.set_xlabel('Ημερομηνία (Days)')
                ax2.set_ylabel('Υγρασία (%)')
                for ax in fig.get_axes():
                    ax.label_outer()
                plt.xticks(time, rotation='vertical')
                plt.show()

        # Δημιουργία παραθύρου γραφήματος
        newWindow = Toplevel(self.root)
        newWindow.title("Choose a city")
        newWindow.geometry("250x100")

        # Αποτρέπει τον χρήστη από το να πατήσει X για να βγει από το παράθυρο έτσι ώστε να μην υπάρξουν προβλήματα
        newWindow.protocol("WM_DELETE_WINDOW", self.__callback)

        OPTIONSPLOT = [self.cities[i.capitalize()] for i in data.split(",")[:-1]]
        # Κείμενο που λέει για ποια πόλη έχουμε ψάξει δεδομένα
        variable = StringVar(newWindow)
        variable.set(OPTIONSPLOT[0])

        # drop down menu που εμφανίζει όλες τις πόλεις
        OptionMenu(newWindow, variable, *OPTIONSPLOT).pack() # data.split(",")[:-1]).pack()

        # Κουμπί Ok που κλέινει το παράθυρο city plot
        Button(newWindow, text="OK", command=close).pack()

    def add_city(self):
        """Προσθήκη πόλης στο cities.txt"""
        def close():
            """Κλείσιμο παραθύρου και διαδικασία προσθήκης"""
            with open("cities.txt", "a", encoding="utf-8") as f:
                with open("cities.txt", "r", encoding="utf-8") as fr:
                    for k, v in self.cities.items():
                        if variable.get() in [self.cities[eng_city.capitalize()] for eng_city in fr.read().split(",")[:-1]]:
                            break
                        if v == variable.get():
                            try: k = k.replace(" ", "")
                            except: pass
                            f.write(str(k).lower() + ",")
            newWindow.destroy()

        # Δημιουργία παραθύρου Choose a city
        newWindow = Toplevel(self.root)
        newWindow.title("Choose a city")
        newWindow.geometry("250x100")

        # Αποτρέπει τον χρήστη από το να πατήσει X για να βγει από το παράθυρο έτσι ώστε να μην υπάρξουν προβλήματα
        newWindow.protocol("WM_DELETE_WINDOW", self.__callback)

        # Κείμενο που εμφανίζει την πρώτη πόλη στην λίστα
        variable = StringVar(newWindow)
        variable.set(self.OPTIONS[0])  # default value

        # drop down menu με όλες τις πόλεις της Ελλάδας
        OptionMenu(newWindow, variable, *self.OPTIONS).pack()

        # Κουμπί Ok που κλείνει το παράθυρο
        Button(newWindow, text="OK", command=close).pack()

    @staticmethod
    def __callback():
        """Συνάρτηση που καλείται όταν ο χρήστης κάνει κλικ X σε οποιοδήποτε παράθυρο εκτός από root
        Η συνάρτηση δεν κάνει τίποτα, έτσι ώστε να μην κλείνουν τα παράθυρα της εφαρμογής"""
        return


if __name__ == "__main__":
    # Λήψη καιρικών συνθηκών της Ελλάδας μέσα από την data bible
    my_data = data_bible.GetData()

    # Αναζήτηση των πόλεων στο cities.txt
    lista = next(os.walk(os.path.join(my_data.jdir, '.')))[2]

    # Για κάθε πόλη στο cities.txt γίνεται έλεγχος ύπαρξης αρχείου JSON
    # Αν εμφανιστεί SSL certificate error εκτελείται η συνάρτηση set_ssl της data_bible
    for file in lista:
        data_bible.Checker(file)
    try:
        my_data.get_data()
    except:
        my_data.set_ssl(data_bible.GetData)
        my_data.get_data()

    # Προσθήκη σημερινού forecast στο database
    SQD.main()

    # Δημιουργία παραθύρου μέσω της tkinter
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()
