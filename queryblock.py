from sqlalchemy import Column, Integer, String,Boolean, ForeignKey,UniqueConstraint,PrimaryKeyConstraint,sql
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,configure_mappers
from sqlalchemy.inspection import inspect
from sqlalchemy import *
from sqlalchemy import event,DDL,Sequence,Identity
from sqlalchemy import inspect,func
from sqlalchemy import create_engine
import time

#path_engine = "firebird://sysdba:300184rm2@localhost///home/rokdrigo/GitClone/Combustible2/firebirdDatabase/firbirdSensores.fdb"
path_to_files="/home/rokdrigo/GitClone/Combustible2/Sensores/"

def QsConn(qs,path_engine):
    #ti = time.time()
    #print('Start Query block')
    #path_engine = "firebird://sysdba:300184rm2@localhost///home/rokdrigo/GitClone/Combustible2/firebirdDatabase/firbirdSensores.fdb"
    engine = create_engine(path_engine, echo=True, future=False)
    try:
        conn=engine.connect()
        conn.execute(text(qs))
        conn.commit()
        conn.close()
    #    print('Commint sueccess 5 rows insert at {}'.format(time.time()-ti))
    except Exception as e:
        print("sommenthing fail")
        conn.rollback()
        conn.close()
        print(qs)
        raise

#engine = create_engine(path_engine, echo=False, future=True)
#insp = inspect(engine)


