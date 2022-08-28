from msilib import Table
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Fortnitejax1@localhost/postgres")

session = Session(engine)

Base = automap_base()
Base.prepare(engine, reflect=True)

# Mapped classes are now created with names by default matching that of the table name.
Table_Name = Base.classes.table_name
print(Table_Name)

# # Example query with filtering
# query = session.query(Table_Name).filter(Table_Name.language != 'english')

# # Convert to DataFrame
# df = pd.read_sql(query.statement, engine)
# df.head()