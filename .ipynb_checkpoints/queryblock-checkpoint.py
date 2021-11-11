from sqlalchemy import Column, Integer, String,Boolean, ForeignKey,UniqueConstraint,PrimaryKeyConstraint,sql
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,configure_mappers
from sqlalchemy.inspection import inspect
from sqlalchemy import *
from sqlalchemy import event,DDL,Sequence,Identity
from sqlalchemy import inspect,func
from sqlalchemy import create_engine
import time
import firebirdsql
#this is working good
### for some reasen alchemy is not working to use insert block statement should use firebirdql instead 
###
#
def QsConn(qs):
    ti = time.time()
    host='206.81.11.212///var/lib/firebird/3.0/data/SensoresRomaga.fdb'
    con = firebirdsql.connect(dsn=host, user='sysdba', password='300184rm2')  
    try:
        cur = con.cursor() 
        #conn=engine.connect()
        #print(qs)
        cur.execute(qs)
        con.commit()
        con.close()
        print('Commint sueccess 18 rows insert at {}'.format(time.time()-ti))
    except Exception as e:
        print("sommenthing fail")
        con.rollback()
        con.close()
        print(qs)
        raise
    
#engine = create_engine(path_engine, echo=False, future=True)
#insp = inspect(engine)

        