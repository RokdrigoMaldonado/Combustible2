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


def load_dataframe_litros(parsedFiles,path_engine):
    print(path_engine)
    df_to_pass=None
    if isinstance(parsedFiles, dict):
        
        loadeded=[item[0] for item in session.query(Sensores.file_name).group_by(Sensores.file_name).all()]
        
        if 'Detalle' in parsedFiles.keys() and parsedFiles['Detalle'].empty== False : 
            files_Litros=list(parsedFiles['Detalle'].groupby(by=['file_name']).count().index)
            df_to_pass=parsedFiles['Detalle'][['Fecha_Hora','Tanque 1 (Lt)','Tanque 2 (Lt)','Odómetro (Km)','unidad_id','file','file_name']].copy()
        
        if 'Litros' in parsedFiles.keys() and parsedFiles['Litros'].empty== False :
            files_Litros=list(parsedFiles['Litros'].groupby(by=['file_name']).count().index)
            df_to_pass=parsedFiles['Litros'][['Fecha_Hora','Tanque 1 (Lt)','Tanque 2 (Lt)','Odómetro (Km)','unidad_id','file','file_name']].copy()    
        
        invalid_data=[]
        #Check and parse this can be rewrite as funcion in the imprube 
        if df_to_pass is not None:
            df_to_pass[["Tanque 1 (Lt)", "Tanque 2 (Lt)","Odómetro (Km)"]] = df_to_pass[["Tanque 1 (Lt)", "Tanque 2 (Lt)","Odómetro (Km)"]].apply(pd.to_numeric)
            df_to_pass[["Tanque 1 (Lt)", "Tanque 2 (Lt)","Odómetro (Km)"]] = df_to_pass[["Tanque 1 (Lt)", "Tanque 2 (Lt)","Odómetro (Km)"]].apply(lambda x: round(x,2))
            df_to_pass.replace(to_replace=[np.NaN],value=sql.null(), inplace=True) 
            df_to_pass=df_to_pass.astype('string')
            #Aqui se puede agregar o validad 
            file_sql_passed=[]
            for file in files_Litros:
                if file not in loadeded:
                    file_load=df_to_pass[df_to_pass['file_name']==file]
                    qsalchemy_litros(file_load)
                

def load_dataframe_Canbus(parsedFiles,path_engine):
    print(path_engine)
    df_to_pass=pd.DataFrame()
    print('Start Canbus PASSSSS.................................................')
    
    loadeded=[item[0] for item in session.query(SensoresCanbus.file_name).group_by(SensoresCanbus.file_name).all()]
    
    #print(loadeded)
    
    if isinstance(parsedFiles, dict):
    
        if 'Canbus CAN-BUS' in parsedFiles.keys() and len(parsedFiles['Canbus CAN-BUS'])>0:

            files_Litros=list(parsedFiles['Canbus CAN-BUS'].groupby(by=['file_name']).count().index)
            renameUbica={parsedFiles['Canbus CAN-BUS'].columns[8]:'Total de Combustible Utilizado por el Motor (Lt)',parsedFiles['Canbus CAN-BUS'].columns[5]:'Temperatura del motor °C',parsedFiles['Canbus CAN-BUS'].columns[7]:'Velocidad del Motor (RPM)'}
            df_to_pass=parsedFiles['Canbus CAN-BUS'][['Fecha_Hora',parsedFiles['Canbus CAN-BUS'].columns[8],parsedFiles['Canbus CAN-BUS'].columns[5],parsedFiles['Canbus CAN-BUS'].columns[7],'unidad_id','file_name','file',]].copy()
            df_to_pass=df_to_pass.rename(columns=renameUbica)
            df_to_pass['Odómetro (Km)']=sql.null()

        if 'Canbus CAN-BUS Sacmamx' in parsedFiles.keys() and len(parsedFiles['Canbus CAN-BUS Sacmamx'])>0: 
            files_Litros=list(parsedFiles['Canbus CAN-BUS Sacmamx'].groupby(by=['file_name']).count().index)
            if 'Odómetro (Km)' not in files_parsed['Canbus CAN-BUS Sacmamx'].columns:
                parsedFiles['Canbus CAN-BUS Sacmamx']['Odómetro (Km)']=None
            df_to_pass=parsedFiles['Canbus CAN-BUS Sacmamx'][['Fecha_Hora','Total de Combustible Utilizado por el Motor (Lt)','Temperatura del motor °C','Velocidad del Motor (RPM)','Odómetro (Km)','unidad_id','file_name','file']].copy()
            print('Hello aqui antes de enviar que esta pasando {}'.format(df_to_pass))
            print(df_to_pass.columns)
        
        invalid_data=[]
        if df_to_pass.empty==False:
            df_to_pass.replace(to_replace=[np.NaN],value= sql.null(), inplace=True) 
            invalid_data=[]
            file_sql_passed=[]
            for file in files_Litros:
                if file not in loadeded:
                    file_load=df_to_pass[df_to_pass['file_name']==file]
                    qsalchemy_canbus(file_load)

def qsalchemy_litros(file_load,path_engine):
    print(path_engine)
    n=0
    ti = time.time()
    print('Start Query block')
    invalid_data=[]
    my_cache = {}
    #path_engine = "firebird://sysdba:300184rm2@localhost///home/rokdrigo/GitClone/Combustible2/firebirdDatabase/Test1.fdb"
    engine = create_engine(path_engine,future=True,echo=True,pool_size=20, max_overflow=0).execution_options(compiled_cache=my_cache)
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
    #path_engine = "firebird://sysdba:300184rm2@localhost///home/rokdrigo/GitClone/Combustible2/firebirdDatabase/Test1.fdb"
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
                    