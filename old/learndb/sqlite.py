# import sqlite3

# db = sqlite3.connect("simple.db")
# cursor = db.cursor()

# cursor.execute('''
#     CREATE TABLE scores(
#         id integer, 
#         name string,
#         surname string,
#         score integer
#     )
# ''')

# db.commit()
# db.close()

# import sqlite3

# db = sqlite3.connect("simple.db")
# cursor = db.cursor()

# cursor.execute('''
#     CREATE TABLE scores(
#         insert into stores (id,name,surname,score) values (1, "Jack", "Black", 76)
#     )
# ''')

# db.commit()
# db.close()

import pandas as pd
import sqlite3

db = sqlite3.connect("UFCStats.db", timeout = 10)

df = pd.read_sql("select * from UFC_cleaned", db)
print(df.columns)
