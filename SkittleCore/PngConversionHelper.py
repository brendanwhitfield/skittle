'''
Functions related to PNG moved from GraphRequestHandler
Created on Jan 17, 2013
@author: Josiah
'''
import png, tempfile
from DNAStorage.StorageRequestHandler import GetPngFilePath, StorePng

def checkForGreyscale(state):
    grayGraph = ['m', 'o']
    return state.requestedGraph in grayGraph

def convertToPng(state, pixels, isRaster = False):
    targetWidth = 1024
    greyscale = checkForGreyscale(state)
    print "GreyScale: ", greyscale
    f = tempfile.mktemp()
    #open up tempFile
    f = open(f, 'wb')
    if greyscale:
        p = multiplyGreyscale(pixels, 255)
        w = png.Writer(len(p[0]), len(p), greyscale=True)
    elif not isRaster:   #Nucleotide Bias
        p = flattenImage(pixels, len(pixels[0]), True, 4)
        w = png.Writer(len(p[0])/4, len(p), greyscale=False, alpha=True)
    else: #raster, color graphs
        p = flattenImage(pixels, targetWidth)
        w = png.Writer(targetWidth, len(p))
    w.write(f, p)
    f.close()
    f = open(f.name, 'rb') #return the binary contents of the file
    data = f.read()
    StorePng(state, f)
    return data

def flattenImage(pixels, targetWidth, isColored = True, nChannels = 3):
    pixels = squishImage(pixels)
    
    p = []
    newline = []
    for color in pixels:
        if color is None:
            newline += (0,) * nChannels
        elif nChannels == 4:
            newline += color 
            newline += (255,) #alpha
        else: 
            newline += color
        if len(newline) >= targetWidth * nChannels: 
            p.append(newline)
            newline = []
    if newline and newline[0] != []: 
        p.append(newline) #append a partial line if there is one
    return p

def multiplyGreyscale(p, greyMax = 255):
    for index, line in enumerate(p):
        p[index] = map(lambda x: int(max(x,0.0) * greyMax), line)
    return p

def squishImage(pixels):
    if isinstance(pixels, list):
        if isinstance(pixels[0], list):
            return reduce(lambda x,y: x + squishImage(y), pixels, [])
        else:
            return pixels
    else:
        return pixels