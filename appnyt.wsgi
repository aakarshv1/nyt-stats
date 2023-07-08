#! /home/ubuntu/nyt-stats/nyt-stats/nytenv/bin/python

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ubuntu/nyt-stats/nyt-stats')
from appnyt import app as application
application.secret_key = 'Cignama1e*^@303834'
