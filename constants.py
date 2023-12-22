import configparser
import os

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), 'configs/config.local'))

YOUTUBE_API_KEY = parser.get('youtube', 'API_KEY')
PLAYLIST_ID=parser.get('youtube','PLAYLIST_ID')