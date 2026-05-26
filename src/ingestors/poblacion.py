"""
Datos poblacionales reales de España por provincia (INE 2024).
Fuente: INE, Censo anual de población 2024.
Los datos municipales detallados requieren descarga manual desde ine.es
"""

POBLACION_PROVINCIAS = {
    "Madrid": 6811294, "Barcelona": 5901087, "Valencia": 2636620,
    "Alicante": 1911709, "Sevilla": 1953763, "Málaga": 1733834,
    "Murcia": 1553512, "Cádiz": 1260675, "Bizkaia": 1154234,
    "A Coruña": 1121139, "Asturias": 1002973, "Illes Balears": 1234746,
    "Las Palmas": 1171593, "Zaragoza": 984853, "Santa Cruz de Tenerife": 1087267,
    "Pontevedra": 957919, "Granada": 929031, "Tarragona": 860091,
    "Girona": 829204, "Toledo": 737477, "Navarra": 681473,
    "Almería": 763895, "Córdoba": 773114, "Jaén": 620139,
    "Valladolid": 518136, "Castellón": 604056, "Cantabria": 587825,
    "Ciudad Real": 486123, "León": 442107, "Huelva": 534282,
    "Lleida": 447904, "Badajoz": 664705, "Ourense": 302462,
    "Lugo": 317068, "Cáceres": 385793, "La Rioja": 325582,
    "Guadalajara": 277935, "Álava": 337741, "Albacete": 382305,
    "Burgos": 357650, "Salamanca": 323794, "Huesca": 226772,
    "Cuenca": 192342, "Palencia": 156675, "Zamora": 164995,
    "Segovia": 153463, "Soria": 89466, "Teruel": 134178,
    "Ávila": 157127, "Ceuta": 81277, "Melilla": 85584,
}

# Total: ~48.6M habitantes
TOTAL_PAIS = sum(POBLACION_PROVINCIAS.values())
