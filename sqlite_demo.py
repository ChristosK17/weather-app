# sqlite_demo.py

import sqlite3, os, JLIB, data_bible

# Άνοιγμα αρχείου cities.txt και καταχώρηση πόλεων σε λίστα cities
with open("cities.txt", "r", encoding="utf-8") as f:
	data = f.read()
	cities = data.split(",")
	try: cities.remove("")
	except: pass

jdir = "JSONforecasts"


class Database:
	def __init__(self, db="weatherdata.db"):
		self.db = db

		# Σύνδεση σε database
		self.conn = sqlite3.connect(db)

		# Δημιουργία cursor database
		self.c = self.conn.cursor()

		# Αν δεν υπάρχει αρχείο database weatherdata.db δημιουργείται
		try:
			self.c.execute("""CREATE TABLE weatherdata (
								name text,
								d_forecast text,
								c_forecast text,
								timestamp text,
								lon real,
								lat real,
								humidity real,
								temperature real
								)""")
		except: pass
		self.conn.commit()

	def insert_data(self, name, d_forecast, c_forecast, lon, lat, humidity, temp, timestamp):
		"""Συνάρτηση που προσθέτει όλα τα στοιχεία του καιρού στο database"""
		self.name = name
		self.d_forecast = d_forecast
		self.c_forecast = c_forecast
		self.lon = lon
		self.lat = lat 
		self.humidity = humidity
		self.temp = temp				
		self.timestamp = timestamp

		self.c.execute("SELECT * FROM weatherdata WHERE (name=? "
					   "AND d_forecast=? "
					   "AND c_forecast=? "
					   "AND timestamp=? "
					   "AND lon=? "
					   "AND lat=? "
					   "AND humidity=? "
					   "AND temperature=?)",
					   (self.name,
						self.d_forecast,
						self.c_forecast,
						self.timestamp,
						self.lon,
						self.lat,
						self.humidity,
						self.temp))

		entry = self.c.fetchone()

		# Αν δεν υπάρχει στοιχείο για την ζητούμενη πόλη στο database την ζητούμενη χρονική στιγμή
		# δημιουργείται "γραμμή" που συμπεριλαμβάνει τα βασικά στοιχεία του καιρού
		if entry is None:
			self.c.execute("INSERT INTO weatherdata VALUES (?, ? ,?, ?, ?, ?, ?, ?)",
						   (self.name,
							self.d_forecast,
							self.c_forecast,
							self.timestamp,
							self.lon,
							self.lat,
							self.humidity,
							self.temp))
		self.conn.commit()

	def get_all(self):
		"""Αναζήτηση και επιστροφή καιρικών συνθηών για ζητούμενη πόλη στο database"""
		self.c.execute(f"SELECT * FROM weatherdata")
		return [row for row in self.c.fetchall()]


def main():
	d = Database()

	# Καταχώρηση JSON αρχείων σε λίστα
	lista = next(os.walk(os.path.join(jdir, '.')))[2]

	# Προσθήκη των forecast των αρχείων JSON στο weatherdata.db
	for file in lista:
		raw_data = JLIB.ParseData(os.path.join("JSONforecasts", file), "f")
		forecast = raw_data.raw_data()
		try:
			d.insert_data(forecast["Name"], raw_data.detailed_forecast(), raw_data.simplified_forecast(), forecast["Longtitude"], forecast["Latitude"], forecast["Humidity"], forecast["Temperature"], forecast['Dt'])
			data_bible.Checker(file, 0)
		except: pass


if __name__ == "__main__": main()

