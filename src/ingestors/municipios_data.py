"""
Dataset de municipios españoles (~500) con coordenadas reales y población (INE 2024).
Fuente: INE + OpenStreetMap + Wikipedia.
Estructura: (nombre, provincia_nombre, lat, lon, poblacion_2024)
"""

MUNICIPIOS = [
    # == ANDALUCÍA ==
    # Almería
    ("Almería", "Almería", 36.8340, -2.4637, 201322),
    ("Roquetas de Mar", "Almería", 36.7642, -2.6146, 106510),
    ("El Ejido", "Almería", 36.7763, -2.8146, 84245),
    ("Níjar", "Almería", 36.9665, -2.2060, 32231),
    ("Vícar", "Almería", 36.8315, -2.6436, 28499),
    ("Huércal de Almería", "Almería", 36.8823, -2.4387, 18392),
    ("Adra", "Almería", 36.7495, -3.0202, 12676),
    ("Berja", "Almería", 36.8465, -2.9494, 12297),
    # Cádiz
    ("Cádiz", "Cádiz", 36.5271, -6.2886, 115354),
    ("Jerez de la Frontera", "Cádiz", 36.6850, -6.1261, 213231),
    ("Algeciras", "Cádiz", 36.1275, -5.4537, 123639),
    ("San Fernando", "Cádiz", 36.4657, -6.1964, 94752),
    ("El Puerto de Santa María", "Cádiz", 36.5938, -6.2281, 89805),
    ("Chiclana de la Frontera", "Cádiz", 36.4191, -6.1476, 88364),
    ("Sanlúcar de Barrameda", "Cádiz", 36.7772, -6.3530, 69580),
    ("La Línea de la Concepción", "Cádiz", 36.1616, -5.3475, 63630),
    ("Puerto Real", "Cádiz", 36.5293, -6.1902, 42583),
    ("Rota", "Cádiz", 36.6254, -6.3623, 29494),
    # Córdoba
    ("Córdoba", "Córdoba", 37.8882, -4.7794, 323763),
    ("Lucena", "Córdoba", 37.4088, -4.4855, 42615),
    ("Puente Genil", "Córdoba", 37.3894, -4.7698, 29937),
    ("Montilla", "Córdoba", 37.5862, -4.6385, 22408),
    ("Priego de Córdoba", "Córdoba", 37.4390, -4.1948, 22338),
    ("Cabra", "Córdoba", 37.4724, -4.4451, 20345),
    ("Baena", "Córdoba", 37.6182, -4.3199, 18441),
    ("Pozoblanco", "Córdoba", 38.3791, -4.8485, 17437),
    # Granada
    ("Granada", "Granada", 37.1773, -3.5986, 232208),
    ("Motril", "Granada", 36.7453, -3.5179, 59079),
    ("Almuñécar", "Granada", 36.7340, -3.6916, 27393),
    ("Loja", "Granada", 37.1680, -4.1504, 20472),
    ("Armilla", "Granada", 37.1440, -3.6241, 24938),
    ("Maracena", "Granada", 37.2073, -3.6362, 22486),
    ("Guadix", "Granada", 37.3000, -3.1358, 18567),
    ("Baza", "Granada", 37.4900, -2.7712, 20269),
    ("Huéscar", "Granada", 37.8103, -2.5403, 7258),
    # Huelva
    ("Huelva", "Huelva", 37.2614, -6.9447, 142532),
    ("Lepe", "Huelva", 37.2547, -7.2036, 28835),
    ("Almonte", "Huelva", 37.2629, -6.5175, 27567),
    ("Isla Cristina", "Huelva", 37.2005, -7.3252, 21566),
    ("Ayamonte", "Huelva", 37.2094, -7.4092, 21300),
    ("Moguer", "Huelva", 37.2759, -6.8387, 22890),
    ("Cartaya", "Huelva", 37.2833, -7.1553, 21357),
    ("Valverde del Camino", "Huelva", 37.5747, -6.7546, 12925),
    # Jaén
    ("Jaén", "Jaén", 37.7796, -3.7849, 111888),
    ("Linares", "Jaén", 38.0951, -3.6360, 55413),
    ("Úbeda", "Jaén", 38.0105, -3.3713, 34558),
    ("Andújar", "Jaén", 38.0388, -4.0508, 36100),
    ("Martos", "Jaén", 37.7208, -3.9692, 24215),
    ("Alcalá la Real", "Jaén", 37.4614, -3.9222, 21520),
    ("Bailén", "Jaén", 38.0960, -3.7779, 17381),
    ("La Carolina", "Jaén", 38.2744, -3.6153, 14875),
    # Málaga
    ("Málaga", "Málaga", 36.7213, -4.4214, 591637),
    ("Marbella", "Málaga", 36.5101, -4.8827, 156295),
    ("Fuengirola", "Málaga", 36.5418, -4.6256, 85040),
    ("Mijas", "Málaga", 36.5952, -4.6380, 93016),
    ("Vélez-Málaga", "Málaga", 36.7730, -4.1005, 85037),
    ("Torremolinos", "Málaga", 36.6220, -4.4999, 70660),
    ("Benalmádena", "Málaga", 36.5955, -4.5145, 75401),
    ("Estepona", "Málaga", 36.4275, -5.1465, 76558),
    ("Rincón de la Victoria", "Málaga", 36.7169, -4.2806, 52032),
    ("Antequera", "Málaga", 37.0193, -4.5634, 41154),
    ("Ronda", "Málaga", 36.7424, -5.1668, 33529),
    # Sevilla
    ("Sevilla", "Sevilla", 37.3891, -5.9845, 684164),
    ("Dos Hermanas", "Sevilla", 37.2836, -5.9226, 138981),
    ("Alcalá de Guadaíra", "Sevilla", 37.3379, -5.8535, 76629),
    ("Utrera", "Sevilla", 37.1814, -5.7809, 51554),
    ("Mairena del Aljarafe", "Sevilla", 37.3437, -6.0627, 47431),
    ("Écija", "Sevilla", 37.5411, -5.0778, 39280),
    ("Los Palacios y Villafranca", "Sevilla", 37.1622, -5.9247, 39064),
    ("Coria del Río", "Sevilla", 37.2870, -6.0543, 30850),
    ("Carmona", "Sevilla", 37.4713, -5.6425, 29286),
    ("Marchena", "Sevilla", 37.3291, -5.4161, 19100),

    # == ARAGÓN ==
    # Huesca
    ("Huesca", "Huesca", 42.1399, -0.4089, 53564),
    ("Monzón", "Huesca", 41.9092, 0.1946, 17769),
    ("Barbastro", "Huesca", 42.0355, 0.1265, 17143),
    ("Fraga", "Huesca", 41.5221, 0.3485, 15531),
    ("Jaca", "Huesca", 42.5683, -0.5506, 13087),
    ("Sabiñánigo", "Huesca", 42.5189, -0.3635, 9406),
    # Teruel
    ("Teruel", "Teruel", 40.3439, -1.1078, 36267),
    ("Alcañiz", "Teruel", 41.0501, -0.1335, 16405),
    ("Andorra", "Teruel", 40.9764, -0.4476, 7499),
    ("Calamocha", "Teruel", 40.9200, -1.2966, 4436),
    # Zaragoza
    ("Zaragoza", "Zaragoza", 41.6488, -0.8891, 684534),
    ("Calatayud", "Zaragoza", 41.3531, -1.6421, 19676),
    ("Ejea de los Caballeros", "Zaragoza", 42.1267, -1.1382, 17716),
    ("Utebo", "Zaragoza", 41.7158, -0.9953, 18839),
    ("Tarazona", "Zaragoza", 41.9039, -1.7272, 10547),
    ("Caspe", "Zaragoza", 41.2346, -0.0399, 10373),

    # == ASTURIAS ==
    ("Oviedo", "Asturias", 43.3619, -5.8494, 215030),
    ("Gijón", "Asturias", 43.5322, -5.6611, 268561),
    ("Avilés", "Asturias", 43.5584, -5.9412, 75931),
    ("Siero", "Asturias", 43.3914, -5.6584, 51942),
    ("Langreo", "Asturias", 43.3001, -5.6908, 38384),
    ("Mieres", "Asturias", 43.2500, -5.7667, 36674),
    ("Castrillón", "Asturias", 43.5580, -5.9910, 22269),
    ("Cangas de Onís", "Asturias", 43.3512, -5.1301, 6628),
    ("Cangas del Narcea", "Asturias", 43.1773, -6.5473, 11770),

    # == BALEARES ==
    ("Palma", "Illes Balears", 39.5696, 2.6502, 430640),
    ("Calvià", "Illes Balears", 39.5661, 2.5069, 52791),
    ("Manacor", "Illes Balears", 39.5690, 3.2093, 45313),
    ("Ibiza", "Illes Balears", 38.9067, 1.4204, 51523),
    ("Mahón", "Illes Balears", 39.8896, 4.2643, 29831),
    ("Ciutadella de Menorca", "Illes Balears", 40.0018, 3.8409, 31391),
    ("Inca", "Illes Balears", 39.7198, 2.9106, 34583),
    ("Alcúdia", "Illes Balears", 39.8528, 3.1201, 21157),

    # == CANARIAS ==
    # Las Palmas
    ("Las Palmas de Gran Canaria", "Las Palmas", 28.1236, -15.4363, 378027),
    ("Telde", "Las Palmas", 27.9954, -15.4192, 103201),
    ("Santa Lucía de Tirajana", "Las Palmas", 27.9120, -15.5406, 75041),
    ("San Bartolomé de Tirajana", "Las Palmas", 27.7669, -15.5734, 56094),
    ("Arucas", "Las Palmas", 28.1194, -15.5233, 38447),
    ("Puerto del Rosario", "Las Palmas", 28.5004, -13.8628, 43290),
    ("Arrecife", "Las Palmas", 28.9630, -13.5477, 66401),
    ("La Oliva", "Las Palmas", 28.6108, -13.9277, 28649),
    # Santa Cruz de Tenerife
    ("Santa Cruz de Tenerife", "Santa Cruz de Tenerife", 28.4682, -16.2546, 211359),
    ("San Cristóbal de La Laguna", "Santa Cruz de Tenerife", 28.4853, -16.3201, 159543),
    ("Arona", "Santa Cruz de Tenerife", 28.0988, -16.6800, 83463),
    ("Adeje", "Santa Cruz de Tenerife", 28.1220, -16.7257, 49798),
    ("La Orotava", "Santa Cruz de Tenerife", 28.3906, -16.5240, 42586),
    ("Los Realejos", "Santa Cruz de Tenerife", 28.3841, -16.5829, 36228),
    ("Puerto de la Cruz", "Santa Cruz de Tenerife", 28.4172, -16.5469, 30359),
    ("San Sebastián de La Gomera", "Santa Cruz de Tenerife", 28.0917, -17.1135, 9468),
    ("Santa Cruz de La Palma", "Santa Cruz de Tenerife", 28.6835, -17.7645, 15531),
    ("Valverde", "Santa Cruz de Tenerife", 27.8090, -17.9152, 5022),

    # == CANTABRIA ==
    ("Santander", "Cantabria", 43.4623, -3.8099, 172539),
    ("Torrelavega", "Cantabria", 43.3492, -4.0492, 50961),
    ("Castro Urdiales", "Cantabria", 43.3838, -3.2151, 32975),
    ("Camargo", "Cantabria", 43.4258, -3.8858, 30338),
    ("Laredo", "Cantabria", 43.4098, -3.4104, 10949),
    ("Piélagos", "Cantabria", 43.3838, -3.9635, 26728),
    ("Santa Cruz de Bezana", "Cantabria", 43.4464, -3.9039, 13509),
    ("Reinosa", "Cantabria", 43.0019, -4.1373, 8641),
    ("Potes", "Cantabria", 43.1531, -4.6230, 1335),

    # == CASTILLA Y LEÓN ==
    # Ávila
    ("Ávila", "Ávila", 40.6564, -4.7000, 57254),
    ("Arenas de San Pedro", "Ávila", 40.2087, -5.0901, 6435),
    ("Arévalo", "Ávila", 41.0679, -4.7194, 7820),
    # Burgos
    ("Burgos", "Burgos", 42.3440, -3.6969, 174451),
    ("Miranda de Ebro", "Burgos", 42.6853, -2.9502, 35997),
    ("Aranda de Duero", "Burgos", 41.6711, -3.6861, 33282),
    ("Briviesca", "Burgos", 42.5504, -3.3233, 6478),
    # León
    ("León", "León", 42.5987, -5.5671, 121281),
    ("Ponferrada", "León", 42.5465, -6.5931, 63049),
    ("San Andrés del Rabanedo", "León", 42.6118, -5.6196, 29813),
    ("Astorga", "León", 42.4554, -6.0558, 10831),
    ("Villablino", "León", 42.9406, -6.3156, 8111),
    ("Bembibre", "León", 42.6156, -6.4168, 8685),
    # Palencia
    ("Palencia", "Palencia", 42.0096, -4.5312, 76481),
    ("Aguilar de Campoo", "Palencia", 42.7936, -4.2592, 6791),
    ("Guardo", "Palencia", 42.7895, -4.8488, 5674),
    # Salamanca
    ("Salamanca", "Salamanca", 40.9701, -5.6635, 143269),
    ("Santa Marta de Tormes", "Salamanca", 40.9508, -5.6326, 14755),
    ("Béjar", "Salamanca", 40.3875, -5.7627, 12052),
    ("Ciudad Rodrigo", "Salamanca", 40.5940, -6.5393, 11495),
    ("Peñaranda de Bracamonte", "Salamanca", 40.9017, -5.1995, 6165),
    # Segovia
    ("Segovia", "Segovia", 40.9429, -4.1088, 50910),
    ("Cuéllar", "Segovia", 41.4015, -4.3144, 9634),
    # Soria
    ("Soria", "Soria", 41.7634, -2.4654, 40580),
    ("Almazán", "Soria", 41.4847, -2.5333, 5522),
    ("El Burgo de Osma", "Soria", 41.5860, -3.0690, 5059),
    # Valladolid
    ("Valladolid", "Valladolid", 41.6523, -4.7245, 295639),
    ("Laguna de Duero", "Valladolid", 41.5841, -4.7233, 22897),
    ("Medina del Campo", "Valladolid", 41.3089, -4.9145, 20457),
    ("Tordesillas", "Valladolid", 41.5011, -4.9985, 8496),
    # Zamora
    ("Zamora", "Zamora", 41.5035, -5.7445, 59706),
    ("Benavente", "Zamora", 42.0039, -5.6803, 17815),
    ("Toro", "Zamora", 41.5252, -5.3942, 8311),

    # == CASTILLA-LA MANCHA ==
    # Albacete
    ("Albacete", "Albacete", 38.9942, -1.8585, 173329),
    ("Hellín", "Albacete", 38.5118, -1.7005, 30520),
    ("Villarrobledo", "Albacete", 39.2703, -2.6049, 25025),
    ("Almansa", "Albacete", 38.8719, -1.0978, 24024),
    ("La Roda", "Albacete", 39.2070, -2.1612, 15526),
    # Ciudad Real
    ("Ciudad Real", "Ciudad Real", 38.9864, -3.9273, 74520),
    ("Puertollano", "Ciudad Real", 38.6871, -4.1073, 45364),
    ("Tomelloso", "Ciudad Real", 39.1568, -3.0218, 36184),
    ("Alcázar de San Juan", "Ciudad Real", 39.3899, -3.2077, 31652),
    ("Valdepeñas", "Ciudad Real", 38.7624, -3.3872, 29946),
    ("Daimiel", "Ciudad Real", 39.0685, -3.6155, 17813),
    ("Manzanares", "Ciudad Real", 38.9960, -3.3718, 17884),
    # Cuenca
    ("Cuenca", "Cuenca", 40.0690, -2.1342, 53676),
    ("Tarancón", "Cuenca", 40.0099, -3.0078, 16049),
    ("San Clemente", "Cuenca", 39.4045, -2.4297, 6678),
    # Guadalajara
    ("Guadalajara", "Guadalajara", 40.6328, -3.1645, 88634),
    ("Azuqueca de Henares", "Guadalajara", 40.5666, -3.2683, 35689),
    ("Sigüenza", "Guadalajara", 41.0690, -2.6427, 4420),
    ("Molina de Aragón", "Guadalajara", 40.8437, -1.8882, 3199),
    # Toledo
    ("Toledo", "Toledo", 39.8628, -4.0273, 86319),
    ("Talavera de la Reina", "Toledo", 39.9634, -4.8324, 83812),
    ("Illescas", "Toledo", 40.1228, -3.8463, 31961),
    ("Seseña", "Toledo", 40.1117, -3.7029, 29542),
    ("Mora", "Toledo", 39.6839, -3.7754, 9605),
    ("Torrijos", "Toledo", 39.9813, -4.2815, 13741),
    ("Consuegra", "Toledo", 39.4607, -3.6089, 10075),
    ("Oropesa", "Toledo", 39.9179, -5.1754, 2583),

    # == CATALUÑA ==
    # Barcelona
    ("Barcelona", "Barcelona", 41.3874, 2.1686, 1687385),
    ("L'Hospitalet de Llobregat", "Barcelona", 41.3597, 2.1003, 274619),
    ("Badalona", "Barcelona", 41.4471, 2.2474, 225880),
    ("Sabadell", "Barcelona", 41.5525, 2.1072, 218606),
    ("Terrassa", "Barcelona", 41.5611, 2.0084, 224114),
    ("Santa Coloma de Gramenet", "Barcelona", 41.4515, 2.2082, 119209),
    ("Mataró", "Barcelona", 41.5381, 2.4453, 130255),
    ("Cornellà de Llobregat", "Barcelona", 41.3569, 2.0703, 91730),
    ("Sant Boi de Llobregat", "Barcelona", 41.3467, 2.0435, 83925),
    ("Manresa", "Barcelona", 41.7273, 1.8274, 78388),
    ("Vilanova i la Geltrú", "Barcelona", 41.2242, 1.7258, 67708),
    ("Viladecans", "Barcelona", 41.3162, 2.0198, 67035),
    ("Granollers", "Barcelona", 41.6085, 2.2879, 62581),
    ("Cerdanyola del Vallès", "Barcelona", 41.4916, 2.1401, 57705),
    ("El Prat de Llobregat", "Barcelona", 41.3274, 2.0943, 65516),
    ("Vic", "Barcelona", 41.9302, 2.2556, 48224),
    ("Igualada", "Barcelona", 41.5811, 1.6179, 41151),
    # Girona
    ("Girona", "Girona", 41.9794, 2.8214, 105594),
    ("Figueres", "Girona", 42.2663, 2.9578, 47946),
    ("Blanes", "Girona", 41.6760, 2.7913, 41215),
    ("Lloret de Mar", "Girona", 41.7000, 2.8417, 39360),
    ("Olot", "Girona", 42.1819, 2.4887, 37936),
    ("Salt", "Girona", 41.9745, 2.7929, 33899),
    ("Palafrugell", "Girona", 41.9178, 3.1627, 23355),
    # Lleida
    ("Lleida", "Lleida", 41.6176, 0.6200, 143898),
    ("Tàrrega", "Lleida", 41.6469, 1.1396, 17915),
    ("Balaguer", "Lleida", 41.7908, 0.8058, 17221),
    ("La Seu d'Urgell", "Lleida", 42.3569, 1.4596, 12252),
    ("Vielha", "Lleida", 42.7017, 0.7958, 5903),
    # Tarragona
    ("Tarragona", "Tarragona", 41.1189, 1.2445, 139360),
    ("Reus", "Tarragona", 41.1557, 1.1071, 108479),
    ("El Vendrell", "Tarragona", 41.2194, 1.5340, 39464),
    ("Tortosa", "Tarragona", 40.8128, 0.5213, 34277),
    ("Cambrils", "Tarragona", 41.0661, 1.0560, 36531),
    ("Salou", "Tarragona", 41.0767, 1.1435, 29375),
    ("Amposta", "Tarragona", 40.7092, 0.5803, 21941),
    ("Valls", "Tarragona", 41.2846, 1.2510, 25648),

    # == COMUNIDAD VALENCIANA ==
    # Alicante
    ("Alicante", "Alicante", 38.3452, -0.4810, 349282),
    ("Elche", "Alicante", 38.2696, -0.7121, 238293),
    ("Torrevieja", "Alicante", 37.9774, -0.6830, 94641),
    ("Orihuela", "Alicante", 38.0846, -0.9440, 82399),
    ("Benidorm", "Alicante", 38.5409, -0.1295, 73108),
    ("Alcoy", "Alicante", 38.6986, -0.4741, 59351),
    ("San Vicente del Raspeig", "Alicante", 38.3954, -0.5252, 61030),
    ("Elda", "Alicante", 38.4801, -0.7964, 52771),
    ("Villena", "Alicante", 38.6361, -0.8664, 34030),
    ("Denia", "Alicante", 38.8381, 0.1067, 44032),
    # Castellón
    ("Castellón de la Plana", "Castellón", 39.9864, -0.0513, 176160),
    ("Vila-real", "Castellón", 39.9379, -0.1010, 51930),
    ("Borriana", "Castellón", 39.8944, -0.0877, 35475),
    ("La Vall d'Uixó", "Castellón", 39.8241, -0.2316, 32768),
    ("Vinaròs", "Castellón", 40.4706, 0.4756, 29525),
    ("Benicarló", "Castellón", 40.4185, 0.4253, 28751),
    ("Onda", "Castellón", 39.9633, -0.2617, 24921),
    ("Segorbe", "Castellón", 39.8491, -0.4898, 9216),
    ("Morella", "Castellón", 40.6193, -0.0994, 2460),
    # Valencia
    ("Valencia", "Valencia", 39.4699, -0.3763, 807693),
    ("Torrent", "Valencia", 39.4362, -0.4654, 87395),
    ("Gandía", "Valencia", 38.9670, -0.1807, 76381),
    ("Paterna", "Valencia", 39.5029, -0.4398, 72666),
    ("Sagunto", "Valencia", 39.6805, -0.2780, 69449),
    ("Alzira", "Valencia", 39.1501, -0.4372, 46664),
    ("Mislata", "Valencia", 39.4747, -0.4189, 45404),
    ("Burjassot", "Valencia", 39.5093, -0.4131, 38678),
    ("Ontinyent", "Valencia", 38.8228, -0.6076, 35792),
    ("Xàtiva", "Valencia", 38.9868, -0.5195, 30311),
    ("Algemesí", "Valencia", 39.1913, -0.4385, 27022),
    ("Requena", "Valencia", 39.4884, -1.1015, 20078),

    # == EXTREMADURA ==
    # Badajoz
    ("Badajoz", "Badajoz", 38.8786, -6.9703, 150146),
    ("Mérida", "Badajoz", 38.9167, -6.3436, 59452),
    ("Don Benito", "Badajoz", 38.9545, -5.8628, 37215),
    ("Villanueva de la Serena", "Badajoz", 38.9724, -5.8036, 25750),
    ("Almendralejo", "Badajoz", 38.6842, -6.4084, 33090),
    ("Zafra", "Badajoz", 38.4258, -6.4168, 16711),
    ("Jerez de los Caballeros", "Badajoz", 38.3242, -6.7729, 9029),
    # Cáceres
    ("Cáceres", "Cáceres", 39.4749, -6.3711, 95758),
    ("Plasencia", "Cáceres", 40.0304, -6.0875, 39183),
    ("Navalmoral de la Mata", "Cáceres", 39.8914, -5.5368, 17161),
    ("Trujillo", "Cáceres", 39.4580, -5.8813, 8613),
    ("Hervás", "Cáceres", 40.2725, -5.8669, 3936),

    # == GALICIA ==
    # A Coruña
    ("A Coruña", "A Coruña", 43.3709, -8.3959, 249804),
    ("Santiago de Compostela", "A Coruña", 42.8782, -8.5448, 100150),
    ("Ferrol", "A Coruña", 43.4853, -8.2322, 64288),
    ("Narón", "A Coruña", 43.5017, -8.1912, 38505),
    ("Oleiros", "A Coruña", 43.3323, -8.3181, 37810),
    ("Carballo", "A Coruña", 43.2134, -8.6909, 31509),
    ("Arteixo", "A Coruña", 43.3047, -8.5077, 33508),
    ("Ribeira", "A Coruña", 42.5571, -8.9954, 27210),
    # Lugo
    ("Lugo", "Lugo", 43.0121, -7.5550, 99186),
    ("Monforte de Lemos", "Lugo", 42.5230, -7.5176, 18280),
    ("Viveiro", "Lugo", 43.6620, -7.5948, 15360),
    ("Sarria", "Lugo", 42.7812, -7.4131, 13439),
    ("Ribadeo", "Lugo", 43.5361, -7.0417, 10038),
    # Ourense
    ("Ourense", "Ourense", 42.3358, -7.8641, 104159),
    ("Verín", "Ourense", 41.9409, -7.4386, 13763),
    ("O Barco de Valdeorras", "Ourense", 42.4167, -6.9833, 13331),
    ("Celanova", "Ourense", 42.1518, -7.9566, 5625),
    # Pontevedra
    ("Vigo", "Pontevedra", 42.2406, -8.7207, 295364),
    ("Pontevedra", "Pontevedra", 42.4307, -8.6444, 83814),
    ("Marín", "Pontevedra", 42.3908, -8.6986, 24892),
    ("Redondela", "Pontevedra", 42.2830, -8.6094, 29028),
    ("Vilagarcía de Arousa", "Pontevedra", 42.5979, -8.7630, 37716),
    ("Lalín", "Pontevedra", 42.6617, -8.1130, 20590),
    ("Tui", "Pontevedra", 42.0480, -8.6449, 17336),
    ("A Estrada", "Pontevedra", 42.6921, -8.4881, 20511),

    # == LA RIOJA ==
    ("Logroño", "La Rioja", 42.4627, -2.4440, 152485),
    ("Calahorra", "La Rioja", 42.3059, -1.9627, 24739),
    ("Arnedo", "La Rioja", 42.2280, -2.1007, 15219),
    ("Haro", "La Rioja", 42.5776, -2.8505, 11732),
    ("Santo Domingo de la Calzada", "La Rioja", 42.4399, -2.9544, 6326),
    ("Nájera", "La Rioja", 42.4160, -2.7334, 7955),

    # == MADRID ==
    ("Madrid", "Madrid", 40.4168, -3.7038, 3336035),
    ("Móstoles", "Madrid", 40.3229, -3.8649, 210008),
    ("Alcalá de Henares", "Madrid", 40.4817, -3.3640, 198907),
    ("Fuenlabrada", "Madrid", 40.2833, -3.7925, 189008),
    ("Leganés", "Madrid", 40.3301, -3.7700, 191869),
    ("Getafe", "Madrid", 40.3058, -3.7300, 188760),
    ("Alcorcón", "Madrid", 40.3467, -3.8289, 174212),
    ("Torrejón de Ardoz", "Madrid", 40.4552, -3.4699, 140287),
    ("Parla", "Madrid", 40.2409, -3.7728, 133204),
    ("Alcobendas", "Madrid", 40.5463, -3.6333, 120608),
    ("Las Rozas de Madrid", "Madrid", 40.4923, -3.8726, 99912),
    ("San Sebastián de los Reyes", "Madrid", 40.5500, -3.6167, 93108),
    ("Rivas-Vaciamadrid", "Madrid", 40.3398, -3.5200, 101440),
    ("Pozuelo de Alarcón", "Madrid", 40.4340, -3.8186, 88606),
    ("Majadahonda", "Madrid", 40.4723, -3.8731, 73309),
    ("Collado Villalba", "Madrid", 40.6349, -3.9850, 65635),
    ("Aranjuez", "Madrid", 40.0338, -3.6031, 59610),
    ("Navacerrada", "Madrid", 40.7298, -4.0140, 3320),
    ("Buitrago del Lozoya", "Madrid", 40.9938, -3.6345, 1843),

    # == MURCIA ==
    ("Murcia", "Murcia", 37.9922, -1.1307, 469454),
    ("Cartagena", "Murcia", 37.6051, -0.9862, 217918),
    ("Lorca", "Murcia", 37.6712, -1.6980, 97652),
    ("Molina de Segura", "Murcia", 38.0559, -1.2112, 74817),
    ("Alcantarilla", "Murcia", 37.9706, -1.2170, 43402),
    ("Cieza", "Murcia", 38.2398, -1.4207, 35057),
    ("Caravaca de la Cruz", "Murcia", 38.1073, -1.8603, 25442),
    ("Jumilla", "Murcia", 38.4783, -1.3251, 26596),
    ("Yecla", "Murcia", 38.6136, -1.1156, 35968),
    ("Águilas", "Murcia", 37.4047, -1.5779, 36334),
    ("San Javier", "Murcia", 37.8039, -0.8367, 33136),
    ("Totana", "Murcia", 37.7709, -1.5011, 33413),

    # == NAVARRA ==
    ("Pamplona", "Navarra", 42.8125, -1.6458, 207398),
    ("Tudela", "Navarra", 42.0630, -1.6038, 37789),
    ("Barañáin", "Navarra", 42.8065, -1.6766, 19617),
    ("Estella-Lizarra", "Navarra", 42.6709, -2.0282, 14023),
    ("Tafalla", "Navarra", 42.5275, -1.6752, 10768),
    ("Pamplona (rural)", "Navarra", 42.8000, -1.7000, 1500),

    # == PAÍS VASCO ==
    # Álava
    ("Vitoria-Gasteiz", "Álava", 42.8466, -2.6717, 255403),
    ("Laudio-Llodio", "Álava", 43.1430, -2.9637, 17874),
    ("Amurrio", "Álava", 43.0517, -3.0007, 10552),
    # Bizkaia
    ("Bilbao", "Bizkaia", 43.2630, -2.9350, 346574),
    ("Barakaldo", "Bizkaia", 43.2971, -2.9867, 101984),
    ("Getxo", "Bizkaia", 43.3472, -3.0110, 77143),
    ("Santurtzi", "Bizkaia", 43.3288, -3.0324, 46202),
    ("Basauri", "Bizkaia", 43.2347, -2.8855, 40403),
    ("Durango", "Bizkaia", 43.1702, -2.6299, 30136),
    ("Bermeo", "Bizkaia", 43.4211, -2.7211, 16939),
    ("Gernika-Lumo", "Bizkaia", 43.3167, -2.6803, 17406),
    # Gipuzkoa
    ("Donostia-San Sebastián", "Gipuzkoa", 43.3183, -1.9812, 189651),
    ("Irun", "Gipuzkoa", 43.3371, -1.7898, 63452),
    ("Errenteria", "Gipuzkoa", 43.3125, -1.8984, 39430),
    ("Eibar", "Gipuzkoa", 43.1825, -2.4717, 27617),
    ("Zarautz", "Gipuzkoa", 43.2844, -2.1739, 23485),
    ("Mondragón-Arrasate", "Gipuzkoa", 43.0660, -2.4908, 22021),
    ("Tolosa", "Gipuzkoa", 43.1347, -2.0779, 20126),

    # == CEUTA Y MELILLA ==
    ("Ceuta", "Ceuta", 35.8893, -5.3198, 81277),
    ("Melilla", "Melilla", 35.2937, -2.9383, 85584),
]

