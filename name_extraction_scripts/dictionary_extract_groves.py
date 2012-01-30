import re
from string import replace
from optparse import OptionParser

from BeautifulSoup import BeautifulSoup as soup

"""
Extracts names and dates from a dictionary of musicians. Adapted from dictionary_extract.py to process Groves.
"""

parser=OptionParser()
parser.add_option("-f", "--file", dest="filepath", help="file path of dictionary")
parser.add_option("-p", "--html", action="store_true", dest="html", default=False, help="use this option if the dictionary is marked-up")
(options, args)=parser.parse_args()

class Person:
	def __init__(self):
		self.first="?"
		self.last="?"
		self.birth="?"
		self.death="?"
		self.text=""
		self.mentions=0
		self.data={}
	def to_string(self):
		# return "%s,%s,%s,%s" % (self.last, self.first, self.birth, self.death) # uncomment to print dates
		return "%s,%s,%s,%s" % (self.last, self.first, self.birth, self.death)
class People:
	def __init__(self):
		self.list=[]
	def get_person(self, last, first):
		for person in self.list:
			if person.first==first and person.last==last:
				return person
		p=Person()
		p.first=first
		p.last=last
		self.list.append(p)
		return p
	def to_string(self):
		names=[]
		for person in self.list:
			names.append(person.to_string())
		return "\n".join(names)
	
def clean_name(name):
	"""
	fixes common OCR errors and gets rid of html markup
	"""
	name=replace(name, "'", "")
	name=replace(name, "&nbsp;", " ")
	name=replace(name, "&amp;", "&")
	name=replace(name, "&quot;", "\"")
	name=replace(name, "ii", "u")
	return name if name and not any(char.isdigit() for char in name) and name[0].isupper() else "?"
	
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
	return date
	
def get_name(text):
	maxlast="20" # max length of last name
	maxfirst="40" # max length of first name
	x=re.search("^(?P<last>.{,%s}?), ?(?P<first>.{,%s}?)," % (maxlast, maxfirst), text)
	(last, first)=(x.group("last"), x.group("first")) if x else ("?", "?")
	return (clean_name(last), clean_name(first))
	
def get_dates(text):
	maxchar="50" # number of allowed characters between b./d. and date
	x=re.search("born .{,%s}?(?P<birth>[1lIi][0-9lJIgiSo]{3})" %(maxchar,), text)
	birth=x.group("birth") if x else "?"
	y=re.search("died .{,%s}?(?P<death>[1lIi][0-9lJIgiSo]{3})" %(maxchar,), text)
	death=y.group("death") if y else "?"
	if birth==death:
		birth="?"
	return (clean_date(birth), clean_date(death))
	
def get_renaissance(people):
	renaissance=People()
	for person in people.list:
		if person.birth!="?" and int(person.birth) in range(1400, 1600) or person.death!="?" and int(person.death) in range(1400, 1600):
			renaissance.list.append(person)
	return renaissance

# read in dictionary file as a list of paragraphs
f=open(options.filepath)
if options.html:
	dictionary=soup(f.read())
	paragraphs=dictionary.findAll("p")
	paragraphs=[x.text for x in paragraphs]
else:
	dictionary=f.read()
	paragraphs=dictionary.split("\n\n")
	for paragraph in paragraphs:
		paragraph.replace("\n", "")
	
f.close()
people=People()
for paragraph in paragraphs:
	(last, first)=get_name(paragraph)
	if last!="?" and first!="?":
		(birth, death)=get_dates(paragraph)
		person=people.get_person(last, first)
		if person.text=="":
			person.text=paragraph
		if person.birth=="?":
			person.birth=birth
		if person.death=="?":
			person.death=death
# get filename from filepath
filename=options.filepath.split("/")[-1]
filename=filename.split(".")[0]
f=open("%s_names.txt" % filename, "w")
# this is specific to Groves - last names are in caps
groves=People()
for person in people.list:
	if all(x.isalpha() and x.isupper() for x in person.last):
		groves.list.append(person)
f.write(groves.to_string())
f.close()


###########################
#GET RENAISSANCE MUSICIANS#
###########################
renaissance=get_renaissance(people)
f=open("%s_renaissance.txt" % filename, "w")
f.write(renaissance.to_string())
f.close()

#######
#TESTS#
#######
"""
test_list=[]
count=0
for person in people.list:
	if person.birth!="?":
		count+=1
	if person.death!="?":
		count +=1
	if person.birth!="?" and person.death!="?" and int(person.birth) > int(person.death):
		test_list.append(person)
		print "last: %s, first: %s, birth: %s, death: %s \n %s" % (person.last, person.first, person.birth, person.death, person.text)
print "death<birth: %s, count: %d" % (len(test_list), count)


for person in people.list:
	for ref in people.list:
		if person.last in ref.text:
			person.mentions+=1
			person.data["%s,%s" % (ref.last, ref.first)]=ref.text

test_list=[]
for person in people.list:
	if person.mentions>10:
		data=' '.join(person.data)
		test_list.append("%s, %s, %d\n%s\n%s" % (person.last, person.first, person.mentions, person.text, data))
f=open("test.txt", "w")
f.write("\n".join(test_list).encode("utf-8"))
f.close()
"""
