from sqlalchemy import Column, Integer, String,Boolean, ForeignKey,UniqueConstraint,PrimaryKeyConstraint,sql
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,configure_mappers
from sqlalchemy.inspection import inspect
from sqlalchemy import *
from sqlalchemy import event,Sequence,Identity
import firebird
import pandas as pd
import os
import fnmatch
import re
import multiprocessing as mp
import xlrd
import pickle
import time
from readExcelFiles import *
from queryblock import *
from openpyxl import load_workbook
from functools import partial

path_engine = "firebird://sysdba:300184rm2@localhost///home/rokdrigo/GitClone/Sensores2/firbirdSensores.fdb"
path_to_files="/home/rokdrigo/GitClone/Sensores2/Sensores/"

#host='206.81.11.212/var/lib/firebird/3.0/data/RomagaFacturasxml.fdb'
#user='sysdba'
#password='300184rm2'

engine = create_engine(path_engine, echo=False, future=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

class Sensores(Base):
    
    __tablename__='Sensores_table'
    __table_args__ = (
    #this can be db.PrimaryKeyConstraint if you want it to be a primary key
    PrimaryKeyConstraint('Fecha_Hora', 'unidad_id', name='id_mix'),)
    Fecha_Hora=Column('Fecha_Hora', TIMESTAMP)
    Tanque1=Column('Tanque 1 (Lt)', Integer, nullable=True)
    Tanque2= Column('Tanque 2 (Lt)', Integer, nullable=True)
    Odómetro=Column('Odómetro (Km)', Integer, nullable=True)
    file_name= Column('file_name', String(1024), nullable=True)
    file=Column('file', String(1024), nullable=True)
    unidad_id = Column(Numeric, ForeignKey('Unidades.numero'))
    unidad = relationship("Unidad", back_populates="sensoresUbica")
    

class SensoresCanbus(Base):
    
    __tablename__='Sensores_canbus'
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        PrimaryKeyConstraint('Fecha_Hora', 'unidad_id'),
    )
    Fecha_Hora=Column('Fecha_Hora',TIMESTAMP)
    canbus=Column('Total de Combustible', Integer, nullable=True)
    temp= Column('Temperatura del motor °C ', Integer, nullable=True)
    rpm=Column('Velocidad del Motor (RPM)', Integer, nullable=True)
    Odometro=Column('Odómetro (Km)', Integer, nullable=True)
    file_name= Column('file_name', String(1024), nullable=True)
    file= Column( 'file',String(512),nullable=True)
    unidad_id = Column(Numeric, ForeignKey('Unidades.numero'))
    unidad_can = relationship("Unidad", back_populates="sensoresCanUbica")
    
