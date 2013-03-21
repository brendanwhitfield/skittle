'''
Created on Nov 29, 2012
@author: Josiah Seaman
'''
from SkittleGraphTransforms import average
from PixelLogic import drawBar
from SkittleCore.GraphRequestHandler import registerGraph
from SkittleCore.models import RequestPacket
from SkittleGraphTransforms import sensitiveTestForSpecificFrequency, normalize
from models import ThreeMerDetectorState
from MathLogic import lowPassFilter

registerGraph('t', "Threemer Detector", __name__, False)



def countMatches(sequence, beginA, beginB, lineSize):
    matches = 0
    for index in range(lineSize):
        if sequence[beginA + index] == sequence[beginB + index]:
            matches += 1
    return float(matches) / lineSize

def oldRepeatMap(state, threeMerState):
    freq = []
    lineSize = state.nucleotidesPerLine()
    for h in range(threeMerState.height(state, state.seq)):
        freq.append([0.0]*(threeMerState.samples*3+1))
        offset = h * lineSize
        for w in range(1, len(freq[h])):
            freq[h][w] = countMatches(state.seq, offset, offset + w , lineSize)
    return freq

def calculateOutputPixels(state, threeMerState = ThreeMerDetectorState()):
    assert isinstance(state, RequestPacket)
    state.scale = 1 #these calculations are only meaningful at scale 1
    
    state.readFastaChunks()#read in next chunk
    scores = oldRepeatMap(state, threeMerState)
    
    threemer_scores = sensitiveTestForSpecificFrequency(scores, 3, threeMerState.samples)
    threemer_scores = lowPassFilter(threemer_scores)
#    avg = average(threemer_scores)
#    threemer_scores.sort()
#    median = threemer_scores[len(threemer_scores)/2]
#    percentile95 = threemer_scores[len(threemer_scores)*95/100]
#    max_ = threemer_scores[-1]
#    return state.width, avg, median, percentile95, max_

    
    '''This trend was found experimentally based on maximums over 69 chunks at width 10-490  #max(threemer_scores)'''
    maximum =  6.1156908088 * (state.nucleotidesPerLine() *70 / 20.0)** (-0.4632922551)
    minimum = 0.2  #min(threemer_scores)

    outputPixels = []
    for size in threemer_scores:
        normalized = normalize(size, minimum, maximum)
        barSize = min(max(0, int(normalized * threeMerState.barWidth)), threeMerState.barWidth)
        barColor = (44, 85, 185)
        if normalized > 0.75:
            barColor = (93,4,157)
        bar = drawBar(barSize, int(threeMerState.barWidth- barSize), barColor, False)
        assert len(bar) == threeMerState.barWidth
        outputPixels.append( bar )
    return outputPixels
        
    