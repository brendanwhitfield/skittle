'''
Created on Nov 29, 2012
@author: Josiah
'''
from SkittleGraphTransforms import chunkUpList, normalizeDictionary, countListToColorSpace, sequenceToColors, countNucleotides
from SkittleStatePackets import StatePacket
import SkittleRequestHandler

SkittleRequestHandler.registerGraph("Nucleotide Display", __name__)
    
def calculateOutputPixels(state):
    assert isinstance(state, StatePacket) 
    seq = state.seq[state.start : state.start + state.length] #substrings the relevant part
    print seq 
    chunks = chunkUpList(seq, state.width )
    print chunks
    if state.scale > 1:
        chunks = chunkUpList(chunks, state.scale)
        print chunks
        counts = countNucleotides(chunks)
        print counts
        counts = normalizeDictionary(counts)
        pixels = countListToColorSpace(counts, state.colorPalette)
    else:
        pixels = sequenceToColors(chunks, state.colorPalette)
    return pixels
    
if __name__ == '__main__':
    print 'Nucleotide Display test case'
    state = StatePacket()
#    state.scale = 1
    print calculateOutputPixels(state)

    
    
    