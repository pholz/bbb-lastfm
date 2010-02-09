import pylast
import lastfmapi

def getFromUserDOM(dom, tag):
    text = dom.firstChild.getElementsByTagName(tag)[0].firstChild
    if text != None:
        return text.data
    else:
        return 0

# IMPORTANT: make a python module lastfmapi with a class Api that initializes instance variables used below, and provide your own data. 
# will be changed to reading a settings file very soon

api = lastfmapi.Api()
network = pylast.get_lastfm_network(api_key = api.API_KEY, api_secret = api.API_SECRET, username = api.username, password_hash = api.password_hash)

# guess & print guessed age of the user 'preflex'
# formula:
#   guessedAge              = sum_i( playcount_i * weightedAverageAge_i ) / sum_i( playcount_i  )
#   with
#   weightedAverageAge_i    = sum_j( age_i_j     * weight_i_j           ) / sum_j( weight_i_j   )
#   playcount_i ...... playcount for user for artist i
#   age_i_j .......... age of top fan j of artist i
#   weight_i_j ....... last.fm's weight attributed to fan j with regard to artist i

me = network.get_user('preflex')
mytopartists = me.get_top_artists()[0:10]

sum_playcount = 0
sum_playcountavgage = 0
my_inferred_age = 0

countries = {}
countryset = set()

for artist_weight in mytopartists:
  #  print artist_weight
    artist = artist_weight['item']
    weight = artist_weight['weight']
    print "%s x %s" %(artist.get_name().encode('latin-1'), weight.encode('latin-1'))
    
    fans = artist.get_top_fans()
    sum_ageweight = 0
    sum_weight = 0
    avg_age_weighted = 0
    
    countries[artist] = [weight, []] 
    
    for fan_weight in fans:
        fan = fan_weight['item']
        fweight = fan_weight['weight']
        info = fan.get_info()
        # we get 
        
        age = int(getFromUserDOM(info, "age"))
        country = getFromUserDOM(info, "country")
        if country != 0:
            countries[artist][1].append( (country, fweight) )
            countryset.add(country)
        
        #print age
        if age != 0:
            sum_ageweight += age * fweight
            sum_weight += fweight
    
   # print countries[artist]
    
    if sum_weight == 0:
        sum_weight = 1
        
    avg_age_weighted = sum_ageweight / sum_weight
    print "weighted avg age: %d" %(avg_age_weighted)
    
    sum_playcount += int(weight)
    sum_playcountavgage += int(weight) * avg_age_weighted
    
if sum_playcount == 0:
    sum_playcount = 1
    
my_inferred_age = sum_playcountavgage / sum_playcount
print "i guess %s is %d years old" %(me.get_name(), my_inferred_age)

#print countries
#print countryset

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
   #     print "factor %f" % (factor) 
        
        sum_country_weights = 0
        for country_weight in clist:
           # print country_weight
          #  print "........"
            if country_weight[0] == country:
             #   print "added"
                sum_country_weights += country_weight[1]
    
   #     print (factor * sum_country_weights)
        score += factor * sum_country_weights
        
    
    countryscores.append( (country, score) )
  

sortedscores = sorted(countryscores, key = lambda c_s : c_s[1], reverse = True)

#print sortedscores
## calculare the probability that user is from a particular country, for the top five countries
totalscores = sum(map(lambda x : x[1], sortedscores))
for item in sortedscores[0:5]:
    relative = float(item[1]) / float(totalscores)
    print "chance of %s being from %s: %f%%" % (me.get_name(), item[0].encode('latin-1'), relative * 100)
