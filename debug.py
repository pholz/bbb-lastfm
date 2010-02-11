import pylast
import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.read('settings.ini')
API_KEY = cfg.get('API','API_KEY')
API_SECRET = cfg.get('API','API_SECRET')
username = cfg.get('USER','username')
password_hash = pylast.md5(cfg.get('USER','password'))

network = pylast.get_lastfm_network(api_key = API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)

me = network.get_user(username)

for item in me.get_top_artists():
    print type(item)