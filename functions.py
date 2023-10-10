from glob import glob
import datetime
from xml.dom import minidom
from osgeo import gdal, osr
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Polygon, Point, MultiPoint, MultiPolygon
import numpy as np
import zipfile
import shutil
from skimage.filters.rank import entropy
from skimage.morphology import disk

def tipoCompresion(pathInput):
    '''
    Funcion que verifca el tipo de compresion de la imagen Sentinel-2

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    '''
    compresion = pathInput.split('/')[-1].split('.')[-1]
    return compresion

def descomprime(pathInput,pathOutput):
    '''
    Funcion para descomprimir archivos .gz y .zip con linux

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2 comprimidas
    '''
    compresion = tipoCompresion(pathInput) 
    if compresion == 'gz':
        os.system('tar -xvzf '+pathInput+' -C '+pathOutput)
    elif compresion == 'zip':
        system = os.name
        if system == 'nt':
            # Descomprimir el archivo ZIP
            with zipfile.ZipFile(pathInput, 'r') as zip_ref:
                # Extraer todo el contenido en la carpeta de destino
                zip_ref.extractall(pathOutput)
        elif system == 'posix':
            os.system('unzip '+pathInput+' -d '+pathOutput)
def listaArchivos(pathInput):
    '''
    Funcion para enlistar archivos de un directorio

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    '''
    archivos = glob(pathInput)
    return archivos

def nomDir(pathInput,nivel):
    '''
    Funcion que obtiene el nombre de Sentinel-2

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    nivel : str
        Nivel de procesamiento de Sentinel-2
    '''
    system = os.name
    if system == 'nt':
        archivo = pathInput.split('\\')[-1].split('.')[0]
    elif system == 'posix':
        archivo = pathInput.split('/')[-1].split('.')[0]
    if nivel == 'L2A':
        return archivo+'.SAFE'
    elif nivel == 'L1C':
        return archivo+'.SAFE'
    elif nivel == 'L1C_resampled':
        return archivo+'.resampled.data'
    
def obtieneFecha(pathDir):
    '''
    Funcion que obtiene la fecha de la imagen Sentinel-2

    Parametros
    ----------
    pathDir : str
        Path de entrada de imagenes Sentinel-2
    '''
    fecha = pathDir.split('/')[-1].split('.')[0].split('_')[2]
    fecha = datetime.datetime.strptime(fecha,'%Y%m%dT%H%M%S')
    return fecha.strftime('%Y%m%dT%H%M%S')

def obtieneFechaImaProc(pathDir):
    '''
    Funcion que obtiene la fecha de procesamiento de la imagen Sentinel-2

    Parametros
    ----------
    pathDir : str
        Path de entrada de imagenes Sentinel-2
    '''
    fecha = pathDir.split('/')[-1].split('.')[0].split('_')[-1]
    #fecha = datetime.datetime.strptime(fecha,'%Y%m%dT%H%M%S')
    return fecha

def obtieneTile(pathArchivo):
    '''
    Funcion que obtiene el tile de la imagen

    Parametros
    ----------
    pathArchivo : str
        Path de entrada de imagenes Sentinel-2
    '''
    tile = pathArchivo.split('/')[-1].split('_')[5]
    return tile

def obtieneAnio(pathArchivo):
   '''
   Funcion que obtiene el anio de la imagen

    Parametros
    ----------
    pathArchivo : str
        Path de entrada de imagenes Sentinel-2
   '''
   anio = pathArchivo.split('/')[-1].split('_')[2][:4]
   return anio

def obtienePorcentajeNube(pathInput):
    '''
    Funcion que obtiene el porcentaje de nubes de la imagen 
    a partir del archivo MTD_MSIL2A.xml

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    '''
    system = os.name
    if system == 'nt':
        mydoc = minidom.parse(pathInput+'\\MTD_MSIL2A.xml')
    elif system == 'posix':
        mydoc = minidom.parse(pathInput+'/MTD_MSIL2A.xml')
    items = mydoc.getElementsByTagName('n1:Quality_Indicators_Info')
    porcNube = float(items[0].getElementsByTagName('Cloud_Coverage_Assessment')[0].firstChild.nodeValue)
    return porcNube

