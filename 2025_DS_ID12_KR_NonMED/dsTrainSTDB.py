from datetime import datetime
import sqlite3

def createTable():
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    # query = "create table if not exists ds_db_train(id integer auto_increment, name text, year int, month int, day int, hour int, minute int, train_scent text, selfcheck int)" 
    query = "create table if not exists ds_db_train(name text, year int, month int, day int, hour int, minute int, train_scent text, selfcheck int)"
    cur.execute(query)
    con.commit()
    con.close()

def insertTable(name, year, month, day, hour, minute, train_scent, selfcheck):
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    data = (name, year, month, day, hour, minute, train_scent, selfcheck)
    query = "insert into ds_db_train(name, year, month, day, hour, minute, train_scent, selfcheck) values (?, ?, ?, ?, ?, ?, ?, ?)" 
    cur.execute(query, data)
    con.commit()
    con.close()

def insertCurrentTable(train_scent, selfcheck):
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    insertTable('cesuser', year, month, day, hour, minute, train_scent, selfcheck)
    showTable()
    
def selectTable():
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    query = "select * from ds_db_train"
    cur.execute(query)
    data = cur.fetchall()
    #print(data)
    for name, year, month, day, hour, minute, train_scent, selfcheck in data:
        print(name, year, month, day, hour, minute, train_scent, selfcheck)
    con.commit()
    con.close()

def selectAllFromTable():
    datas = [('name', 'year', 'month', 'day', 'hour', 'minute', 'train_scent', 'selfcheck')]
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    query = "select * from ds_db_train"
    cur.execute(query)
    data = cur.fetchall()
    #print(data)
    for name, year, month, day, hour, minute, train_scent, selfcheck in data:
        datas.append((name, year, month, day, hour, minute, train_scent, selfcheck))
    con.commit()
    con.close()
    # print(datas)
    return datas

def selectDataFromTable(train_scent):
    datas = []
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    query = "select * from ds_db_train where train_scent = '%s'"%train_scent
    cur.execute(query)
    data = cur.fetchall()
    #print(data)
    for name, year, month, day, hour, minute, train_scent, selfcheck in data:
        datas.append((name, year, month, day, hour, minute, train_scent, selfcheck))
    con.commit()
    con.close()
    # print(datas)
    return datas

def showTable():
    con = sqlite3.connect("dsTrainSTDB.db")
    cur = con.cursor()
    query = "select * from ds_db_train"
    cur.execute(query)
    data = cur.fetchall()
    for name, year, month, day, hour, minute, train_scent, selfcheck in data:
        print(name, year, month, day, hour, minute, train_scent, selfcheck)
    con.commit()
    con.close()

if __name__ == "__main__":
    createTable()
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    # insertCurrentTable("Rose", 32)
    selectTable()
    # selectDataFromTable("Lemon")