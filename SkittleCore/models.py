'''
Created on Nov 30, 2012

@author: Josiah
'''
from django.db import models
import Graphs.models   #import ParentState
from FastaFiles import readFile
import DNAStorage.StorageRequestHandler as StorageRequestHandler
from django.conf import settings

chunkSize = settings.CHUNK_SIZE
'''
This is the single global state packet that defines a view state in Skittle.  
This state packet is equivalent to an URL or a request from the Skittle website.
'''
class RequestPacket(models.Model):
    #TODO: user = models.ForeignKey(User)
    #TODO: session
    specimen = models.CharField(max_length=200, default='hg18')
    chromosome = models.CharField(max_length=200, default='chrY-sample')
    '''It is debatable whether or not the sequence should be stored in the state
    variable since it is only referenced at the first level operation.  Past the first
    step, the input sequence is more likely to be a floatList produced by the previous
    operation.'''
    seq = models.TextField(default=None, null=True)
    colorPalette = models.CharField(max_length=50, 
                                    choices=[("Spring", "Spring"),
                                    ("Summer", "Summer"),
                                    ("Dark", "Dark"),
                                    ("DRUMS", "DRUMS"),
                                    ("Blues", "Blues"),
                                    ("Reds", "Reds"),
                                    ('Classic','Classic')],
                                    default='Classic')
    width = models.IntegerField(default=None, null=True)
    scale = models.IntegerField(default=None, null=True)
    '''Internally, start begins at 0.  Biologists count indices starting at 1, so this number 
    is 1 less than the number displayed on the website.  This also means that you should print
    index+1 whenever you are writing user readable output.'''
    start = models.IntegerField(default=None, null=True)
    length = models.IntegerField(default=0)
    requestedGraph = models.CharField(max_length=1, default=None, null=True)
    
    searchStart = models.IntegerField(default=10)
    searchStop  = models.IntegerField(default=20)
    
    def getFastaFilePath(self):
        return StorageRequestHandler.GetFastaFilePath(self.specimen, self.chromosome, self.start)

    def getActiveGraphSettings(self):
        return Graphs.models.ParentState.objects.filter(session = self, visible = True)
    
    '''Derived value height may need to be further reduced for functions that must scan ahead.'''
    def height(self):
        return self.length / self.nucleotidesPerLine()
    
    def nucleotidesPerLine(self):
        return self.width * self.scale
    
    '''This is a multifunctional 'make the file bigger' read logic for sequential chunks'''
    def readAndAppendNextChunk(self, addPadding = False):
        assert StorageRequestHandler.GetFastaFilePath(self.specimen, self.chromosome, 1) is not None, "Specimen and Chromosome is not in the database"
        startBackup = self.start
        if not self.seq: 
            self.seq = '' #ensure that seq is at least a string object
        self.start = self.start + self.length # jump to the end of the current sequence  (+ chunkSize)
        
        print "Requesting",self.specimen, self.chromosome, self.start 
        sequence = readFile(self)# see if there's a file that begins where you end, this will stop on a partial file
        if sequence is not None:
            self.seq = self.seq + sequence #append two sequences together
        elif addPadding:
            self.seq = self.seq + ('N' * chunkSize)
        self.start = startBackup
        self.length = len(self.seq)
        return self
   
    def readFastaChunks(self):
        numChunks = self.scale or 1 
        if self.seq is not None and len(self.seq) >= numChunks * chunkSize:
            return
        self.seq = ''
        self.length = len(self.seq)
        for chunk in range(numChunks):
            self.readAndAppendNextChunk()
        
class StatePacket(RequestPacket): 
    specimen = 'hg18'
    chromosome = 'chrY-sample'
    width =  200
    scale = 1
    start = 1
#    length = 65536
    requestedGraph = 'n'
    
class ProcessQueue(models.model):
    Specimen = models.CharField(max_length=200)
    Chromosome = models.CharField(max_length=200)
    Graph = models.CharField(max_length=1)
    Start = models.IntegerField()
    Scale = models.IntegerField(default=None, null=True)
    CharsPerLine = models.IntegerField(default=None, null=True)
    
    def IsBeingProcessed(request):
        assert isinstance(request, RequestPacket)
        specimen, chromosome, graph, start, scale, charsPerLine = request.specimen, request.chromosome, request.requestedGraph, request.start, request.scale, request.width
        
        process = ProcessQueue.objects.filter(Specimen = specimen, Chromosome = chromosome, Graph = graph, Start = start, Scale = scale, CharsPerLine = charsPerLine)[:1]
        
        if process:
            return True
        else:
            return False
            
    def BeginProcess(request):
        if not IsBeingProcessed(request):
            process = ProcessQueue(Specimen = request.specimen, Chromosome = request.chromosome, Graph = request.requestedGraph, Start = request.start, Scale = request.scale, CharsPerLine = request.width)
            process.save()
            return True
        else:
            return False
        
    def FinishProcess(request):
        if IsBeingProcessed(request):
            process = ProcessQueue.objects.filter(Specimen = specimen, Chromosome = chromosome, Graph = graph, Start = start, Scale = scale, CharsPerLine = charsPerLine).delete()
            return True
        else:
            return False
    