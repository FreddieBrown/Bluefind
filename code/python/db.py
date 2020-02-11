import sqlite3

class Database:
	def __init__(self, path):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
	def insert(self, list_of_entries):
		"""
		This function will take a list of tuples of the type (MAC address, coordinates, datetime).
		These will be stored in the database specified in the connection.
		This will always be stored in the 'find' table each time. 
		"""
		self.cursor.executemany('INSERT INTO find(mac, coord, recvd) VALUES (?,?,?)', list_of_entries)
		self.connection.commit()
	def select(self, num):
		"""
		This function will select data from the database from the 'find' table.
		num will dictate how many entries are retrieved from the database.
		"""
		addresses = []
		coords = []
		stmt = '''SELECT mac, coord FROM (SELECT mac, max(recvd) AS recvd FROM find GROUP BY(mac)) m  
				NATURAL JOIN find WHERE m.mac = find.mac AND find.recvd = m.recvd ORDER BY recvd DESC LIMIT {}'''.format(num)
		# stmt = "SELECT DISTINCT mac, coord FROM find ORDER BY recvd DESC LIMIT {} ".format(num)
		for row in self.cursor.execute(stmt):
			addresses.append(row[0])
			coords.append(row[1])
		return [coords, addresses]