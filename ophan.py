from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache


import settings
import logging
import urllib

client = memcache.Client()

FIFTEEN_MINUTES = 15 * 60


def popular(section_id = None):
	most_read_url = "http://%s/api/mostread" % client.get("OPHAN_HOST")

	if section_id:
		most_read_url = most_read_url + "/" + section_id

	params = {'age' : FIFTEEN_MINUTES}

	most_read_url = most_read_url + "?" + urllib.urlencode(params)

	logging.info(most_read_url)

	result = fetch(most_read_url)

	if result.status_code == 200:
		return result.content

	logging.error("Ophan read failed with status code %d" % result.status_code)
	return None