import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import substring

ruta_shp = r"C:\Users\yolo1\Desktop\Autitos 3\Data San Miguel\Prop_SanMiguel\Prop_SanMiguel.shp" 
gdf_puntos = gpd.read_file(ruta_shp)

if gdf_puntos.crs is None:
    gdf_puntos.set_crs(epsg=4326, inplace=True)
gdf_puntos = gdf_puntos.to_crs(epsg=32719)

nodo_curinanca = Point(-70.6513, -33.4972)
nodo_lazcano = Point(-70.6521, -33.5015)

eje_wgs84 = gpd.GeoSeries([LineString([nodo_curinanca, nodo_lazcano])], crs="EPSG:4326")
eje_utm = eje_wgs84.to_crs(epsg=32719).iloc[0]

distancias = np.arange(0, eje_utm.length, 100)
segmentos_geom = []

for i in range(len(distancias)):
    start = distancias[i]
    end = distancias[i+1] if i + 1 < len(distancias) else eje_utm.length
    segmentos_geom.append(substring(eje_utm, start, end))

gdf_segmentos = gpd.GeoDataFrame(
    {'id_tramo': [f"Tramo {i+1} ({int(distancias[i])}m - {int(end)}m)" for i in range(len(segmentos_geom))]}, 
    geometry=segmentos_geom, 
    crs="EPSG:32719"
)

gdf_buffers = gdf_segmentos.copy()
gdf_buffers['geometry'] = gdf_segmentos.geometry.buffer(20, cap_style=2)

join_espacial = gpd.sjoin(gdf_puntos, gdf_buffers, how='inner', predicate='intersects')
conteo = join_espacial.groupby('id_tramo').size().reset_index(name='n_locales')

gdf_resultados = gdf_segmentos.merge(conteo, on='id_tramo', how='left')
gdf_resultados['n_locales'] = gdf_resultados['n_locales'].fillna(0).astype(int)

max_locales = gdf_resultados['n_locales'].max() or 1
w_logistica, w_peatonal, ancho_acera = 0.60, 0.40, 2.5 

gdf_resultados['ICV'] = ((1 - (gdf_resultados['n_locales'] / max_locales)) * w_logistica) + \
                        ((ancho_acera / 2.5) * w_peatonal)

def clasificar_estado(icv):
    if icv > 0.7: return "Óptimo"
    elif icv > 0.4: return "Saturado"
    else: return "Crítico"

gdf_resultados['Diagnostico'] = gdf_resultados['ICV'].apply(clasificar_estado)

ruta_base = r"C:\Users\yolo1\Desktop\Autitos 3\Data San Miguel\Prop_SanMiguel"
gdf_resultados.to_file(f"{ruta_base}\GranAvenida_Segmentada_ICV.shp")
df_export = gdf_resultados.drop(columns='geometry')
df_export.to_csv(f"{ruta_base}\Tabla_ICV_Hito2.csv", index=False)

print(df_export.to_string(index=False))