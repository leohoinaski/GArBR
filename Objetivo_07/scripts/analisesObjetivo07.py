# -*- coding: utf-8 -*-

"""
Created on Wed Aug 28 17:30:30 2024

@author: Camilo Bastos Ribeiro
"""

#fonte shapefiles do Brasil:
#https://gadm.org/download_country_v3.html

#fonte shapefile de areas urbanas:
#https://www.ibge.gov.br/geociencias/cartas-e-mapas/redes-geograficas/15789-areas-urbanizadas.html?=&t=downloads

#fonte de dados (compilados e padronizados) com a localização das estações de monitoramento no BR:
#https://onedrive.live.com/?id=5BFEEDBF4F33F40C%21194731&cid=5BFEEDBF4F33F40C

#importanto bibliotecas
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.ops import unary_union


def aqs_sm_plot(gdf_BR, gdf_var, column, cmap='coolwarm_r'):
    """
    Função para plotar um mapa com as estações de monitoramento do Brasil.
    
    Parâmetros:
    - gdf_BR: GeoDataFrame com geometria do Brasil.
    - gdf_var: GeoDataFrame contendo as estações de monitoramento geolocalizadas.
    - column: Nome da coluna do gdf_var a ser usada para a coloração do mapa.
    - cmap: Colormap para personalizar a visualização (padrão: 'coolwarm_r').
    """    
    
    plt.figure(figsize=(8,6))
    ax = plt.gca()
    gdf_BR.plot(ax=ax, color='silver', linewidth=.5, edgecolor='w')
    gdf_var.plot(column, ax=ax, cmap=cmap, marker='o', markersize=2, legend=True,
                 legend_kwds={'fontsize': 6, 'frameon': False,
                              'loc': 'lower left', 'bbox_to_anchor': (.13, .35)})
    plt.axis('off')
    plt.show()
    

def aqs_mm_plot(gdf_BR, gdf_vars, columns_cmap):
    """
    Função para plotar subplots com múltiplas colunas.
        *pode ser adotada para plotar mapas com o tipo ou status da estação*
 
    Parâmetros:
    - gdf_BR: GeoDataFrame com a geometria do Brasil.
    - gdf_vars: GeoDataFrame com as estações de monitoramento geolocalizadas.
    - columns_cmap: Dicionário onde as chaves são as colunas a serem plotadas 
    e os valores são os colormaps correspondentes.
    """

    num_cols = len(columns_cmap)
    num_rows = 2
    
    # Labels para as subplots (a), (b), (c), ...
    labels = [f"({chr(97 + i)})" for i in range(num_cols)]    

    fig, axs = plt.subplots(num_rows, 1, figsize=(7,6), constrained_layout=True)
    axs = axs.flatten()
    for i, (column, cmap) in enumerate(columns_cmap.items()):
        
        # Plotando o mapa base
        gdf_BR.plot(ax=axs[i], color='gainsboro',linewidth=.4, edgecolor='w')
        
        # Plotando os dados geo_aqs baseados na coluna escolhida e cmap correspondente
        gdf_vars.plot(column, ax=axs[i], cmap=cmap, marker='o', markersize=1, legend=True,
                     legend_kwds={'fontsize': 6, 'frameon': False,
                                  'loc': 'lower left', 'bbox_to_anchor': (-0.04, .3)})
        axs[i].axis('off')
        axs[i].set_title(labels[i], fontsize=7)

    # Desativando os eixos vazios se o número de plots for ímpar
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    plt.show()


