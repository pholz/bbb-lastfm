import pylast
import cPickle
import sys
import ConfigParser

def getFromUserDOM(dom, tag):
    text = dom.firstChild.getElementsByTagName(tag)[0].firstChild
    if text != None:
        return text.data
    else:
        return 0
        
def getArtistFromName(name):
    a = pylast.Artist(name,network)
    return a

cfg = ConfigParser.ConfigParser()
cfg.read('settings.ini')
API_KEY = cfg.get('API','API_KEY')
API_SECRET = cfg.get('API','API_SECRET')
username = cfg.get('USER','username')
password_hash = pylast.md5(cfg.get('USER','password'))

network = pylast.get_lastfm_network(api_key = API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)

# guess & print guessed age of the user 'preflex'
# formula:
#   guessedAge              = sum_i( playcount_i * weightedAverageAge_i ) / sum_i( playcount_i  )
#   with
#   weightedAverageAge_i    = sum_j( age_i_j     * weight_i_j           ) / sum_j( weight_i_j   )
#   playcount_i ...... playcount for user for artist i
#   age_i_j .......... age of top fan j of artist i
#   weight_i_j ....... last.fm's weight attributed to fan j with regard to artist i

me = network.get_user(username)

### testing
#print getArtistFromName(u'Opeth'.encode('latin-1')).get_name()
#print getArtistFromName(u'Sigur R\xf3s'.encode('latin-1')).get_name()

NUM_ARTISTS = 3

mytopartists = 0
fromLib = False
if len(sys.argv) < 2:
    topartists = me.get_top_artists()[0:NUM_ARTISTS]
    mytopartists = map(lambda dic: (dic['item'], int(dic['weight'])), topartists)
else:
    theFile = open('mycharts','r')
    topartists = cPickle.load(theFile)
  #  print topartists
 #   for x in topartists:
#        print type(x[0])
  #      print x[0].decode('latin-1')
    mytopartists = map(lambda (a, v): (getArtistFromName(a), v), topartists[0:NUM_ARTISTS])
    fromLib = True
    

sum_playcount = 0
sum_playcountavgage = 0
my_inferred_age = 0

countries = {}
countryset = set()

## sum ( pcA * sum (genAF * weightAF) / totalWeightA ) ) / totalPCA

sum_playcountavggender = 0

for artist_weight in mytopartists:

    artist = artist_weight[0]
    weight = int(artist_weight[1])
    print artist.get_name().encode('latin-1')
   # print "%s x %d" %(artist.get_name().encode('latin-1'), weight)
    
    fans = artist.get_top_fans()
    sum_ageweight = 0
    sum_weight = 0
    avg_age_weighted = 0
    
    sum_genweight = 0
    avg_gen_weighted = 0
    sum_weight_gen = 0
    
    countries[artist] = [weight, []] 
    
    for fan_weight in fans:
        fan = fan_weight['item']
        fweight = fan_weight['weight']
        info = fan.get_info()
        # we get 
        
        age = int(getFromUserDOM(info, "age"))
        country = getFromUserDOM(info, "country")
        gender = getFromUserDOM(info, "gender")
        if country != 0:
            countries[artist][1].append( (country, fweight) )
            countryset.add(country)
        
        #print age
        if age != 0:
            sum_ageweight += age * fweight
            sum_weight += fweight
            
        if gender != 0:
            numgen = 0
            if gender == 'f':
                numgen = 1
            sum_genweight += numgen * fweight
            sum_weight_gen += fweight
        
        
    
    if sum_weight == 0:
        sum_weight = 1
        
    if sum_weight_gen == 0:
        sum_weight_gen = 1
    
    
        
    avg_age_weighted = sum_ageweight / sum_weight
    print "weighted avg age: %d" %(avg_age_weighted)
    
    avg_gen_weighted = float(sum_genweight) / float(sum_weight_gen)
    print "weighted avg gender: %f" %(avg_gen_weighted)
    
    sum_playcount += int(weight)
    sum_playcountavgage += int(weight) * avg_age_weighted
    sum_playcountavggender += int(weight) * avg_gen_weighted
    
if sum_playcount == 0:
    sum_playcount = 1
    
my_inferred_age = sum_playcountavgage / sum_playcount
print "i guess you are %d years old" %(my_inferred_age)

my_inferred_gender = float(sum_playcountavggender) / float(sum_playcount)
print "%f%% chance that you are female" %(my_inferred_gender * 100)

## now look at all countries that my fav artists' top fans are from
## for each country, sum the fan weights of top fans of every artist and weight it by the relative importance of that artist among my favourites
## take the sum of those weights and rank the countries by their scores

countryscores = []
    
for country in countryset:
    score = 0
  #  print country
    
    for artist in countries:
        playcount_list = countries[artist]
        playcount = playcount_list[0]
        clist = playcount_list[1]
        pc = int(playcount)
        factor = float(pc)/float(sum_playcount)
        
        sum_country_weights = 0
        for country_weight in clist:
            if country_weight[0] == country:
                sum_country_weights += country_weight[1]
    
        score += factor * sum_country_weights

    countryscores.append( (country, score) )
  

sortedscores = sorted(countryscores, key = lambda c_s : c_s[1], reverse = True)

## calculare the probability that user is from a particular country, for the top five countries
totalscores = sum(map(lambda x : x[1], sortedscores))
for item in sortedscores[0:5]:
    relative = float(item[1]) / float(totalscores)
    print "chance of you being from %s: %f%%" % (item[0].encode('latin-1'), relative * 100)
