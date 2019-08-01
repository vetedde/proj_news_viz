import re 
import csv
import sqlite3
import argparse

def csv_to_sqlite(filename, dst):
    try:
        newsjournal_name = filename[filename.rfind('/')+1:filename.rfind('.')]
    except:
        newsjournal_name = 'database'
    conn = sqlite3.connect(f"{dst}{newsjournal_name}.db")
    cur = conn.cursor() 
    cur.execute("""CREATE TABLE IF NOT EXISTS {}(date varchar, url varchar, edition varchar,
    topics varchar,	authors varchar, title varchar, text varchar, reposts_fb varchar,
    reposts_vk varchar,	reposts_ok varchar,	reposts_twi varchar, reposts_lj varchar, reposts_tg varchar,	
    likes varchar, views varchar, comm_count varchar, whatever varchar)""".format(newsjournal_name))
    with open(filename, encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for field in reader:
		    #some lines were damaged, that's why there are used try/except
            try:
                cur.execute("INSERT INTO {} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);".format(newsjournal_name), field)
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
	
