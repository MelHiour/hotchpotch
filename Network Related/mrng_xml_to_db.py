#!/usr/bin/env python3

import mysql.connector

mydb = mysql.connector.connect(
  host="192.168.0.19",
  user="mremoteng",
  passwd="LabPass123",
  database="mRemoteNG"
)

values = [i for i in range(0,120)]

mycursor = mydb.cursor()

def db_get_columns(db_cursor, table_name):
    columns = []
    db_cursor.execute("describe " + table_name)
    for line in db_cursor:
        columns.append(line[0])
    return columns

def db_insert(db_cursor, table_name, values):
    columns = db_get_columns(db_cursor, table_name)
    columns_string = ','.join(column for column in columns)
    sql = "INSERT INTO {} ({}) VALUES {}".format(table_name, columns_string, tuple(values))
    db_cursor.execute(sql)
    mydb.commit()

db_insert(mycursor, 'tblCons', values)
