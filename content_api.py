import urlparse

def content_id(url):
	parsed_url = urlparse.urlparse(url)
	return parsed_url.path