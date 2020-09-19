from __future__ import print_function
import xml.etree.ElementTree as etree
import re, sys, os, heapq, math
from collections import *
from Stemmer import Stemmer as PyStemmer
import glob

reload(sys)
sys.setdefaultencoding('utf-8')
ps = PyStemmer('porter')

if(len(sys.argv[1:])<2):
	print("needs 3 arguments")
	sys.exit()

pathWikiXML = sys.argv[1].strip()
outputDirPth = sys.argv[2].strip()
if not os.path.exists(outputDirPth):
    os.makedirs(outputDirPth)

absltPthCurrPrgrm = os.path.abspath(os.path.dirname(sys.argv[0]))
# print("existential question ",os.path.exists(outputDirPth))
# print(pathWikiXML)
# file = sys.argv[0]
# pathname = os.path.dirname(file)
##########################################################################

stopwords, allwords = dict(), dict()

prntLst = ['t', 'p', 'c']
dir_names = ["title", "text", "category"]
tags, print_tags = dict(), dict()
for i in range(3):
	tags[dir_names[i]] = i
	print_tags[dir_names[i]] = prntLst[i]

occ, new_adj = [], []
for i in range(3):
	occ.append(defaultdict(int))
	new_adj.append(defaultdict(list))

document_number, total_document_count, valdDoc = 0, 0, 1
file_index, offset_value = [0, 0, 0, 0], [0, 0, 0, 0]

offset_pointer, posting_pointer = list(), list()

document_titles = open(os.path.join(outputDirPth, 'doc_titles.txt'), 'wb')

##########################################################################

def strip_tag_name(t):
	idx = k = t.rfind("}")
	if idx != -1:
		t = t[idx + 1:]
	return t

# update dictionary for category
def update_dict_infobox(text): 
	tmpword = re.findall("{{Infobox(.*?)}}", text)
	if tmpword:
		if valdDoc:
			for t in tmpword :
				t = t.split(' ')
				for temp in t: 
					temp = temp.lower()
					temp = ps.stemWord(temp)
					if (temp) and (temp not in stopwords):
						occ[3][temp] += 1
						allwords[temp] = 1

# update dictionary for text
def update_dict_category(text): 
	tmpword = re.findall("\[\[Category:(.*?)\]\]", text)
	if tmpword :
		if valdDoc:
			for t in tmpword :
				t = t.split(' ')
				for temp in t: 
					temp = temp.lower()
					temp = ps.stemWord(temp)
					if (temp) and (temp not in stopwords):
						occ[2][temp] += 1
						allwords[temp] = 1
				
# update dictionary for title, text
def update_dict(tag_type, text):
	global occ, allwords, tags
	spltLst = re.split('[^A-Za-z0-9]', text)
	spltLst = [ps.stemWord(wrd.lower()) for wrd in spltLst]
	for word in spltLst:
		if (word != '') and (word not in stopwords) :
			occ[tags[tag_type]][word] += 1
			allwords[word] = 1

#write the primary index
def writeIntoFile(tag_index, pathOfFolder, index, countFinalFile):                                        
    global posting_pointer
    data = list()

    for key in sorted(index):
        string = str(key)+' '
        temp = index[key]
        if len(temp) != 0:
            idf = math.log10(total_document_count / float(len(temp)))
        for i in range(len(temp)):
            S1 = temp[i].split('d')
            if len(S1) > 1:
                S2 = S1[1].split('c')
                if len(S2) > 1:
	                DD,CC,GG = S2[0], float(S2[1]), ((1+math.log10(float(S2[1]))) * idf)
	                string = string + 'd' + DD + 'c' + str(("%.2f" % GG)) + ' '

        data.append(string)
    	# fileName = pathOfFolder + 'term_offset.txt'
        offset_pointer[tag_index].write(key + ":" + str(offset_value[tag_index]) + "\n")
        offset_value[tag_index] = offset_value[tag_index] + 1 + len(string)

    if valdDoc:
	    posting_pointer[tag_index].write('\n'.join(data))
	    posting_pointer[tag_index].write('\n')
	    countFinalFile += 1

def mergeFiles(tag_index, pathOfFolder, countFile, f_name):                                                 #merge multiple primary indexes
    listOfWords, indexFile, topOfFile = {}, {}, {}
    flag = [0] * countFile
    data = defaultdict(list)
    heap = []
    countFinalFile = 0
    for i in range(countFile):
        fileName = pathOfFolder + f_name + str(i)
        indexFile[i] = open(fileName, 'rb')
        flag[i] = 1
        topOfFile[i] = indexFile[i].readline().strip()
        listOfWords[i] = topOfFile[i].split(':')
        if listOfWords[i][0] not in heap:
            heapq.heappush(heap, listOfWords[i][0])        
    count = 0        
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count += 1
        for i in xrange(countFile):
            if flag[i]:
                if listOfWords[i][0] == temp:
                    data[temp].extend(listOfWords[i][1:])
                    if count == 1000000:
                        oldCountFile = countFinalFile
                        writeIntoFile(tag_index, pathOfFolder, data, countFinalFile)
                        if oldCountFile != countFinalFile:
                            data = defaultdict(list)
                    topOfFile[i] = indexFile[i].readline().strip()   
                    if topOfFile[i] == '':
                            flag[i] = 0
                            indexFile[i].close()
                            os.remove(pathOfFolder + f_name + str(i))
                    else:
                        listOfWords[i] = topOfFile[i].split(':')
                        if listOfWords[i][0] not in heap:
                            heapq.heappush(heap, listOfWords[i][0])
    writeIntoFile(tag_index, pathOfFolder, data, countFinalFile)

