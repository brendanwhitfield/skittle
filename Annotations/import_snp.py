'''
Created on Mar 7, 2013

@author: Josiah
'''
from models import SnpIndexInfo, Annotation
import SkittleCore.Graphs.SNPdata

def createSnpIndex():
    indexFile = open('snps.index.sorted.txt', 'r')
    for line in indexFile:
        tokens = line.split()
        entry, created = SnpIndexInfo.objects.get_or_create(Start=tokens[0], SnpName=tokens[1], Chromosome=tokens[2], CompactIndex=tokens[3])
        print entry
        
def createAnnotationsFromCompact(clientGenotypeFilepath, chromosome):
    annotations = {}
#    f = open(clientGenotypeFilepath, 'r')
#    compactString = f.read()
#    f.close()
    compactString =SkittleCore.Graphs.SNPdata.packedSNPs 
    
    #array with 8 values, coming from the GFF file.  Reorder slightly
    
    for snp in SnpIndexInfo.objects.filter(Chromosome=chromosome):
        annotations[snp.SnpName] = [compactString[snp.CompactIndex*2], compactString[snp.CompactIndex*2+1], snp.Start]
    assert len(snp) != 0, "SNP index not loaded"
    
    return annotations