def listaBandas(pathInput,nivel,resolucion,banda):
    '''
    Funcion que lista las bandas de acuerdo al nivel y banda

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    nivel : str
        Nivel de procesamiento de Sentinel-2
    resolucion : str
        Resolucion de la banda
    banda : str
        Banda de Sentinel-2
    '''
    if nivel == 'L2A':
        archivoBanda = glob(pathInput+'/GRANULE/L2*/IMG_DATA/'+resolucion+'/*'+banda+'*.jp2')
    elif nivel == 'L1C':
        archivoBanda = glob(pathInput+'/GRANULE/L1C*/IMG_DATA/*.jp2')
    elif nivel == 'L1C_resampled':
        archivoBanda = glob(pathInput+'/'+banda+'.img')
    print("Archivo usado:"+archivoBanda[0])
    return archivoBanda[0]

def aperturaDS(pathBand):
    '''
    Funcion que abre un archivo raster con GDAL

    Parametros
    ----------
    pathBand : str
        Path de entrada de imagenes Sentinel-2
    '''
    ds = gdal.Open(pathBand)
    return ds

def imgToGeoTIF(ds,tif,pathOutput):
    '''
    Funcion que convierte una imagen a GeoTIF con GDAL

    Parametros
    ----------
    ds : str
        Dataset de GDAL
    tif : str
        Nombre del archivo GeoTIF
    pathOutput : str
        Path de salida de imagenes GeoTIF
    '''
    print("Pasando a tif: "+pathOutput+tif+'.tif')
    gdal.Translate(pathOutput+tif+'.tif',ds)

def creaTif(dsRef,npy,output):
    '''
    Funcion que crea un GeoTIF a partir de un arreglo de numpy

    Parametros
    ----------
    dsRef : str
        Dataset de referencia de GDAL
    npy : str
        Arreglo de numpy
    output : str
        Path de salida de imagenes GeoTIF
    '''
    geotransform = dsRef.GetGeoTransform()
    nx = dsRef.RasterXSize
    ny = dsRef.RasterYSize
    dst_ds = gdal.GetDriverByName('GTiff').Create(output, ny, nx, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(dsRef.GetProjectionRef())
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).WriteArray(npy)
    dst_ds.FlushCache()
    dst_ds = None

def remuestrea(pathOutput,ds,dimx,dimy):
    '''
    Funcion que remuestrea una imagen con GDAL

    Parametros
    ----------
    pathOutput : str
        Path de salida de imagenes GeoTIF
    ds : str
        Dataset de GDAL
    dimx : int
        Dimension en x
    dimy : int 
        Dimension en y
    '''
    gdal.Translate(pathOutput,ds,options=gdal.TranslateOptions(xRes=dimx,yRes=dimy))

def obtieneCuadrante(ds):
    '''
    Funcion que obtiene el cuadrante de la imagen don un dataset de GDAL

    Parametros
    ----------
    ds : str
        Dataset de GDAL
    '''
    xSize = ds.RasterXSize
    ySize = ds.RasterYSize
    geo = ds.GetGeoTransform()
    xmin = geo[0]
    ymax = geo[3]
    xres = geo[1]
    yres = geo[5]
    xmax = xmin + xres*xSize
    ymin = ymax + yres*ySize

    return [xmin,ymax,xmax,ymin]

def obtieneParametrosGeoTrasform(ds):
    '''
    Funcion que obtiene los parametros de geotransformacion de un dataset de GDAL

    Parametros
    ----------
    ds : str
        Dataset de GDAL
    '''
    geo = ds.GetGeoTransform()
    nx = ds.RasterXSize
    ny = ds.RasterYSize
    xmin = geo[0]
    ymax = geo[3]
    xres = geo[1]
    yres = geo[5]
    xmax = xmin + xres*nx
    ymin = ymax + yres*ny

    return nx,ny,xmin,ymax,xres,yres,xmax,ymin

def entropiaNumpy(pathInput):
    ds = gdal.Open(pathInput+'B12.tif')
    b12 = ds.ReadAsArray()
    entropia = entropy(b12, disk(5))
    creaTif(ds,entropia,pathInput+'b12_entropia.tif')
    return entropia

