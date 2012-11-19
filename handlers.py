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

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

FIVE_MINUTES = 5 * 60

def fresh(current_seconds):
	return (time.time() - current_seconds) < FIVE_MINUTES

def resolve_content(url):
	params = {'show-fields' : 'headline,thumbnail,trailText'}

	data = json.loads(content_api.read(content_api.content_id(url), params))
	return data.get('response', {}).get('content', {})

def read_ophan(section_id = None):

	ophan_json = None

	if section_id:
		ophan_json = ophan.popular(section_id = section_id)
	else:
		ophan_json = ophan.popular()

	if not ophan_json:
		raise deferred.PermanentTaskFailure()

	ophan_data = json.loads(ophan_json)

	client = memcache.Client()

	resolved_stories = [resolve_content(entry['url']) for entry in ophan_data]

	client = memcache.Client()

	base_key = 'all'

	if section_id: base_key = section_id

	client.set(base_key, json.dumps(resolved_stories))
	client.set(base_key + '.epoch_seconds', time.time())	

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
			try:
				deferred.defer(read_ophan, section_id = section_id, _name = section_id)
			except taskqueue.DuplicateTaskNameError:
				# Ignore dogpiling
				pass
			ophan_json = "[]"

		last_read = client.get(section_id + ".epoch_seconds")

		if last_read and not fresh(last_read):
			deferred.defer(read_ophan)

		headers.json(self.response)
		headers.set_cache_headers(self.response, 60)
		self.response.out.write(ophan_json)
