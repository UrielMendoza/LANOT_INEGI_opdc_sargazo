# Instalador que crea las carpetas y descarga los archivos necesarios para el funcionamiento del programa

import os

# URLs
urls = [
    "http://132.247.103.145/tmp/sargazo/data/masks/land_UTM16N_20m_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_UTM16N_20m_SPlaya_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_2_UTM16N_20m_SPlaya_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_2_UTM16N_20m_SPlaya_b100m_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/playas_UTM16N_20m_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/cuerpos_agua_UTM16N_20m_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_UTM16N_20m_distance.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_UTM16N_20m_2021_b500m.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/land_1_UTM20N_2021.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/MSK_DETFOO_B8A.geojson",
    "http://132.247.103.145/tmp/sargazo/data/masks/MSK_DETFOO_B8A_b1500.geojson"
]

# Verifica si el sistemas e swindows o linux
system = os.name
if system == 'nt':
    system = 'windows'
elif system == 'posix':
    system = 'linux'

# Si es windows
if system == 'windows':
    # Crea las carpetas necesarias
    os.system('mkdir .\\data\\masks\\')
    os.system('mkdir .\\input\\')
    os.system('mkdir .\\output\\')
    os.system('mkdir .\\output\\rgb\\')
    os.system('mkdir .\\output\\rgb\\sargazo\\')
    os.system('mkdir .\\output\\rgb\\TC\\')
    os.system('mkdir .\\output\\sargazo_centroides\\')
    os.system('mkdir .\\output\\sargazo_segmentados\\')
    os.system('mkdir .\\output\\sargazo_vertices\\')
    os.system('mkdir .\\tmp\\')

    # Descarga los archivos necesarios
    for url in urls:
        os.system(f'curl -o ./data/masks/{url.split("/")[-1]} {url}')
    
    # Descarga el archivo de prueba de entrada
    os.system('curl -o ./input/S2A_MSIL2A_20230521T160831_N9999_R140_T16QEJ_20230522T020259.zip http://132.247.103.145/tmp/sargazo/INEGI_ODC_sargazo/sargazo_test/S2A_MSIL2A_20230521T160831_N9999_R140_T16QEJ_20230522T020259.zip')

# Si es linux
elif system == 'linux':
    # Crea las carpetas necesarias
    os.system('mkdir -p ./data/masks/')
    os.system('mkdir -p ./input/')
    os.system('mkdir -p ./output/')
    os.system('mkdir -p ./output/rgb/')
    os.system('mkdir -p ./output/rgb/sargazo/')
    os.system('mkdir -p ./output/rgb/TC/')
    os.system('mkdir -p ./output/sargazo_centroides/')
    os.system('mkdir -p ./output/sargazo_segmentados/')
    os.system('mkdir -p ./output/sargazo_vertices/')
    os.system('mkdir -p ./tmp/')

    # Descarga los archivos necesarios
    for url in urls:
        os.system(f'wget -O ./data/masks/{url.split("/")[-1]} {url}')

    # Descarga el archivo de prueba de entrada
    os.system('wget -O ./input/S2A_MSIL2A_20230521T160831_N9999_R140_T16QEJ_20230522T020259.zip http://132.247.103.145/tmp/sargazo/INEGI_ODC_sargazo/sargazo_test/S2A_MSIL2A_20230521T160831_N9999_R140_T16QEJ_20230522T020259.zip')



