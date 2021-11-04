import multiprocessing as mp
from time import time
import os
import numpy as np
import pandas as pd
import datetime as dt
import re
#import xlrd
import openpyxl
import time

def loadFiles_litros(filelink):
    filetype='cuentalitros'
    parsed_combustible=(pd.read_excel(filelink,sheet_name='Eventos',
                         engine="openpyxl",
                         usecols=None, 
                         header=1,
                         skiprows=range(1,10),
                         converters={'Combustible (Lt)': lambda x : pd.to_numeric(x.split()[0].replace('-', ''))},
                         parse_dates=[['Fecha','Hora']],
                         date_parser=lambda col: pd.to_datetime(col, format="%d-%m-%Y %H:%M:%S",dayfirst=True)
                     )
            )

   
    parsed_combustible['file']=filelink
    parsed_combustible['file_name']=os.path.basename(filelink)
    print("----"*40)
    print("File loaded ......{} typo de archivo {}".format(filelink,filetype))
    return parsed_combustible

def loadFiles_canbus(filelink):
    f=lambda x : pd.to_numeric(x.split()[0].replace('-', ''))
    filetype='canbus'
    try:
        parsed_canbus=(pd.read_excel(filelink,sheet_name='Datos Computadora CAN-BUS OBD',
                                 engine="openpyxl",
                                 usecols='B:R',
                                 header=1,
                                 skiprows=range(1,8),
                                 converters={6:f,8:f,9:f,10:f,11:f,12:f,'Datos Computadora CAN-BUS OBD':lambda x : pd.to_numeric(x.split()[0].replace('-', ''))},
                                 parse_dates=[['Fecha','Hora']],
                                 date_parser=lambda col: pd.to_datetime(col, format="%d-%m-%Y %H:%M:%S",dayfirst=True)
                             )
                    )
        
        print('Parsed Columns revies {}'.format(parsed_canbus.columns))
    
    except :
            print("La unidad no tiene Canbus")
            parsed_canbus=pd.DataFrame(['Sin Canbus'])
               
    parsed_canbus['file']=filelink
    parsed_canbus['file_name']=os.path.basename(filelink)
    print("----"*40)
    print("Parsed File {} typo de archivo {}".format(filelink,filetype))
    return parsed_canbus


def loadFiles_tanques(filelink):
    f=lambda x : pd.to_numeric(x.split()[0].replace('-', ''))
    filetype='cuentalitros_detalle'
    parsed_Detalle=(pd.read_excel(filelink,sheet_name='Detalle del Evento',
                         engine="openpyxl",
                         usecols=None,
                         header=1,
                         skiprows=range(1,9),
                         converters={'Tanque 1 (Lt)':f ,'Tanque 2 (Lt)':f},
                         parse_dates=[['Fecha','Hora']],
                         date_parser=lambda col: pd.to_datetime(col, format="%d-%m-%Y %H:%M:%S",dayfirst=True)
                     )
            )

    parsed_Detalle['file']=filelink
    parsed_Detalle['file_name']=os.path.basename(filelink)
    print("----"*40)
    print("File loaded ......{} typo de archivo {}".format(filelink,filetype))
    return parsed_Detalle

def load_sacmax_canbus(filelink):
    f= lambda col:pd.to_numeric(col,errors='coerce')
    r= lambda x: round(x,2)
    dateParserF= lambda col:pd.to_datetime(col,format="%d/%m/%Y %H:%M:%S", dayfirst=True)
    print("file Sacmamx {} to load".format(filelink))
    filecanbus=(pd.read_csv(filelink,header=0,
                                    parse_dates = {'Fecha y Hora':[0,1]},
                                    date_parser =dateParserF,
                           converters={'Temperatura del motor °C':f,2:f,3:f,4:f})
                         )
    
    renameSacmamxColumnsCanbus={ filecanbus.columns[1]:'Total de Combustible Utilizado por el Motor (Lt)',
        'Fecha y Hora':'Fecha_Hora',
        'Odometro':'Odómetro (Km)',
        'RPM':'Velocidad del Motor (RPM)'
    }
    
    filecanbus[filecanbus.columns[3]]=filecanbus[filecanbus.columns[3]].apply(lambda col:pd.to_numeric(col,errors='coerce'))
    filecanbus[filecanbus.columns[2]]=filecanbus[filecanbus.columns[2]].apply(lambda col:pd.to_numeric(col,errors='coerce'))
    filecanbus=filecanbus.rename(columns=renameSacmamxColumnsCanbus)
    
    filecanbus['file']=filelink
    filecanbus['file_name']=os.path.basename(filelink)
    
    if 'Temperatura del motor °C ' in filecanbus.keys():
        filecanbus=filecanbus.rename(columns={'Temperatura del motor °C ':'Temperatura del motor °C'})
        filecanbus['Temperatura del motor °C']= filecanbus['Temperatura del motor °C'].apply(lambda col:pd.to_numeric(col,errors='coerce'))
    
    if 'Temperatura del motor °C' not in filecanbus.keys():
        filecanbus['Temperatura del motor °C']=None
                
    print('Read canbus***************************Sacma {} columns'.format(filecanbus.columns))
    
    return filecanbus
    
    
def load_sacmax_sensores(filelink):
    f= lambda col:pd.to_numeric(col,errors='coerce')
    dateParserF= lambda col:pd.to_datetime(col,format="%d/%m/%Y %H:%M:%S", dayfirst=True)
    renameSacmamxColumnsLitros={
       'Odometro':'Odómetro (Km)',
    }
    filesLitroDetalle=(pd.read_csv(filelink,header=0,parse_dates = {'Fecha_Hora':[0,1]},
                                   date_parser =dateParserF,
                                   converters={2:f,3:f})
                                       )
    filesLitroDetalle['file']=filelink
    filesLitroDetalle['file_name']=os.path.basename(filelink)
    renameDetalleSacmaUnits={'Fecha_Hora':'Fecha_Hora',filesLitroDetalle.columns[1]:'Tanque 1 (Lt)', filesLitroDetalle.columns[2]:'Tanque 2 (Lt)','Odometro':'Odómetro (Km)'}
    filesLitroDetalle=filesLitroDetalle.rename(columns=renameDetalleSacmaUnits)
    filesLitro= filesLitroDetalle
    filesLitro['Combustible (Lt)']=pd.to_numeric(filesLitro.iloc[:,2],errors='coerce')
    filesLitro['Odómetro (Km)']=pd.to_numeric(filesLitro.iloc[:,3],errors='coerce')
    return filesLitro
                                       
                                                 
                                                 
  