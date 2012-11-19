import urlparse
import urllib

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
		url = url + "?" + urllib.urlencode(params)

	cached_data = client.get(url)

	if cached_data: return cached_data

	result = fetch(url)

	if not result.status_code == 200:
		return None

	client.set(url, result.content, time = 60 * 5)

	return result.content