def porcNubosidadOceano(df,pathLM):
    '''
    Funcion que obtiene el porcentaje de nubosidad en el mar

    Parametros
    ----------
    df : str
        GeoDataFrame de GeoPandas
    pathLM : str
        Path de las mascaras de tierra
    '''
    # Porcentaje de nubosidad solo en el mar
    print("Porcentaje de nubosidad en el mar")
    # Km2
    areaTile = 12056.04
    df_maskLand = gpd.read_file(pathLM+'land_2_UTM16N_20m_SPlaya_2021.geojson')
    res_differenceNube = gpd.overlay(df, df_maskLand, how='difference')
    nubeOceano = res_differenceNube['geometry'].area.sum()*0.000001
    porcNubeOceano = (nubeOceano*100)/areaTile
    porcNubeOceano = round(porcNubeOceano,4)
    return porcNubeOceano

def nubesMascara(cuadrante,bufferNubes,pathSCL,pathLM,pathTmp):
    cuadrante = str(cuadrante[0])+' '+str(cuadrante[1])+' '+str(cuadrante[2])+' '+str(cuadrante[3])

    os.system('gdal_calc.py -A '+pathSCL+' --outfile='+pathTmp+'cloudMaskShadow_bin_tmp.tif --calc="0*(A!=8)+0*(A!=9)+0*(A!=10)+0*(A!=11)+1*(A==8)+1*(A==9)+1*(A==10)+1*(A==11)"')

    os.system('gdal_polygonize.py '+pathTmp+'cloudMaskShadow_bin_tmp.tif -f "GeoJSON" '+pathTmp+'SCL_tmp.json')
    df = gpd.read_file(pathTmp+'SCL_tmp.json')
    # Verifica la validez de la geometria
    is_valid = df.geometry.is_valid
    invalid_geoms = df[~is_valid].index.tolist()
    # Corrige la geometria
    for idx in invalid_geoms:
        geom_ext = df.geometry[idx].exterior
        new_poly = Polygon(geom_ext.coords)
        df.geometry[idx] = new_poly
    df = df[df['DN'] == 1]
    # Porcentaje nubosidad oceano
    #porcNubeOceano = porcNubosidadOceano(df, pathLM)
    if len(df) == 0:
        print("No buffer de nubes")
        banderaNub = False
        return banderaNub#,porcNubeOceano
    else:
        print("Buffer de nubes")
        banderaNub = True
        df = df.buffer(bufferNubes)
        print("Disolviendo Buffer")
        df_g = df.unary_union
        df = gpd.GeoDataFrame(crs=df.crs, geometry=[df_g])
        # Elimina el buffer cerca de las costas
        df_mask = gpd.read_file(pathLM+'land_2_UTM16N_20m_SPlaya_b100m_2021.geojson')
        res_difference = gpd.overlay(df, df_mask, how='difference')
        res_difference.to_file(pathTmp+"cloudMaskShadow_b250_bin_rec_tmp.json", driver='GeoJSON')


        return banderaNub#,porcNubeOceano
    
def sargazoBinNumpy(pathInput):
    b11 = aperturaDS(pathInput+'B11.tif').ReadAsArray().astype(np.int16)
    b8A = aperturaDS(pathInput+'B8A.tif').ReadAsArray().astype(np.int16)
    b08 = aperturaDS(pathInput+'B08_20.tif').ReadAsArray().astype(np.int16)
    b04 = aperturaDS(pathInput+'B04.tif').ReadAsArray().astype(np.int16)

    b11 = ((b11 - 1000) * 0.0001)
    b8A = ((b8A - 1000) * 0.0001)
    b08 = ((b08 - 1000) * 0.0001)
    b04 = ((b04 - 1000) * 0.0001) 

    ref = aperturaDS(pathInput+'B04.tif')

    # Prueba de tif
    creaTif(ref,b11,pathInput+'B11_mult.tif')
    creaTif(ref,b8A,pathInput+'B8A_mult.tif')
    creaTif(ref,b08,pathInput+'B08_20_mult.tif')
    creaTif(ref,b04,pathInput+'B04_mult.tif')

    sargazoBin = np.where((b8A > 0.07) & (b04 < 0.1) & (b11 < 0.05) & (b04 < b8A) & (b04 < b08), 1, 0)

    creaTif(ref,sargazoBin,pathInput+'alg_tmp_numpy.tif')


