from sqlalchemy.orm import declarative_base,sessionmaker,relationship,configure_mappers
from sqlalchemy.inspection import inspect
from sqlalchemy import *
from sqlalchemy import event,Sequence,Identity
import pandas as pd
import os
import fnmatch
import re
import multiprocessing as mp
import time
from readExcelFiles import *
from queryblock import *
from models import *

def qsalchemy_litros(file_load,path_engine):
    print(path_engine)
    n=0
    ti = time.time()
    print('Start Query block')
    invalid_data=[]
    my_cache = {}
    
    engine = create_engine(path_engine,future=True,echo=True)
    Session = sessionmaker(bind=engine,autoflush=False)
    
    with session as conn:
        for col,row in file_load.iterrows():
            n=n+1
            sensor_inofo=Sensores(Fecha_Hora=pd.to_datetime(row['Fecha_Hora']),Tanque1=row['Tanque 1 (Lt)'],Tanque2=row['Tanque 2 (Lt)'],Odómetro=row['Odómetro (Km)'],file_name=str(row['file_name']),file=str(row['file']),unidad_id=int(row['unidad_id']))   
            try:
                session.add(sensor_inofo) 
                session.commit()
                #print('Item success')
                if n % 20==0:
                    
                    print('cargados 100*n registros {}'.format(n))
            except:
                session.rollback()
                session.close()
                raise
                invalid_data.append(row['file'])
                print('data invalid {}'.format(row['file']))
        
    print('End file time {} segundos'.format(time.time()-ti))
   
    
def qsalchemy_canbus(file_load,path_engine):
    print(path_engine)
    n=0
    invalid_data=[]
    ti = time.time()
    print('Start Query block')
    engine = create_engine(path_engine, echo=False, future=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    for col,row in file_load.iterrows():
        n=n+1
        sensores_canbus = SensoresCanbus(Fecha_Hora=pd.to_datetime(row['Fecha_Hora']),canbus=row['Total de Combustible Utilizado por el Motor (Lt)'],temp=row['Temperatura del motor °C '],rpm=row['Velocidad del Motor (RPM)'],Odometro=row['Odómetro (Km)'],file_name=str(row['file_name']),file=str(row['file']),unidad_id=int(row['unidad_id']))
        try:
            session.add(sensores_canbus) 
            session.commit()
            if n % 500==0:
                print('cargados 100*n registros {}'.format(n))
        except:
            session.rollback()
            raise
            invalid_data.append(row['file_name'])
            print('data invalid {}')    
    print('End file time {} segundos'.format(time.time()-ti))
                    