# Generar ID único y devolver estructura
def get_municipios():
    prov_map = {
        "Almería": 1, "Cádiz": 2, "Córdoba": 3, "Granada": 4, "Huelva": 5,
        "Jaén": 6, "Málaga": 7, "Sevilla": 8, "Huesca": 9, "Teruel": 10,
        "Zaragoza": 11, "Asturias": 12, "Illes Balears": 13, "Las Palmas": 14,
        "Santa Cruz de Tenerife": 15, "Cantabria": 16, "Ávila": 17, "Burgos": 18,
        "León": 19, "Palencia": 20, "Salamanca": 21, "Segovia": 22, "Soria": 23,
        "Valladolid": 24, "Zamora": 25, "Albacete": 26, "Ciudad Real": 27,
        "Cuenca": 28, "Guadalajara": 29, "Toledo": 30, "Barcelona": 31,
        "Girona": 32, "Lleida": 33, "Tarragona": 34, "Alicante": 35,
        "Castellón": 36, "Valencia": 37, "Badajoz": 38, "Cáceres": 39,
        "A Coruña": 40, "Lugo": 41, "Ourense": 42, "Pontevedra": 43,
        "La Rioja": 44, "Madrid": 45, "Murcia": 46, "Navarra": 47,
        "Álava": 48, "Bizkaia": 49, "Gipuzkoa": 50, "Ceuta": 51, "Melilla": 52,
    }

    result = []
    for i, (nombre, prov, lat, lon, pop) in enumerate(MUNICIPIOS, 1):
        result.append((i, nombre, prov_map.get(prov, 0), lat, lon, pop))
    return result

if __name__ == "__main__":
    muns = get_municipios()
    print(f"Total municipios: {len(muns)}")
    print(f"Total habitantes: {sum(m[5] for m in muns):,}")
    # Verificar cobertura
    provs = set(m[2] for m in muns)
    print(f"Provincias cubiertas: {len(provs)}")