def filtroPixel(dsRef,dsSar,nubeBaja,entropia,dsSCL,SNbuffer,pathTmp,pathLM):
    
    # Nube baja con B12
    nuMask = dsRef.ReadAsArray()
    b12 = dsRef.ReadAsArray().astype(np.int16)
    b12 = (b12 - 1000) * 0.0001
    sar = dsSar.ReadAsArray()
    scl = dsSCL.ReadAsArray()
    df_detfoo = gpd.read_file(pathLM+'MSK_DETFOO_B8A_b1500.geojson')
    nx,ny,xmin,ymax,xres,yres,xmax,ymin = obtieneParametrosGeoTrasform(dsRef)

    # Sin buffer de nubes
    if SNbuffer == False:
        nubes = gdal.Open(pathTmp+'cloudMaskShadow_bin_tmp.tif').ReadAsArray()

    print('=============================================')
    print('Detección de sargazo algoritmo: ',len(sar[sar == 1]),' elementos')
    print('=============================================')

    contB12 = 0
    contSN = 0
    contEnt = 0
    contSCL = 0
    # Sin buffer nubes
    contNubes = 0
    listaBanderas = []

    #Sombra de nube
    sombraNube = 0.001
    #Entropia
    entropiaMin = 4.0

    for i in range(nuMask.shape[0]):
        for j in range(nuMask.shape[1]):
            if sar[i,j] == 1:               
                y = (i*yres + ymax) + yres/2
                x = (j*xres + xmin) + xres/2
                sargazoPunto = Point(x,y)
                # ENTROPIA CON DETFOO 
                seriePunto = df_detfoo.geometry.contains(sargazoPunto)
                if len(seriePunto[seriePunto == True]) >= 1 and entropia[i,j] >= entropiaMin:
                    nuMask[i,j] = 0
                    listaBanderas.append('Entropia y Detfoo')
                    contEnt += 1
                # SCL
                elif (scl[i,j] == 3) or (scl[i,j] == 8) or (scl[i,j] == 9) or (scl[i,j] == 10) or (scl[i,j] == 11):
                    nuMask[i,j] = 0
                    listaBanderas.append('SCL')
                    contSCL += 1  

                else:
                    nuMask[i,j] = 1
            else:
                nuMask[i,j] = 0

    # Sin buffer de nubes
    if SNbuffer == False:
        for i in range(nuMask.shape[0]):
            for j in range(nuMask.shape[1]):
                if sar[i,j] == 1: 
                    if nubes[i,j] == 0:
                        nuMask[i,j] = 0
                        listaBanderas.append('Nubes')
                        contNubes += 1
                else:
                    nuMask[i,j] = 0

    print(set(listaBanderas))
    print('Filtrados Nube Baja: ',contB12)
    print('Filtrados Sombra nube: ',contSN)
    print('Filtrados Entropia y Detfoo: ',contEnt)
    print('Filtrados SCL: ',contSCL)
    # Sin buffer de nubes
    print('Filtrados Nubes: ',contNubes)

def poligonizacion(tile,anio,fecha,pathLM,pathInput,pathOutput):
    time = datetime.datetime.strptime(fecha,'%Y%m%dT%H%M%S')
    fechaDia = time.strftime('%Y-%m-%d')
    os.system('gdal_polygonize.py '+pathInput+'nubesBajas_mask.tif -f "GeoJSON" '+pathInput+'alg_mask_filter_tmp.json')
    df = gpd.read_file(pathInput+'alg_mask_filter_tmp.json')
    df = df[df.DN == 1]

    print('=============================================')
    print('Deteccion de sargazo con filtro de pixel: ',len(df),' elementos')
    print('=============================================')

    if len(df)>= 1:
        df['IDpoligono'] = range(1, len(df) + 1)
        df['tile'] = tile
        df['fecha'] = fecha
        df['fechaDia'] = fechaDia
        # CALCULO DE DISTANCIA A LA COSTA
        gdf = gpd.read_file(pathLM+'land_UTM16N_20m_2021.geojson')
        distances = []
        df['distCosta_km'] = None
        for i in range(len(df)):
            distance = round(gdf['geometry'].iloc[0].distance(df['geometry'].iloc[i])*0.001,4)
            distances.append(distance)
        df['distCosta_km'] = distances
        df = df.drop(columns=['DN'])      
        df.to_file(pathInput+'alg_mask_filter_tmp_sar.json', driver="GeoJSON")
        banderaSar = True
        nombre = None
        return nombre, banderaSar
    else:
        print('=========================')
        print('NO DETECCIÓN DE SARGAZO')
        print('=========================')
        nombre = ''
        banderaSar = False
        return nombre, banderaSar
    