#############################################################################

if os.path.exists(os.path.join(absltPthCurrPrgrm, 'stopwords.txt')):
	with open(os.path.join(absltPthCurrPrgrm, 'stopwords.txt'), 'r') as file :
		words = file.read().split('\n')
		# stem the stop word
		for word in words: 
			word = ps.stemWord(word)
			if word:
				stopwords[word] = 1
else:
	print("stopwords.txt does not exist in the directory")
	sys.exit()

documentcount = 0
###########################################################################
# parse the documents
for event, elem in etree.iterparse(pathWikiXML, events = ('start', 'end')):
	tag_name = strip_tag_name(elem.tag)

	# finished extracting all the text in the page tag.
	if (tag_name == 'page') and (event == 'end'): 
		documentcount += 1
		total_document_count += 1
		for word in allwords:
			for tag in tags: 
				if occ[tags[tag]][word] != 0: 
					node = 'd' + str(document_number) + 'c' + str(occ[tags[tag]][word])
					new_adj[tags[tag]][word].append(node)
		
		occ = []
		for i in range(3):
			occ.append(defaultdict(int))

		allwords = {}
		document_number += 1
		elem.clear()

	elif (tag_name in tags) and (event == 'end'): 
		if tag_name == 'text': 
			update_dict_category(str(elem.text))
			#  update_dict_infobox(str(elem.text))
		update_dict(tag_name, str(elem.text))
		if tag_name == 'title': document_titles.write(str(elem.text) + '\n') 

	if documentcount >= 2000: 
		documentcount = 0
		for i in range(3): 
			directory = dir_names[i]
			if not os.path.exists(os.path.join(outputDirPth, directory)): 
				os.makedirs(os.path.join(outputDirPth, directory))
			owd = os.getcwd()
			os.chdir(os.path.join(outputDirPth, directory))
			s = str(print_tags[dir_names[i]]) + str(file_index[i])
			f = open(s, "w")
			for v in sorted(new_adj[i]): 
				s = v + ":"
				for u in new_adj[i][v]: 
					s += u + ":" 
				print(s, file = f) 
			f.close()
			os.chdir(owd)
			file_index[i] += 1
		new_adj = []
		for i in range(3):
			new_adj.append(defaultdict(list))

# print('mark ', documentcount)

if documentcount > 0: 
	for i in range(3): 
		directory = dir_names[i]
		if not os.path.exists(os.path.join(outputDirPth, directory)):
			os.makedirs(os.path.join(outputDirPth, directory))
		
		owd = os.getcwd()
		os.chdir(os.path.join(outputDirPth, directory))
		s = str(print_tags[dir_names[i]]) + str(file_index[i])
		f = open(s, "w")
		for v in sorted(new_adj[i]): 
			s = v + ":"
			for u in new_adj[i][v]: 
				s += u + ":" 
			print(s, file = f) 
		f.close()
		os.chdir(owd)
		file_index[i] += 1
	# print('done if, exit for loop')

offset_pointer.append(open(os.path.join(outputDirPth, "title/term_offset.txt"), 'wb'))
offset_pointer.append(open(os.path.join(outputDirPth, "text/term_offset.txt"), 'wb'))
offset_pointer.append(open(os.path.join(outputDirPth, "category/term_offset.txt"), 'wb'))

# offset_pointer.append(open("./infobox/term_offset.txt", 'wb'))
posting_pointer.append(open(os.path.join(outputDirPth, "title/final.txt"), 'wb'))
posting_pointer.append(open(os.path.join(outputDirPth, "text/final.txt"), 'wb'))
posting_pointer.append(open(os.path.join(outputDirPth, "category/final.txt"), 'wb'))
# posting_pointer.append(open("./infobox/final.txt", 'wb'))

# print('merge1')
# print(file_index)
mergeFiles(0, os.path.join(outputDirPth, "title/"), file_index[0]-1, 't')
# print('merge2')
mergeFiles(1, os.path.join(outputDirPth, "text/"), file_index[1]-1, 'p')
# print('merge3')
mergeFiles(2, os.path.join(outputDirPth, "category/"), file_index[2]-1, 'c')
# mergeFiles(3, "./infobox/", file_index[3], 'i')
# code for query
# print('merge done')
for i in range(3): 
	offset_pointer[i].close()
	posting_pointer[i].close()
