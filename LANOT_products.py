
# Importacion de librerias
import functions as fn
from glob import glob
import os

def sargazo(pathInput, pathTmp, pathLM ,pathOutput):
    '''
    Funcion de procesamiento de imagenes Sentinel-2 para la deteccion de sargazo
    mediante las bandas 4, 8, 8A y 11. Y el uso de mascaras vectoriales estaticas
    de linea de costa y nmascaras dinamicas de nubes altas y bajas.

    Parametros
    ----------
    pathInput : str
        Path de entrada de imagenes Sentinel-2
    pathTmp : str
        Path de salida de archivos temporales
    pathLM : str
        Path de archivos de de mascaras vectoriales estaticas
    pathOutput : str
        Path de salida de archivos de salida
    '''
    
    # Referencias de bandas
    bandas20m = ('B02','B03','B04','B05','B8A','B11','B12','SCL')
    bandas10m = ['B08']

    # Path de archivos
    print('1. Enlistado de archivos...')
    archivo = fn.listaArchivos(pathInput+'/*')
    print(archivo)
    archivo = archivo[0]

    # Obtencion de datos
    fecha = fn.obtieneFecha(archivo)
    fechaDia = fecha.split('T')[0]
    fechaImaProc = fn.obtieneFechaImaProc(archivo)
    tile = fn.obtieneTile(archivo)
    anio = fn.obtieneAnio(archivo)
    print("Fecha: "+fecha)
    print("Tile: "+tile)
    # Descomprimiendo archivo
    fn.descomprime(archivo,pathTmp)
    dirI = fn.nomDir(archivo,'L2A')

    # Porcentaje de nubes
    print('2. Porcentaje de nubes...')
    porcNube = fn.obtienePorcentajeNube(pathTmp+dirI)
    print('Procentaje de nubes: ',porcNube)

    # Condicion de nubes
    if porcNube >= 80.0 :
        print('=============================================')
        print('Imágen con exceso de nubosidad, no se procesara')
        print('=============================================')
        exit()

    # Valores referidos a porcentaje de nubes
    elif porcNube >= 30.0:
        nubesBajas = 0.02
        bufferNubes = 200
        SNbuffer = True
    else:
        nubesBajas = 0.04
        bufferNubes = 400
        SNbuffer = True

    # Pasando a geotiif y remuestreando a 20m
    print('3. Convirtiendo a GeoTIFF y remuestreando a 20m...')
    for banda20 in bandas20m:
        dirB20 = fn.listaBandas(pathTmp+dirI,'L2A','R20m',banda20)
        dsB20 = fn.aperturaDS(dirB20)
        fn.imgToGeoTIF(dsB20,banda20,pathTmp)
    for banda10 in bandas10m:
        print(banda10)
        dirB10 = fn.listaBandas(pathTmp+dirI,'L2A','R10m',banda10)
        dsB10 = fn.aperturaDS(dirB10)
        fn.imgToGeoTIF(dsB10,banda10,pathTmp)
        fn.remuestrea(pathTmp+banda10+'_20.tif',dsB10,20,20)

    # Parametros de referencia para el procesamiento
    print('4. Parametros de referencia para el procesamiento...')
    ref = fn.aperturaDS(pathTmp+bandas20m[-2]+'.tif')
    scl = fn.aperturaDS(pathTmp+bandas20m[-1]+'.tif')
    cuadrante = fn.obtieneCuadrante(ref)   

    # Mascara de nubes altas
    print('5. Mascara de nubes altas...')
    #banderaNub,porcNubeOceano = fn.nubesMascara(cuadrante,bufferNubes,pathTmp+bandas20m[-1]+'.tif',pathLM,pathTmp)
    banderaNub = fn.nubesMascara(cuadrante,bufferNubes,pathTmp+bandas20m[-1]+'.tif',pathLM,pathTmp)

    # Algortimo de sargazo
    print('6. Algoritmo de sargazo...')
    fn.sargazoBinNumpy(pathTmp)
    dsSar = fn.aperturaDS(pathTmp+'alg_tmp_numpy.tif')

    # Obtencion de entropia
    print('7. Obteniendo entropia...')
    entropia = fn.entropiaNumpy(pathTmp)

    # Filtro de pixeles con nubes bajas y entropia
    print('8. Procesando sargazo con filtro...')
    nuMask = fn.filtroPixel(ref,dsSar,nubesBajas,entropia,scl,SNbuffer,pathTmp,pathLM)
    fn.creaTif(ref,nuMask,pathTmp+'nubesBajas_mask.tif')
    del nuMask

    # Poligonizacion
    print('9. Procesando poligonizacion...')
    archivoProc,banderaSar = fn.poligonizacion(tile,anio,fecha,pathLM,pathTmp,pathOutput)

    # Aplicacion de mascaras vectoriales
    if banderaSar == True:
        print('10. Aplicando mascaras vectoriales...')
        banderaSar, totalSarMask, archivoProc = fn.mascarasVectoriales(1,tile,anio,fecha,fechaImaProc,SNbuffer,pathLM,pathTmp,pathOutput)

        banderaSar_log = 'si'
        totalSar = totalSarMask

        print('11. Creando archivos extra de salida...')
        # Vertices
        os.system('mkdir -p '+pathOutput+tile+'/sagazo_vertices/')
        fn.obtieneVertices(archivoProc,pathOutput+tile+'sargazo_vertices/')
        # Centroides
        os.system('mkdir -p '+pathOutput+tile+'/sargazo_centroides/')
        fn.obtieneCentroides(archivoProc,pathOutput+tile+'sargazo_centroides/',pathLM)
        # Segmentado
        os.system('mkdir -p '+pathOutput+tile+'/sargazo_segmentados/')
        fn.obtieneSegmentado(archivoProc,pathOutput+tile+'sargazo_segmentados/',pathLM)
        # CSV
        archivoCSV, crs = fn.creaCSV(archivoProc,pathTmp)
    
    # Si no hay sargazo
    else:
        banderaSar_log = 'no'
        totalSar = '0'

    # Compuesto RGB
    print('12. Creando compuestos RGB...')
    os.system('mkdir -p '+pathOutput+'rgb/sargazo/'+tile+'/')                
    fn.RGB(pathTmp+bandas20m[4]+'.tif',pathTmp+bandas20m[3]+'.tif',pathTmp+bandas20m[2]+'.tif',tile,anio,fecha,fechaImaProc,pathOutput,pathTmp)
    os.system('mkdir -p '+pathOutput+'rgb/TC/'+tile+'/')
    fn.RGB_TC(tile,anio,fecha,fechaImaProc,'L2A','R10m',pathTmp+dirI,pathOutput,pathTmp)

    # Borrado de archivos temporales
    os.system('rm -r '+pathTmp+'*json')
    os.system('rm -r '+pathTmp+'*.csv')
    os.system('rm -r '+pathTmp+'*.xml')
    os.system('rm -r '+pathTmp+'*.zip')
    os.system('rm -r '+pathTmp+'*.tif')
    os.system('rm -r '+pathTmp+'*.SAFE')