def verificaLugar(df_sargazo,pathLM):
    df_playas = gpd.read_file(pathLM+'playas_UTM16N_20m_2021.geojson')
    df_cuerposA = gpd.read_file(pathLM+'cuerpos_agua_UTM16N_20m_2021.geojson')
    df_sargazo['lugar'] = None
    df_sargazo['nom_playa'] = None
    playero = ['oceano' for i in range(len(df_sargazo))]
    nombre_playa = ['null' for i in range(len(df_sargazo))]

    for k in range(len(df_sargazo)):
        for j in range(len(df_playas)):
            if df_sargazo.iloc[k].geometry.intersects(df_playas.iloc[j].geometry) == True:
                playero[k] = 'playa'
                nombre_playa[k] = df_playas.iloc[j]['name']
                continue
        for j in range(len(df_cuerposA)):
            if df_sargazo.iloc[k].geometry.intersects(df_cuerposA.iloc[j].geometry) == True:
                playero[k] = 'c_aguacont'
                continue

    df_sargazo['lugar'] = playero
    df_sargazo['nom_playa'] = nombre_playa

    return df_sargazo
    
def mascarasVectoriales(maskUTM,tile,anio,fecha,fechaProc,SNbuffer,pathLM,pathTmp,pathOutput):

    # SIN DETFOO
    df = gpd.read_file(pathTmp+'alg_mask_filter_tmp_sar.json')
    if maskUTM == 1:
        df_mask = gpd.read_file(pathLM+'land_2_UTM16N_20m_SPlaya_2021.geojson')
    elif maskUTM == 2:
        df_mask = gpd.read_file(pathLM+'land_1_UTM20N_2021.geojson')

    res_difference = gpd.overlay(df, df_mask, how='difference')
    print('=============================================')
    print('Detección de sargazo con mascara de tierra: ',len(res_difference),' elementos')
    print('=============================================')

    # Con buffer de nubes
    if SNbuffer == True:
        # Puede que algunas veces no genere la mascara de nubes
        try:            
            df_maskCloudShadow = gpd.read_file(pathTmp+'cloudMaskShadow_b250_bin_rec_tmp.json')
            res_difference = gpd.overlay(res_difference, df_maskCloudShadow, how='difference')
        except:
            pass
        print('=============================================')
        print('Detección de sargazo con mascara de nubes/sombra: ',len(res_difference),' elementos')
        print('=============================================')

    os.system('mkdir -p '+pathOutput+tile+'/')
    nombre = pathOutput+tile+'/'+'S2_MSI_SAR_'+tile+'_'+fecha+'_'+fechaProc+".json"
    res_difference["geometry"] = [MultiPolygon([feature]) if type(feature) == Polygon \
    else feature for feature in res_difference["geometry"]]
    df_sargazo = res_difference
    if len(res_difference)>= 1:
        banderaSar = True
        # OBTENCION DE AREA Km2
        df_sargazo["area_km2"] = round(df_sargazo['geometry'].area*0.000001,4)
        # VERIFICA SI ES PLAYERO Y OTRA ALGA
        df_sargazo = verificaLugar(df_sargazo, pathLM)
        # SOLO AREA DE SARGAZO
        df_sargazo_s = df_sargazo.loc[(df_sargazo['lugar'] == 'oceano') | (df_sargazo['lugar'] == 'playa')]
        totalSar = str(round(df_sargazo_s['area_km2'].sum(),4))
        # ARCHIVO FINAL
        # MANDA A DATA
        df_sargazo.to_file(nombre, driver="GeoJSON")

    else:
        print('=========================')
        print('NO DETECCIÓN DE SARGAZO')
        print('=========================')
        banderaSar = False
        totalSar = '0'    
    return banderaSar, totalSar, nombre

def obtieneVertices(pathInput,pathOutput):
    polys = gpd.read_file(pathInput)
    points = polys.copy()
    points = points.explode()
    points.geometry = points.geometry.apply(lambda x: MultiPoint(list(x.exterior.coords)))
    nombre = pathOutput+pathInput.split('/')[-1].split('.')[0]+'_vertices.json'
    points.to_file(nombre,driver='GeoJSON')