class Unidad(Base):
    
    __tablename__ = 'Unidades'

    #id = Column(Integer,nullable=False,primary_key=True)
    numero = Column(Integer,primary_key=True)
    economico=Column(String(256),unique=True)
    canbus = Column(String(256))
    company = Column(String(256))
    sensoresUbica = relationship("Sensores",back_populates="unidad")
    sensoresCanUbica = relationship("SensoresCanbus",back_populates="unidad_can")
    
    def __init__(self,numero,economico,canbus,company):
        self.numero=numero
        self.economico = economico
        self.canbus=canbus
        self.company = company
        #self.parsedFiles=[]
    
    def __str__(self):
        return "La unidad:"+str(self.numero)+" "+"Compania"+" "+str(self.company)
    
    
    def get_files(self,session):
        
        self.ListFilesUnidad=[]
        self.Litros_ubicalo=[]
        self.Litros_sacmamx=[]
        self.Canbus_ubicalo=[]
        self.Canbus_sacmamx=[]
        
        os.chdir(path_to_files)
        
        loadeded_litros=[item[0] for item in session.query(Sensores.file_name).group_by(Sensores.file_name).all()]
        loadeded_canbus=[item[0] for item in session.query(SensoresCanbus.file_name).group_by(SensoresCanbus.file_name).all()]
        
        ListFilesLoad=([file for file in os.listdir('.') if fnmatch.fnmatch(file, '*.xlsx') or fnmatch.fnmatch(file,'*.csv')])
        ListFilesUnidad=([file for file in ListFilesLoad if re.search(self.economico,file)])
        
        for file in ListFilesUnidad:
            if fnmatch.fnmatch(file, '*.xlsx'):
                
                sheets=get_sheetnames_xlsx(path_to_files+file)
                
                if file not in loadeded_litros:
                    #print(loadeded_litros)
                    print('file in eventos {}'.format(file))
                    if ('Eventos' in sheets) or ('Detalle del Evento' in sheets):
                        print("Eventos")
                        self.Litros_ubicalo.append(file)
                        print(file)
                
                if file not in loadeded_canbus:
                    #print(loadeded_canbus)
                    print('Not file in {}'.format(file))
                    if ('Datos Computadora CAN-BUS OBD' in sheets):
                        print("Canbus")
                        self.Canbus_ubicalo.append(file)
                        
            if file not in loadeded_canbus:
                if fnmatch.fnmatch(file,'*.csv') and re.search('Canbus',file):
                    print("Scama_canbus___{}".format(file))
                    self.Canbus_sacmamx.append(file)                
            
            if file not in loadeded_litros:        
                if fnmatch.fnmatch(file,'*.csv') and not re.search('Canbus',file):
                    print("Sacma fie {}".format(file))
                    self.Litros_sacmamx.append(file)   

        return self.ListFilesUnidad
        
    
    def parse_files(self):
        parsed_files=dict()
        evenots=[]
        Detalle_ubicalo=pd.DataFrame()
        litros_sacmamx=pd.DataFrame()
        canbus_sacmamx=pd.DataFrame()
        Canbus_ubicalo=pd.DataFrame()
        
        
        if self.Litros_ubicalo or self.Litros_sacmamx or self.Canbus_sacmamx or self.Canbus_ubicalo:
            Canbus_ubicalo=[]
            #print(self.Litros_ubicalo)
            cores=3
            print('parse')
            
            map_send=[path_to_files+file for file in  self.Litros_ubicalo]
            if map_send:
                #process_files(cores,map_send,unidad,functionLoad,sheet_load)
                evenots=process_files(3,map_send,self.numero,loadFiles_litros,sheet_load='Eventos')
            
            map_send=[path_to_files+file for file in self.Canbus_ubicalo]
            if map_send and self.Canbus_ubicalo:
                Canbus_ubicalo=process_files(3,map_send,self.numero,loadFiles_canbus,sheet_load='Canbus CAN-BUS')
            
            map_send=[path_to_files+file for file in self.Litros_ubicalo]
            if map_send:
                Detalle_ubicalo=process_files(3,map_send,self.numero,loadFiles_tanques,sheet_load='Detalle del Evento')
                
            map_send=[path_to_files+file for file in self.Canbus_sacmamx]
            if map_send:
                canbus_sacmamx=process_files(3,map_send,self.numero,load_sacmax_canbus,sheet_load='file canbus sacma not need sheet')
            
            map_send=[path_to_files+file for file in self.Litros_sacmamx]
            if map_send:
                litros_sacmamx=process_files(3,map_send,self.numero,load_sacmax_sensores,sheet_load='tanques sacma not need sheet')
                
            print("end load files")
                
            if self.company=='Ubicalo':
                parsed_files= {'Eventos':evenots,'Canbus CAN-BUS':Canbus_ubicalo,'Detalle':Detalle_ubicalo}
                return parsed_files 
          
            if self.company=='Sacmamx':
                parsed_files={'Litros':litros_sacmamx,'Canbus CAN-BUS Sacmax':canbus_sacmamx}
                return parsed_files
        else:
            print('Nothing')
