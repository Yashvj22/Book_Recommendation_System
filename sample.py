import sqlite3

conn = sqlite3.connect('feedback.sqlite')
cur = conn.cursor()
cur.execute('SELECT * from feedback;')
rows = cur.fetchall()
print('Printing data')
print(rows)

cur.close()
conn.close()