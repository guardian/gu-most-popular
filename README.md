gu-most-popular
===============

A most popular app built on top of Ophan.

## Design

The app uses the in-built deferred library to minimise traffic to Ophan.

## Getting things running

This app runs on Google App Engine

It reads two keys out of Memcache that must be setup for the app to work.

* OPHAN_HOST : the location of the Ophan API
* API_KEY : your api key (optional in development as the app only uses public fields)

