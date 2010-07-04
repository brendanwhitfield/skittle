#include "HighlightDisplay.h"
#include "glwidget.h"
#include "SequenceEntry.h"
#include <sstream>
#include <algorithm>
#include <QtGui/QScrollArea>
#include <QtGui/QSpinBox>
#include <QtGui/QGridLayout>

HighlightDisplay::HighlightDisplay(UiVariables* gui, GLWidget* gl)
:NucleotideDisplay(gui, gl)
{	
	hidden = true;
	actionLabel = string("Sequence Highlighter");
	actionTooltip = string("Highlights user specified sequences");
	actionData = actionLabel; 
	activeSeqEdit = NULL;
	reverseCheck = NULL;
	formLayout = NULL;
	settingsBox = NULL;
	addButton = NULL;
	
	percentage_match = 0.8;
	frameCount = 0;
	rowCount = 0;
}

HighlightDisplay::~HighlightDisplay(){
    glDeleteLists(display_object, 1);
}

QScrollArea* HighlightDisplay::settingsUi()
{	
    settingsTab = new QScrollArea();    
    settingsTab->setWindowTitle(QString("Sequence Highlighter Settings"));
    settingsTab->setMinimumHeight(120);
    settingsBox = new QFrame(settingsTab);
    settingsTab->setWidget(settingsBox);
	settingsTab->setWidgetResizable(true);
    
	formLayout = new QGridLayout(settingsBox);
	settingsBox->setLayout(formLayout);
	
    QSpinBox* similarityDial = new QSpinBox(settingsBox);
    similarityDial->setValue(80);
    similarityDial->setSuffix("%");
    similarityDial->setMinimum(20);
    similarityDial->setMaximum(100);
    reverseCheck = new QCheckBox("Search Reverse Complement", settingsBox);
    reverseCheck->setChecked(true);
    addButton = new QPushButton("Add a New Sequence", settingsBox);
    
    formLayout->addWidget(reverseCheck, 0,0);
    formLayout->addWidget(new QLabel("Minimum Similarity:"), 1,0);
	formLayout->addWidget(similarityDial, 1,1);
    formLayout->addWidget(addButton, 2,0);
	addNewSequence();
	
	connect( addButton, SIGNAL(clicked()), this, SLOT(addNewSequence()));
		
    connect( similarityDial, SIGNAL(valueChanged(int)), this, SLOT(setPercentSimilarity(int)));     	
	connect( reverseCheck, SIGNAL(released()), this, SLOT(invalidate()));
	return settingsTab;
}

void HighlightDisplay::display()
{		
	checkVariables();
	glPushMatrix();
	glScaled(1,-1,1);
		if(!upToDate)
		{
			vector<vector<int> > results;
			for(int i = 0; i < (int)seqLines.size(); i++)
			{
				results.push_back( identifyMatches( seqLines[i]->seq ) );
				if(reverseCheck->isChecked())
					results.push_back( identifyMatches( reverseComplement(seqLines[i]->seq) ) );
			}
			combine( results );
			loadTextureCanvas();
			upToDate = true;
		}
		if( !nucleotide_colors.empty())
			textureBuffer->display();
	glPopMatrix();
}

GLuint HighlightDisplay::render()//deprecated
{
	GLuint list = glGenLists(1);
    return list;
}

vector<int> HighlightDisplay::identifyMatches(string find)
{
	vector<unsigned short int> scores = calculate(find);

	vector<int> pixels;
	int findSize = find.size();
	int remainingLength = 0;
	int match_minimum = (int)(255 * percentage_match);
	const char* seq = (sequence->c_str()+nucleotide_start);
	int offset = 0;
	for(int i = 0; i < (int)scores.size(); i+=scale)
	{
		vector<unsigned short int>::iterator bestMatch = max_element(scores.begin()+i, scores.begin()+i+scale);
		short int bestScore = *bestMatch;
		int grey = static_cast<int>(  float(bestScore)/findSize * 255 );//Grey scale based on similarity
		int pixelColor = grey;//white to grey
		
		//highlight matches with color
		if(grey >= match_minimum)//count this as a starting position
		{
			offset = distance(scores.begin()+i, bestMatch);
			remainingLength = findSize;// - scale;
		}
		if(remainingLength >= 1)//trail after a match
		{//green if it matches, blue if it doesn't
			if(seq[i+offset] == find[findSize - remainingLength])
				pixelColor = 260;//green
			else
				pixelColor = 258;//blue
				
			remainingLength = max(0, remainingLength - scale);
		}
		pixels.push_back( pixelColor );
	}
	return pixels;
}

