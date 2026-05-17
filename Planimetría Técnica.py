# esto se corrio en Qgis

import math
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsProject, QgsField, QgsSymbol, QgsRendererCategory,
    QgsCategorizedSymbolRenderer
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

layer_name = "Perfil_Gran_Avenida_Situacion_Propuesta"
layer = QgsVectorLayer("Polygon?crs=epsg:32719", layer_name, "memory")
pr = layer.dataProvider()

pr.addAttributes([QgsField("Tipo", QVariant.String)])
layer.updateFields()

x1, y1 = 346627.80, 6293299.11
x2, y2 = 346734.16, 6293795.88

dx = x2 - x1
dy = y2 - y1
L = math.hypot(dx, dy)

ux = dx / L
uy = dy / L

nx = -uy
ny = ux

componentes = [
    ("Acera Peatonal Oriente (2.8m)", 2.8, L, "#A6A6A6"),
    ("Faja de Servicio/Microhub (2.6m)", 2.6, L - 10, "#E67E22"),
    ("Pistas Vehiculares Oriente (6.0m)", 6.0, L, "#737373"),
    ("Pista de Buses Oriente (3.5m)", 3.5, L, "#C0392B"),
    ("Bandejon Central (2.0m)", 2.0, L, "#27AE60"),
    ("Pistas Vehiculares Poniente (6.0m)", 6.0, L, "#737373"),
    ("Pista de Buses Poniente (3.5m)", 3.5, L, "#C0392B"),
    ("Ciclovia Poniente - Parque (2.2m)", 2.2, L, "#2980B9")
]

current_offset = -15.9
categories = []

for nombre, ancho, largo_geom, color_hex in componentes:
    p1_x = x1 + (current_offset * nx)
    p1_y = y1 + (current_offset * ny)
    
    p2_x = p1_x + (largo_geom * ux)
    p2_y = p1_y + (largo_geom * uy)
    
    p3_x = p2_x + (ancho * nx)
    p3_y = p2_y + (ancho * ny)
    
    p4_x = p1_x + (ancho * nx)
    p4_y = p1_y + (ancho * ny)
    
    coords = [
        QgsPointXY(p1_x, p1_y),
        QgsPointXY(p2_x, p2_y),
        QgsPointXY(p3_x, p3_y),
        QgsPointXY(p4_x, p4_y)
    ]
    
    feat = QgsFeature(layer.fields())
    feat.setGeometry(QgsGeometry.fromPolygonXY([coords]))
    feat.setAttribute("Tipo", nombre)
    pr.addFeature(feat)
    
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    symbol.setColor(QColor(color_hex))
    symbol.setOpacity(0.9)
    category = QgsRendererCategory(nombre, symbol, nombre)
    categories.append(category)
    
    current_offset += ancho

layer.updateExtents()
renderer = QgsCategorizedSymbolRenderer("Tipo", categories)
layer.setRenderer(renderer)
QgsProject.instance().addMapLayer(layer)
iface.mapCanvas().zoomToFeatureExtent(layer.extent())