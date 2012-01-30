# -*- coding: utf-8 -*-

import re
from string import replace
from optparse import OptionParser


"""
This script is only useful for scraping data from a copy of Cumming's Biographical Dictionary of Musicians that's been fed through ABBYY and edited so that it's OCR'd without column recognition.
"""

# Get file path from args or use default
parser=OptionParser()
parser.add_option("-f", "--file", dest="filepath", help="file path of cummings", default="cummings.txt")
(options, args)=parser.parse_args()

def clean_date(date):
	"""
	fixes common OCR errors
	"""
	date=replace(date, "g", "9")
	date=replace(date, "i", "1")
	date=replace(date, "o", "0")
	date=replace(date, "l", "1")
	date=replace(date, "I", "1")
	date=replace(date, "S", "8")
	date=replace(date, "J", "1")
	date=replace(date, "-", "?")
	return date
	
def get_name(line):
	maxlast="20" # max length of last name
	maxfirst="80" # max length of first name
	x=re.search("^(?P<last>[A-Z].{,%s}?), ?(?P<first>[A-Z].{,%s}?)\." % (maxlast, maxfirst), line)
	(last, first) = (x.group("last"), x.group("first")) if x else ("","")
	return "%s,%s" % (last, first) if last and first else ""
	
def get_dates(line):
	x=re.search("(?P<birth>([1lIi][0-9lJIgiSo]{3}\??|[_\-?])) ?\??(?P<death>([1lIi][0-9lJIgiSo]{3}\??|[_\-?])) ?\??$", line)
	(birth, death)=(x.group("birth"), x.group("death")) if x else ("","")
	return "%s,%s" % (clean_date(birth), clean_date(death)) if birth and death else ""
	
def restructure(cummings):
	"""
	Takes two lines that are supposed to be one line and joins them into the line it was meant to be.
	"""
	for (i, x) in enumerate(cummings):
		if i<(len(cummings)-1) and get_name(x) and not get_dates(x) and not get_name(cummings[i+1]) and get_dates(cummings[i+1]):
			cummings.insert(i, ' '.join([cummings.pop(i), cummings.pop(i)]))

# Read in file and put text into a list
cummings=open(options.filepath).readlines()
cummings=[line for line in cummings if line!='\n']
cummings=[line.replace("\n", "") for line in cummings]

# Replace instances of ,, with the last name in the previous item in the list
for (i, line) in enumerate(cummings):
	if line[0]==",":
		if get_name(cummings[i-1]):
			cummings[i]="%s,%s" % (get_name(cummings[i-1]).split(",")[0], line[2:])
		else:
			cummings[i]="%s,%s" % (get_name(cummings[i-2]).split(",")[0], line[2:])
			
# Restructure
restructure(cummings)

# Get names and dates and write into file
l=["%s,%s" % (get_name(line), get_dates(line),) for line in cummings]
l=[line for line in l if line[0].isalpha()]

f=open("cummings_names.txt", "w")
f.write("\n".join(l))
f.close()

# Get Renaissance musicians and write to file
renaissance=[]
for line in l:
	info=line.split(",")
	if len(info)==4:
		birth=int(info[2]) if info[2].isdigit() else -1
		death=int(info[3]) if info[3].isdigit() else -1
		if birth in xrange(1400, 1600) or death in xrange(1400, 1600):
			renaissance.append(line)
			
f=open("cummings_renaissance.txt", "w")
f.write("\n".join(renaissance))
f.close()

# Calculate percentage error
theoretical=open(options.filepath).readlines()
theoretical=[line for line in theoretical if (line[0].isalpha() and line[0].isupper()) or line[0]==","]
percentage=float(len(cummings))/len(theoretical)*100
print str(percentage)+"%"