def obtieneCentroides(pathInput,pathOutput,pathLM):
    df = gpd.read_file(pathInput)
    df_maskLand= gpd.read_file(pathLM+'land_2_UTM16N_20m_SPlaya_b100m_2021.geojson')
    geoSc = df.geometry.centroid
    df['geometry'] = geoSc
    res_difference = gpd.overlay(df, df_maskLand, how='difference')
    nombre = pathOutput+pathInput.split('/')[-1].split('.')[0]+'_centroides.json'
    # Geojson 
    res_difference.to_file(nombre,driver='GeoJSON')


def obtieneSegmentado(pathInput,pathOutput,pathLM):

    df = gpd.read_file(pathInput)
    df_maskLand= gpd.read_file(pathLM+'land_2_UTM16N_20m_SPlaya_b100m_2021.geojson')
    crs = df.crs

    lista_df_puntos = list()
    for poly_index in df.index:
        poly = df.loc[poly_index, 'geometry']
        x0, y0, x1, y1 = poly.bounds
        x = np.arange(x0, x1, 10)
        y = np.arange(y0, y1, 10)
        X,Y = np.meshgrid(x, y)
        idPoligono = df.loc[poly_index, 'IDpoligono']
        tile = df.loc[poly_index, 'tile']
        fecha = df.loc[poly_index, 'fecha']
        fechadia = df.loc[poly_index, 'fechaDia']
        distCosta = df.loc[poly_index, 'distCosta_km']
        areakm2 = df.loc[poly_index, 'area_km2']
        lugar = df.loc[poly_index, 'lugar']
        nomPlaya = df.loc[poly_index, 'nom_playa']
        df_puntos_alc = pd.DataFrame(np.array([X.flatten(), Y.flatten()]).T, columns=['x', 'y'])\
            .assign(clave=poly_index)\
            .pipe(lambda df: gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y'])))\
            .loc[lambda df: df.within(poly)]
        df_puntos_alc['idpoligono'], df_puntos_alc['tile'], df_puntos_alc['fecha'], df_puntos_alc['fechadia'], df_puntos_alc['distcosta_km'],  df_puntos_alc['area_km2'], df_puntos_alc['lugar'], df_puntos_alc['nom_playa'] = [idPoligono, tile, fecha, fechadia, areakm2, distCosta, lugar, nomPlaya]
        lista_df_puntos.append(df_puntos_alc.iloc[::-1])
        
    df_xy = pd.concat(lista_df_puntos, axis=0)
    df_xy.crs = crs

    res_difference = gpd.overlay(df_xy, df_maskLand, how='difference')
    nombre = pathOutput+pathInput.split('/')[-1].split('.')[0]+'_segmentado.json'
    # Geojson 
    res_difference.to_file(nombre,driver='GeoJSON')

def creaCSV(pathInput,pathOutput):
    gdf = gpd.read_file(pathInput)
    gdf.area_km2 = round(gdf.area_km2,4)
    crs = gdf.crs.srs.split(':')[-1]
    archivoCSV = pathOutput+pathInput.split('/')[-1].split('.')[0]+'.csv'
    gdf.to_csv(archivoCSV,index=False)

    return archivoCSV,crs

def RGB(r,g,b,tile,anio,fecha,fechaProc,pathOutputGeoTiff,pathTmp):
    nombre = pathOutputGeoTiff+'sargazo/'+tile+'/'+'S2_MSI_SAR_'+tile+'_'+fecha+'_'+fechaProc+".tif"
    os.system('gdal_merge.py -separate -co PHOTOMETRIC=RGB -o '+nombre+' '+r+' '+g+' '+b)

def RGB_TC(tile,anio,fecha,fechaProc,nivel,resolucion,pathInput,pathOutputGeoTiff,pathTmp):
    dirTC = listaBandas(pathInput,nivel,resolucion,'TCI')
    nombre = pathOutputGeoTiff+'TC/'+tile+'/'+'S2_MSI_TC_'+tile+'_'+fecha+'_'+fechaProc+'.tif'
    os.system('gdal_translate '+dirTC+' '+nombre)