//This calculates how well a region of the genome matches a query sequence 'find' at every nucleotide.  
vector<unsigned short int> HighlightDisplay::calculate(string find)
{
	vector<unsigned short int> scores;
	int findSize = find.size();
	int start = nucleotide_start;
	unsigned short int maxMismatches = findSize - static_cast<unsigned short int>((float)findSize * percentage_match + .999);
		//at 50%   1 = 0,  2 = 1, 3 = 1
	const string& seq = *sequence;
	for( int h = 0; h < display_size && h  < (int)seq.size() - start - (findSize-1); h++)
	{
			unsigned short int mismatches = 0;
			int start_h = start + h;
			unsigned short int l = 0;
			while(mismatches <= maxMismatches && l < findSize)
			{
				if(seq[start_h + l] != find[l])//this is the innermost loop.  This line takes the most time
					++mismatches;
				++l;
			}
			scores.push_back(l - mismatches);
			/*unsigned short int score = 0;
			int start_h = start + h;
			for(int l = 0; l < findSize; ++l)
			{
				if(seq[start_h + l] == find[l])//this is the innermost loop.  This line takes the most time
					++score;
			}
			scores.push_back(score);*/
	}	
	return scores;
}

void HighlightDisplay::combine(vector< vector<int> >& results)
{	
	nucleotide_colors.clear();
	
	//ensure they're all the same length
	int nSequences = results.size();
	int length = display_size;
	if(!results.empty())
		length = results[0].size();
	vector< vector<int>::iterator > iterators;
	for(unsigned int i = 0; i < results.size(); ++i)
	{
		if( length != (int)results[i].size() )
		{
			results[i].resize(length, 0 );
		}
		iterators.push_back( results[i].begin() );
	}
	
	color c = color(0,0,0);
	int matchSeq = 0;
	for(int i = 0; i < length; i++)
	{
		int score = 0;
		for(int k = 0; k < nSequences; ++k)
		{
			score = max(score, results[k][i]);//*(iterators[k]));
			//score = *(iterators[k]);
			//++iterators[k];
			if(score > 256)
			{
				matchSeq = k;
				if(reverseCheck->isChecked())
					matchSeq /= 2;
				break;
			}/**/
		}
			
		if(score < 257)
		{
			 c = color(score, score, score);
		}
		else{
			if( score == 258) c = seqLines[matchSeq]->mismatchColor;		
			if( score == 260) c = seqLines[matchSeq]->matchColor;
		}
		nucleotide_colors.push_back( c );
	}
}

inline char complement(char a)
{
	if(a == 'A') return 'T';
	if(a == 'C') return 'G';
	if(a == 'G') return 'C';
	if(a == 'T') return 'A';
	return 'N';
}

string HighlightDisplay::reverseComplement(string original)
{
	string rc;
	int size = original.size();
	rc.resize(size, 'N');
	for(int x = 0; x < size; ++x)
	{					
		rc[x] = complement(original[size-x-1]);
	}
	return rc;
}

void HighlightDisplay::setHighlightSequence(const QString& high_C)
{
	if(seqLines.empty())
		addNewSequence();
	int index = seqLines.size()-1;
	seqLines[index]->setHighlightSequence(high_C);
	
	invalidate();
}

void HighlightDisplay::addNewSequence()
{	
	activeSeqEdit = new QLineEdit(settingsBox);
	if(seqLines.empty())  
		activeSeqEdit->setText("AAAAAAAAAAAA");	
	std::stringstream ss1;
	ss1 << "Sequence " << ++rowCount;//Sequence number
	QLabel* label = new QLabel(ss1.str().c_str());
	SequenceEntry* entry = new SequenceEntry(label, activeSeqEdit );
	
	int row = formLayout->rowCount();
	formLayout->removeWidget(addButton);
    formLayout->addWidget(label, row, 0, Qt::AlignRight);
	formLayout->addWidget(activeSeqEdit, row, 1);
	formLayout->addWidget(entry->colorBox, row, 2);
	formLayout->addWidget(entry->removeButton, row, 3);
	formLayout->addWidget(addButton, row+1, 0);
	
    settingsBox->setMinimumHeight(settingsBox->minimumHeight() + activeSeqEdit->minimumHeight());
	seqLines.push_back( entry );
	
	connect(seqLines[seqLines.size()-1], SIGNAL( removeEntry(SequenceEntry*)), this, SLOT(removeEntry(SequenceEntry*)));
	connect( activeSeqEdit, SIGNAL(textChanged(const QString&)), this, SLOT(invalidate()));
	connect( entry, SIGNAL(colorChanged()), this, SLOT(invalidate()));
	//connect(this, SIGNAL(highlightChanged(const QString&)), activeSeqEdit, SLOT(setText(const QString&)) );
	invalidate();
}

void HighlightDisplay::removeEntry(SequenceEntry* entry)
{
	entry->label->hide();
	formLayout->removeWidget(entry->label);
	entry->lineEdit->hide();
	formLayout->removeWidget(entry->lineEdit);
	entry->colorBox->hide();
	formLayout->removeWidget(entry->colorBox);
	entry->removeButton->hide();
	formLayout->removeWidget(entry->removeButton);
	
	seqLines.erase( std::find(seqLines.begin(), seqLines.end(), entry) );

	invalidate();	
}

void HighlightDisplay::setPercentSimilarity(int percentile)
{
	double newVal = (float)percentile / 100.0;
	if( percentage_match != newVal )
	{
		percentage_match = newVal;
		invalidate();
	}
}