def aqs_number_plot(data, column, title_left, title_right, color_left='Blue', color_right='Red'):
    """
    Função para gerar dois gráficos de barras comparando o número de estações por estado
    com base em uma coluna categórica (ex: tipo de estação ou status).

    Parâmetros:
    - data: DataFrame contendo os dados das estações de monitoramento, incluindo a coluna de estado.
    - column: Nome da coluna categórica utilizada para filtrar os dados (deve ter dois valores únicos).
    - title_left: Título para o gráfico à esquerda.
    - title_right: Título para o gráfico à direita.
    - color_left: Cor para as barras no gráfico à esquerda (padrão: 'Blue').
    - color_right: Cor para as barras no gráfico à direita (padrão: 'Red').

    O gráfico à esquerda representa a primeira categoria, e o gráfico à direita representa a segunda.

    Retorno:
    - Um gráfico com dois subplots comparando o número de estações por estado para cada valor
      único da coluna categórica fornecida.
    """
    
    # Filtrgem dados por categoria
    unique_values = data[column].unique()
    value1, value2 = unique_values

    # Filtragem dos dados com base nos valores únicos da coluna
    subset1 = data[data[column] == value1]
    subset2 = data[data[column] == value2]

    # Contagem do número de estações por estado
    count1 = subset1['ESTADO'].value_counts().reset_index()
    count1.columns = ['Estado', 'Estacoes']

    count2 = subset2['ESTADO'].value_counts().reset_index()
    count2.columns = ['Estado', 'Estacoes']

    # Criação de subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

    # Plot para a primeira categoria
    sns.barplot(x='Estado', y='Estacoes', data=count1, color=color_left, ax=axes[0],
                edgecolor='silver',linewidth=1.5)
    axes[0].set_title('(a)', fontsize=17)
    axes[0].set_xlabel('Estado', fontsize=17)
    axes[0].set_ylabel('Número de estações', fontsize=17)
    axes[0].tick_params(axis='x', labelsize=17,rotation=0)
    axes[0].tick_params(axis='y', labelsize=17)

    # Plot para a segunda categoria
    sns.barplot(x='Estado', y='Estacoes', data=count2, color=color_right, ax=axes[1],
                edgecolor='silver',linewidth=1.5)
    axes[1].set_title('(b)', fontsize=17)
    axes[1].set_xlabel('Estado', fontsize=17)
    axes[1].set_ylabel('Número de estações', fontsize=17)
    axes[1].tick_params(axis='x', labelsize=17,rotation=0)
    axes[1].tick_params(axis='y', labelsize=17)

    plt.tight_layout()
    plt.show()


def aqs_cover_br(gdf_aqs, gdf_BR, buffer_dist=5000):
    """
    Função para criar buffers de 5km ao redor das estações, 
    calcular a área total dos buffers de estações (subtraindo as áreas sobrepostas),
    e calcular o percentual de cobertura em relação à área total do Brasil.

    Parâmetros:
    - gdf_aqs: GeoDataFrame contendo as estações de monitoramento.
    - gdf_BR: GeoDataFrame representando a área total do Brasil.
        *pode ser usado outro gdf (ex: área urbana ou tipo de uso do solo)*
    - buffer_dist: Distância do buffer em metros (padrão é 5000 metros).
    
    Retorna:
    - DataFrame com as áreas totais (em km²) e percentuais de cobertura.
    """
    
    # Criação dos buffers de 5 km ao redor de cada ponto
    gdf_aqs['buffer'] = gdf_aqs.geometry.buffer(buffer_dist)
    
    # Criação do buffer ao redor da geometria se não for polígono
    if gdf_BR.geometry.type.isin(['Point', 'MultiPoint']).any():
        gdf_BR['geometry'] = gdf_BR.geometry.buffer(5)
        
    # Unificação das geometrias    
    gdf_BR_unified = unary_union(gdf_BR.geometry)
    
    # Separação dos buffers por tipo de estação
    ref_buffers = gdf_aqs[gdf_aqs['Tipo'] == 'Referência']['buffer']
    ind_buffers = gdf_aqs[gdf_aqs['Tipo'] == 'Indicativa']['buffer']
    
    # Dissolver os buffers para remover as áreas sobrepostas
    ref_dissolved = ref_buffers.unary_union
    ind_dissolved = ind_buffers.unary_union
    
    # Calculo da área total dos buffers (em km²)
    ref_area = ref_dissolved.area / 1e6
    ind_area = ind_dissolved.area / 1e6
    
    # Calculo da área total do Brasil (em km²)
    br_area = gdf_BR_unified.area / 1e6
    
    # Calculo do percentual de cobertura em relação ao Brasil
    ref_perc = (ref_area / br_area) * 100
    ind_perc = (ind_area / br_area) * 100
    
    # Retorno dos resultados
    return pd.DataFrame({
        'area_tot': [br_area],
        'area_ref': [ref_area],
        'area_ind': [ind_area],
        '%_ref': [ref_perc],
        '%_ind': [ind_perc]
    })


