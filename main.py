from LANOT_products import sargazo

def main():
    # Prueba de la funcion de sargazo

    # Parametros
    pathInput = './input/'
    pathTmp = './tmp/'
    pathLM = './data/masks/'
    pathOutput = './output/'

    # Ejecucion de la funcion
    sargazo(pathInput, pathTmp, pathLM, pathOutput)

if __name__ == '__main__':
    main()
