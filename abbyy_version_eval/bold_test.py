import sys
import re
from optparse import OptionParser
from BeautifulSoup import BeautifulStoneSoup

"""
Extracts names from Baker's by picking out bold text from beginnings of paragraphs.
"""

def main(options):

    bakers = BeautifulStoneSoup(open(options.filename), convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    paragraphs = bakers.findAll("p")
    names=[]
    for paragraph in paragraphs:
        temp = paragraph.findAll("span", {"style" : "font-weight:bold;"})
        temp = [item.text for item in temp]
        for item in temp:
            # Count as name only if item fits "Last, First" format
            if re.search("[A-Z].*, ?[A-Z].*", item):
                names.append(item)
    f=open(options.output, "w")
    f.write("\n".join(names).encode("utf-8"))
    f.close()
    print "Names extracted: %s" % len(names)        

if __name__ == "__main__":

    parser=OptionParser()
    parser.add_option("-f", dest="filename", help="name of file to read in")
    parser.add_option("-o", dest="output", help="output file name")
    (options, args)=parser.parse_args()
    main(options)
    