def urban_area_by_state(gdf_urban, gdf_states):
    """
    Função para calcular a área urbana dentro de cada estado no Brasil.

    Parâmetros:
    - gdf_urban: GeoDataFrame representando as áreas urbanas do Brasil.
    - gdf_states: GeoDataFrame representando os estados do Brasil.

    Retorna:
    - GeoDataFrame com o polígono unificado da área urbana para cada estado.
    """
    
    # Criação de uma lista para armazenar os resultados
    results = []
    
    for _, state in gdf_states.iterrows():
        state_geom = state['geometry']
        state_name = state['HASC_1']
        
        # Filtragem de áreas urbanas que intersectam o estado
        urban_in_state = gdf_urban[gdf_urban.intersects(state_geom)]
        
        # Interseção das áreas urbanas com o polígono do estado
        urban_in_state = urban_in_state.copy()
        urban_in_state['geometry'] = urban_in_state['geometry'].intersection(state_geom)
        
        # Unificação das áreas urbanas dentro do estado
        urban_union = urban_in_state.unary_union
        
        # Add o resultado
        results.append({
            'Estado': state_name,
            'geometry': urban_union
        })
        
        print(state)
    
    # Criação de GeoDataFrame com os resultados
    gdf_result = gpd.GeoDataFrame(results, geometry='geometry', crs=gdf_states.crs)
    
    return gdf_result


def aqs_cover_state(gdf_aqs, gdf_states, column, buffer_dist=5000):
    """
    Função para calcular a área de cobertura dos buffers ao redor das estações em relação à área
    de cada estado, considerando um buffer de raio fixo de 5 km.

    Parâmetros:
    - gdf_aqs: GeoDataFrame contendo as estações de monitoramento.
    - gdf_states: GeoDataFrame representando os estados do Brasil.
        *pode ser usado outro gdf (ex: área urbana ou tipo de uso do solo)*
    - buffer_dist: Distância do buffer em metros (padrão é 5000 metros).
    
    Retorna:
    - DataFrame com áreas de cobertura dos buffers para cada estado e percentuais de cobertura.
    """
    
    # Criação dos buffers ao redor de cada ponto
    gdf_aqs['buffer'] = gdf_aqs.geometry.buffer(buffer_dist)
    
    # Dissolvendo os buffers para remover as áreas sobrepostas
    ref_buffers = gdf_aqs[gdf_aqs['Tipo'] == 'Referência']['buffer']
    ind_buffers = gdf_aqs[gdf_aqs['Tipo'] == 'Indicativa']['buffer']
    
    ref_dissolved = ref_buffers.unary_union
    ind_dissolved = ind_buffers.unary_union
    
    # Inicialização do DataFrame para armazenar os resultados
    results = []

    for _, state in gdf_states.iterrows():
        state_geom = state['geometry']
        state_name = state[column]
        
        # Interseção dos buffers com o estado
        ref_intersection = ref_dissolved.intersection(state_geom)
        ind_intersection = ind_dissolved.intersection(state_geom)
        
        # Calculo das áreas de cobertura dentro do estado
        if isinstance(ref_intersection, gpd.geoseries.GeoSeries):
            ref_area = ref_intersection.area.sum() / 1e6
        else:
            ref_area = ref_intersection.area / 1e6
        
        if isinstance(ind_intersection, gpd.geoseries.GeoSeries):
            ind_area = ind_intersection.area.sum() / 1e6
        else:
            ind_area = ind_intersection.area / 1e6
        
        # Calculo da área total do estado (em km²)
        state_area = state_geom.area / 1e6
        
        # Calculo do percentual de cobertura
        ref_perc = (ref_area / state_area) * 100
        ind_perc = (ind_area / state_area) * 100
        
        #Armazenando resultados
        results.append({
            'Estado': state_name,
            'Ref_Area': ref_area,
            'Ind_Area': ind_area,
            'Estado_Area': state_area,
            'Ref_%': ref_perc,
            'Ind_%': ind_perc
        })
    
    return pd.DataFrame(results)