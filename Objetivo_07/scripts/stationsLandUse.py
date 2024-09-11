#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:45:33 2024

@author: leohoinaski
"""

import os
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
#import matplotlib.pyplot as plt
import rasterio as rs
import rasterio.mask
import numpy as np


file = 'Monitoramento_QAr_BR_latlon_2024.csv'
bufferSize = 5000
year = 2022


def stationBuffers(file,bufferSize): 
    rootDir = os.path.dirname(os.getcwd())
    inputFolder = rootDir+'/inputs'
    df = pd.read_csv(inputFolder+'/'+file)
    geometry = [Point(xy) for xy in zip(df.LONGITUDE, df.LATITUDE)]
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    gdf = gdf.set_crs(4326, allow_override=True)
    gdfMeter = gpd.GeoDataFrame(gdf, crs=4326).to_crs('EPSG:3857')
    gdfBuffer = gdfMeter.buffer(bufferSize)
    gdfBuffer = gdfBuffer.to_crs('EPSG:4326')
    gdf['buffer'] = gdfBuffer
    gdf = gdf.drop_duplicates(subset=['geometry'])
    return gdf

def stationUnionByUF(gdf):
    stationInUF=[]
    for index, uf in enumerate(gdf['ESTADO'].unique()):
       stationInUF.append(gdf['buffer'][gdf['ESTADO']==uf].unary_union)
       
    stationInUF = pd.DataFrame(stationInUF,columns=["geometry"])   
    stationInUF = gpd.GeoDataFrame(stationInUF, geometry=stationInUF['geometry'],
                                   crs="EPSG:4326")
    stationInUF['ESTAÇÃO'] = gdf['ESTADO'].unique()
    stationInUF['buffer'] = stationInUF['geometry'].copy() 
    
    return stationInUF

def cutMapbiomas(gdf,year,prefix):
    """
    Esta função é utilizada para cortar o arquivo do Mapbiomas para o domínio 
    de modelagem. Se o domínio for muito grande, ela simplesmente lê o arquivo
    original sem cortar. 
    
    FUNÇÃO NÃO ESTÁ SENDO UTILIZADA NA VERSÃO ATUAL

    Parameters
    ----------
    domainShp : geodataframe
        Geodataframe com a geometria do domínio de modelagem.
    inputFolder : path
        Caminho para a pasta de inputs.
    outfolder : path
        Caminho para a pasta de outputs.
    year : int
        Ano de referência para a modelagem.
    GRDNAM : str
        Nome da grade de modelagem de acordo com o MCIP.

    Returns
    -------
    out_meta : rasterio
        Detalhes do raster.
    arr : rasterio
        Array do raster.

    """
    rootDir = os.path.dirname(os.getcwd())
    inputFolder = rootDir+'/inputs'
    outfolder = rootDir+'/outputs/mapbiomas'
    os.makedirs(outfolder, exist_ok=True)
    
    dfLegend = pd.read_csv(inputFolder+'/mapbiomasLegend.csv')
    
    for dl in dfLegend['Code ID']:
        gdf[str(dl)] = np.nan  


    for index, row in gdf.iterrows():
        # Abrindo o arquivo do MAPBIOMAS
        with rs.open(inputFolder+'/brasil_coverage_'+str(year)+'.tif') as src:
    
            # Tenta abrir e cortar o arquivo. Se for muito grande, não cortará e passará
            # para o except
            #  Abrindo raster e cortando
            try:
                out_image, out_transform = rasterio.mask.mask(src,[row.buffer],
                                                              crop=True)
            except:
                out_image, out_transform = rasterio.mask.mask(src,[row.geometry],
                                                              crop=True)
            # Extraindo propriedades do raster
            out_meta = src.meta
            out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
            # Se conseguir recortar...
            if out_meta:   
                # Abre um novo arquvio e salva na pasta de outputs recortado
                with rs.open(outfolder+'/mapbiomas_'+row['ESTAÇÃO'].replace('/','')+'.tif', "w", **out_meta) as dest:
                    dest.write(out_image)

     
            values, counts = np.unique(out_image.flatten(), return_counts=True)
            for ii,val in enumerate(values):
                if val!=0:
                    gdf.loc[index,gdf.columns[gdf.columns==str(val)]] = counts[ii]
    #gdf.to_csv(outfolder+'/stationsLandUse.csv') 
    gdf = gdf.drop(columns=['geometry'])         
    gdf.to_csv(outfolder+'/'+prefix+'stationsLandUse.csv',)
    gdf = gdf.drop(columns=['buffer']) 
    gdf.to_csv(outfolder+'/'+prefix+'stationsLandUseNoGeometry.csv') 
    return gdf

def cutMapbiomasSimple(gdf,year):
    """
    Esta função é utilizada para cortar o arquivo do Mapbiomas para o domínio 
    de modelagem. Se o domínio for muito grande, ela simplesmente lê o arquivo
    original sem cortar. 
    
    FUNÇÃO NÃO ESTÁ SENDO UTILIZADA NA VERSÃO ATUAL

    Parameters
    ----------
    domainShp : geodataframe
        Geodataframe com a geometria do domínio de modelagem.
    inputFolder : path
        Caminho para a pasta de inputs.
    outfolder : path
        Caminho para a pasta de outputs.
    year : int
        Ano de referência para a modelagem.
    GRDNAM : str
        Nome da grade de modelagem de acordo com o MCIP.

    Returns
    -------
    out_meta : rasterio
        Detalhes do raster.
    arr : rasterio
        Array do raster.

    """
    rootDir = os.path.dirname(os.getcwd())
    inputFolder = rootDir+'/inputs'
    outfolder = rootDir+'/outputs/mapbiomas'
    os.makedirs(outfolder, exist_ok=True)
    
    dfLegend = pd.read_csv(inputFolder+'/mapbiomasLegend.csv')
    
    for dl in dfLegend['Code ID']:
        gdf[str(dl)] = np.nan  


    for index, row in gdf.iterrows():
        # Abrindo o arquivo do MAPBIOMAS
        with rs.open(inputFolder+'/brasil_coverage_'+str(year)+'.tif') as src:
    
            # Tenta abrir e cortar o arquivo. Se for muito grande, não cortará e passará
            # para o except
            #  Abrindo raster e cortando
            try:
                out_image, out_transform = rasterio.mask.mask(src,[row.buffer],
                                                              crop=True)
            except:
                out_image, out_transform = rasterio.mask.mask(src,[row.geometry],
                                                              crop=True)
            # Extraindo propriedades do raster
            out_meta = src.meta
            out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

            values, counts = np.unique(out_image.flatten(), return_counts=True)
            for ii,val in enumerate(values):
                if val!=0:
                    gdf.loc[index,gdf.columns[gdf.columns==str(val)]] = counts[ii]      
    gdf.to_csv(outfolder+'/UFLandUse.csv') 
    return gdf

def UFstatistics(gdfUFstations,UFshapePath):
    ufShape = gpd.read_file(UFshapePath)
    gdfUF=[]
    for index, row in gdfUFstations.iterrows():
        gdfUF.append(cutMapbiomasSimple(ufShape[ufShape.UF==row['ESTAÇÃO']],year))
    gdfUF=pd.DataFrame(gdfUF)
    gdfUF = pd.DataFrame(gdfUF,columns=["geometry"]) 
    return gdfUF



gdf = stationBuffers(file,bufferSize,)

stationInUF = stationUnionByUF(gdf)

gdf = cutMapbiomas(gdf,year,'')

gdfUFstations = cutMapbiomas(stationInUF,year,'UF')

    
UFshapePath = '/media/leohoinaski/HDD/shapefiles/Brasil.shp'

gdfUF = UFstatistics(gdfUFstations,UFshapePath)