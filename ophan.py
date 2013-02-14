from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
from google.appengine.ext import ndb

import logging
import urllib
from models import Configuration

client = memcache.Client()

FIFTEEN_MINUTES = 15 * 60


def popular(section_id = None):
	results = Configuration.query(Configuration.key == "OPHAN_API_KEY")
	if not results.iter().has_next():
		return None

	ophan_api_key = results.iter().next().value
	logging.info(ophan_api_key)

	most_read_url = "http://api.ophan.co.uk/api/mostread"

	if section_id:
		most_read_url = most_read_url + "/" + section_id

	params = {'age' : FIFTEEN_MINUTES,
		'api-key' : ophan_api_key}

	most_read_url = most_read_url + "?" + urllib.urlencode(params)

	logging.info(most_read_url)

	result = fetch(most_read_url)

	if result.status_code == 200:
		return result.content

	logging.error("Ophan read failed with status code %d" % result.status_code)
	return None