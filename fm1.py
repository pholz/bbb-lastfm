import pylast
import lasfmapi

api = lasfmapi.Api()
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
mytopartists = me.get_top_artists()

sum_playcount = 0
sum_playcountavgage = 0
my_inferred_age = 0

for artist_weight in mytopartists:
  #  print artist_weight
    artist = artist_weight['item']
    weight = artist_weight['weight']
    print "%s x %s" %(artist.get_name().encode('latin-1'), weight.encode('latin-1'))
    
    fans = artist.get_top_fans()
    sum_ageweight = 0
    sum_weight = 0
    avg_age_weighted = 0
    
    for fan_weight in fans:
        fan = fan_weight['item']
        weight = fan_weight['weight']
        age = fan.get_age()
        #print age
        if age != 0:
            sum_ageweight += age * weight
            sum_weight += weight
            
    if sum_weight == 0:
        sum_weight = 1
        
    avg_age_weighted = sum_ageweight / sum_weight
    print "weighted avg age: %d" %(avg_age_weighted)
    
    sum_playcount += weight
    sum_playcountavgage += weight * avg_age_weighted
    
if sum_playcount == 0:
    sum_playcount = 1
    
my_inferred_age = sum_playcountavgage / sum_playcount
print "i guess %s is %d years old" %(me.get_name(), my_inferred_age)
    
    
