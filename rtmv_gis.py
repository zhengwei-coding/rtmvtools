# -*- coding: utf-8 -*-
"""
@author: Zhengwei GUAN
"""

# GIS for rtmv parsing


import folium
import os


if __name__ == "__main__":
    m = folium.Map(location=[45.5236, -122.6750])
    print(m)
    'This is a default'
    m.save('map.html')
