import sqlite3
import os

#db_abs_path = os.path.dirname(os.path.realpath(__file__)) + '/users.db'
conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS items")
c.execute("DROP TABLE IF EXISTS users")

c.execute("""CREATE TABLE items(
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    title           TEXT,
                    body            TEXT,
                    author          TEXT,
                    create_date     TEXT,
                    publish         INTEGER
)""")

c.execute("""CREATE TABLE users(
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name           TEXT,
                    email       TEXT,
                    username          TEXT,
                    password     TEXT,
                    register_date   TEXT
                    
)""")



'''items = [
    ("Article 1", "You can record anything.", "Anna Gottfried", "25-01-2020"),
    ("Article 2", "1kg of fresh bananas.","Jadwiga Gottfried", "28-08-2020"),
    ("Article 3", "In color!", "Jan Gottfried", "27-05-2020"),
    ("Article 4", "From the best farms.", "Roman Gottfried", "21-03-2020")
]'''
'''c.executemany("INSERT INTO items (title, body, author, create_date) VALUES (?,?,?,?)", items)
'''


conn.commit()
conn.close()