import re
import sys
import cPickle

def unescape(s):
    s = s.replace("&#32;", " ")
    s = s.replace("&#33;", "!")
    s = s.replace("&#34;", "\"")
    s = s.replace("&#35;", "#")
    s = s.replace("&#36;", "$")
    s = s.replace("&#37;", "%")
    s = s.replace("&#38;", "&")
    s = s.replace("&#39;", "\'")
    s = s.replace("&#40;", "(")
    s = s.replace("&#41;", ")")
    s = s.replace("&#42;", "*")
    s = s.replace("&#43;", "+")
    s = s.replace("&#44;", ",")
    s = s.replace("&#45;", "-")
    s = s.replace("&#46;", ".")
    s = s.replace("&#47;", "/")
    s = s.replace("&#58;", ":")
    s = s.replace("&#59;", ";")
    s = s.replace("&#60;", "<")
    s = s.replace("&#61;", "=")
    s = s.replace("&#62;", ">")
    s = s.replace("&#63;", "?")
    s = s.replace("&#64;", "@")
    return s

def load(x):
    dom = open(x, 'r')
    input = dom.read()
    lines = input.split("\n")
    dom.close()

    theList = []
    lastLineType = 1

    theDictionary = {}

    alert = 'ARTIST_DNE_ALERT'
    
    for line in lines:
        if re.search('<key>Artist</key>',line):
            if lastLineType != 1:
                theList.append('0')
            artist = line.replace('<key>Artist</key><string>','')
            artist = artist.replace('</string>','')
            artist = artist.strip('\t')
            theList.append(unicode(unescape(artist),'utf-8'))
            lastLineType = 0
        if re.search('<key>Play Count</key>',line):
            if lastLineType != 0:
                theList.append(alert)
            pcount = line.replace('<key>Play Count</key><integer>','')
            pcount = pcount.replace('</integer>','')
            pcount = pcount.strip('\t')
            theList.append(pcount)
            lastLineType = 1

    for i in range(0,len(theList)-1,2):
        if theList[i] in theDictionary:
            theDictionary[theList[i]] += int(theList[i+1])
        else:
            theDictionary[theList[i]] = int(theList[i+1])

    if alert in theDictionary:
        del theDictionary[alert]
        
    theDictionary = sorted(theDictionary.iteritems(),key=lambda (k,v):(v,k), reverse=True)

    for item in theDictionary:
        if item[1] > 0:
            print item[0] + ', ' + str(item[1])
            
    f_dict = open('mycharts','w')
    print 'writing to disk...'
    print theDictionary
    cPickle.dump(theDictionary, f_dict)

if len(sys.argv) < 2:
    print 'pleaese specify the library xml, e.g.: "python itunesLoader.py Library.xml"'
else:
    load(sys.argv[1])

    
        

        
            
