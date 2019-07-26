import sqlite3
import csv
import argparse

def csv_to_sqlite(filename, dst):
	conn = sqlite3.connect('{}gazeta.db'.format(dst))
	cur = conn.cursor() 
	cur.execute("""CREATE TABLE IF NOT EXISTS gazeta(date varchar,	url varchar,	edition varchar,
	topics varchar,	authors varchar,	title varchar,	text varchar,	reposts_fb varchar,
	reposts_vk varchar,	reposts_ok varchar,	reposts_twi varchar,	reposts_lj varchar,	reposts_tg varchar,	
	likes varchar,	views varchar,	comm_count varchar, whatever varchar)""")
	filename.encode('utf-8')
	with open(filename) as f:
		reader = csv.reader(f)
		for field in reader:
		  #some lines were damaged, that's why there are used try/except
			try:
				cur.execute("INSERT INTO gazeta VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", field)
			except:
				continue

	conn.commit()
	conn.close()
		
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='''Usage:python csv_to_sqlite.py <path_to_csv> <destination_path>''')
	parser.add_argument("path_to_csv", help="which csv file convert to .db file")
	parser.add_argument("destination_path", default='', help="where program should put '.db file'")
	args = parser.parse_args()
	c = csv_to_sqlite(args.path_to_csv, args.destination_path)
	
