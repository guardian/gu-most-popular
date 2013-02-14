import webapp2
import jinja2
import os
import json
import logging
import time

from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from google.appengine.ext import deferred

import headers
import ophan
import content_api
import formats

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

TEN_MINUTES = 10 * 60

def fresh(current_seconds):
	return (time.time() - current_seconds) < TEN_MINUTES

def resolve_content(url):
	params = {'show-fields' : 'headline,thumbnail,trailText'}

	result = content_api.read(content_api.content_id(url), params)

	if result:
		data = json.loads(result)
		return data.get('response', {}).get('content', {})
	return None

def read_ophan(section_id = None):

	client = memcache.Client()

	last_read = client.get(section_id + ".epoch_seconds")

	if last_read and fresh(last_read): return

	ophan_json = None

	if section_id == 'all':
		ophan_json = ophan.popular()
	else:
		ophan_json = ophan.popular(section_id = section_id)		

	if not ophan_json:
		raise deferred.PermanentTaskFailure()

	ophan_data = json.loads(ophan_json)

	resolved_stories = [resolve_content(entry['url']) for entry in ophan_data]

	resolved_stories = [story for story in resolved_stories if not story == None]

	client = memcache.Client()

	base_key = 'all'

	if section_id: base_key = section_id

	if len(resolved_stories) > 0:
		client.set(base_key, json.dumps(resolved_stories))
		client.set(base_key + '.epoch_seconds', time.time())

	logging.info("Updated data for section %s; listing %d stories" % (section_id, len(resolved_stories)))	

def refresh_data(section_id):
	deferred.defer(read_ophan, section_id = section_id)

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class MostViewed(webapp2.RequestHandler):
	def get(self, section_id = None):
		if not section_id: section_id = 'all'

		client = memcache.Client()

		ophan_json = client.get(section_id)
		
		if not ophan_json:
			refresh_data(section_id)
			ophan_json = "[]"

		last_read = client.get(section_id + ".epoch_seconds")

		if last_read and not fresh(last_read):
			refresh_data(section_id)

		headers.json(self.response)
		headers.set_cache_headers(self.response, 60)
		headers.set_cors_headers(self.response)
		self.response.out.write(formats.jsonp(self.request, ophan_json))
