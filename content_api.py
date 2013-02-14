import urlparse
import urllib
import logging

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache

CONTENT_API_HOST = 'content.guardianapis.com'

def content_id(url):
	parsed_url = urlparse.urlparse(url)
	return parsed_url.path

def read(content_id, params = None):
	client = memcache.Client()

	url = "http://%s%s" % (CONTENT_API_HOST, content_id)

	if params:
		cached_key = client.get('API_KEY')
		if not 'api-key' in params and cached_key:
			params['api-key'] = cached_key
		url = url + "?" + urllib.urlencode(params)

	#logging.debug(url)

	cached_data = client.get(url)

	if cached_data: return cached_data

	result = fetch(url)

	if not result.status_code == 200:
		logging.warning("Content API read failed: %d" % result.status_code)
		return None

	client.set(url, result.content, time = 60 * 15)

	return result.content
