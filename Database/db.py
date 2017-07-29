import sqlite3
def getFuzz(type):
    conn = sqlite3.connect("Database/db.sqlite")
    c = conn.cursor()

    list = [type]
    sql = '''SELECT fuzz, expected, nature from fuzz where type=?'''
    c.execute(sql, list)

    output = []
    for value in c.fetchall(): #the first item is the real payload
        output.append([value[0], value[1], value[2]])
    try:         
        return output
    finally:
        conn.close()
