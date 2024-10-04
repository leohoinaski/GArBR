# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:45:51 2024

@author: Camilo Bastos Ribeiro
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.ops import unary_union


###dados de entrada###

#gdf_pop = gpd com população geolocalizada (epsg=5880)
#gdf_aqs = gdf com estações geolocalizadas (epsg=5880)
#gdf_states = gdf com estados do Brasil (epsg=5880)
#buffer defalt = 5000m

#%%

###cobertura de cada tipo de estação (Brasil)###

#função calcula o percentual da população coberta pelas estações (por tipo)
#em relação ao total da população no Brasil

def aqs_pop_cover(gdf_aqs, gdf_pop, buffer_dist=5000):
    results = []
    pop_total = gdf_pop['PopResid'].sum()
    
    for tipo in gdf_aqs['Tipo'].unique():
        gdf_aqs_tipo = gdf_aqs[gdf_aqs['Tipo'] == tipo]
        gdf_aqs_tipo['buffer'] = gdf_aqs_tipo.geometry.buffer(buffer_dist)
        buffers_dissolved = gdf_aqs_tipo['buffer'].unary_union
        gdf_pop_within = gdf_pop[gdf_pop.geometry.within(buffers_dissolved)]
        pop_within = gdf_pop_within['PopResid'].sum()
        pop_perc_within = (pop_within / pop_total) * 100
        
        results.append({
            'Tipo': tipo,
            'pop_total': pop_total,
            'pop_cover': pop_within,
            '%_pop_cover': pop_perc_within
        })

    return pd.DataFrame(results)

###cobertura de estação por tipo e por estado###

#função calcula o percentual da população coberta pelas estações (por tipo)
#em relação ao total da população em cada estado no Brasil

def aqs_pop_cover_state(gdf_aqs, gdf_pop, gdf_states, buffer_dist=5000):
    
    results = []
    gdf_aqs['buffer'] = gdf_aqs.geometry.buffer(buffer_dist)
    
    for idx, state in gdf_states.iterrows():
        state_name = state['HASC_1']
        state_geom = state['geometry']
        gdf_pop_state = gdf_pop[gdf_pop.geometry.within(state_geom)]
        gdf_aqs_state = gdf_aqs[gdf_aqs.geometry.within(state_geom)]
        pop_total_state = gdf_pop_state['PopResid'].sum() if not gdf_pop_state.empty else 0
        
        print(state)

        if not gdf_aqs_state.empty:
            tipos_presentes = gdf_aqs_state['Tipo'].unique().tolist()
            for tipo in ['Indicativa', 'Referência']:
                if tipo in tipos_presentes:
                    gdf_aqs_tipo = gdf_aqs_state[gdf_aqs_state['Tipo'] == tipo]
                    buffers_dissolved = gdf_aqs_tipo['buffer'].unary_union
                    gdf_pop_within = gdf_pop_state[gdf_pop_state.geometry.within(buffers_dissolved)]
                    pop_within_buffers = gdf_pop_within['PopResid'].sum() if not gdf_pop_within.empty else 0
                    
                    pop_perc_within_buffers = (pop_within_buffers / pop_total_state * 100) if pop_total_state > 0 else 0
                else:
                    pop_within_buffers = 0
                    pop_perc_within_buffers = 0
                
                results.append({
                    'state': state_name,
                    'tipo': tipo,
                    'pop_total': pop_total_state,
                    'pop_cover': pop_within_buffers,
                    '%_pop_cover': pop_perc_within_buffers
                })
        else:
            for tipo in ['Indicativa', 'Referência']:
                results.append({
                    'state': state_name,
                    'tipo': tipo,
                    'pop_total': pop_total_state,
                    'pop_cover': 0,
                    '%_pop_cover': 0
                })
    
    return pd.DataFrame(results)