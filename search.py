from __future__ import print_function
import xml.etree.ElementTree as etree
import re, os, heapq, math, operator, string, time, sys
from collections import *
from Stemmer import Stemmer as PyStemmer
import glob

reload(sys)
sys.setdefaultencoding('utf-8')
ps = PyStemmer('porter')

if(len(sys.argv[1:])<1):
	print("Needs 1 argument, the index directory")
	sys.exit()

indexDirPth = sys.argv[1]
# qryTxtFlPth = sys.argv[2]
# outTxtFlPth = sys.argv[3]

# if not os.path.exists(outTxtFlPth):
#     with open(outTxtFlPth, 'w+'): pass
# else:
# 	open(outTxtFlPth, 'w').close()

absltPthCurrPrgrm = os.path.abspath(os.path.dirname(sys.argv[0]))
###########################################################################

stopwords = dict()
inverted_index_file, mapping, doc_offset = list(), list(), list()
inverted_index_file.append(open(os.path.join(indexDirPth, 'title/final.txt'), 'r'))
inverted_index_file.append(open(os.path.join(indexDirPth, 'text/final.txt'), 'r'))
inverted_index_file.append(open(os.path.join(indexDirPth, 'category/final.txt'), 'r'))
dir_names = ["title", "text", "category"]
docs = defaultdict(float)

for i in range(3):
	mapping.append(defaultdict(int))

document_titles = open(os.path.join(indexDirPth, 'doc_titles.txt'), 'r')

def create_offset():
	lines = document_titles.readlines()
	cumulative = 0
	for line in lines: 
		doc_offset.append(cumulative)
		cumulative += len(line)

def index_term_mapping(i):
	mapping = defaultdict(int)
	owd = os.getcwd()
	os.chdir(indexDirPth + dir_names[i])
	with open("term_offset.txt") as file:
		lines = file.readlines()
		for line in lines:
			line = line.split(':')
			mapping[line[0]] = int(line[1].strip())
	file.close() 
	os.chdir(owd)
	return mapping

def single_field_query_tag(q, i): 
	global inverted_index_file, docs, mapping
	if q in mapping[i]: 
		off = mapping[i][q]
		inverted_index_file[i].seek(off)
		line = inverted_index_file[i].readline()
		line = line.split(' ')
		l = len(line)
		for word in line : 
			if word == q: continue
			word = word.split('d')
			if len(word) > 1:
				word = word[1].split('c')
				if len(word) > 1: 
					# if l <= 1:
					docs[word[0]] += float(word[1])
					# else :
					# 	docs[word[0]] += float(word[1]) / float(l-1.0)

def single_field_query(q):
	for i in range(3): 
		single_field_query_tag(q, i)
	
def relevance_ranking():
	global docs
	Docs = sorted(docs.items(), key = operator.itemgetter(1), reverse = True)
	Docs = Docs[:min(10, len(docs))]
	output = ""
	for doc in Docs:
		t = int(doc_offset[int(doc[0])])
		document_titles.seek(t)	
		new_string = document_titles.readline().strip()
		output += new_string + "\n"
	print(output)
	# with open(outTxtFlPth, 'a+') as f:
	# 	print(output, file=f)

###########################################################################

# make a list of all the stopwords.
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

for i in range(3):
	mapping[i] = index_term_mapping(i)

create_offset()

##########################################################################

# get queries into a list
# with open(qryTxtFlPth) as f:
#     qrs = f.read().splitlines()

# print(qrs)

while True:
	query = raw_input("Enter query-> ").strip('\n').lower().strip()
	if(query == 'exit'):
		print('Exiting the query loop')
		break
	start = time.time()
	flag = 0
	docs = defaultdict(float)
	if ("title:" in query) or ("body:" in query) or ("category:" in query) or ("infobox:" in query) or ("e:" in query):
		flag = 1
	query = query.split(' ')
	if flag: 
		for q in query:
			q = q.split(':')
			q[1] = ps.stemWord(q[1])
			if q[0] == "title":
				single_field_query_tag(q[1], 0)
			elif q[0] == "body":
				single_field_query_tag(q[1], 1)
			elif q[0] == "category":
				single_field_query_tag(q[1], 2)
			elif q[0] == "infobox":
				pass
			else:
				pass
	else :
		for q in query: 
			q = ps.stemWord(q)
			single_field_query(q)

	relevance_ranking()
	print ("Query time:", time.time() - start, "seconds.")	

for i in range(3): 
	inverted_index_file[i].close()