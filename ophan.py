from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache


import settings
import logging

client = memcache.Client()


def popular(section_id = None):
	most_read_url = "http://%s/api/mostread" % client.get("OPHAN_HOST")

	result = fetch(most_read_url)

	if result.status_code == 200:
		return result.content
	return None