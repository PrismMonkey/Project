# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import requests, re
from bs4 import BeautifulSoup
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils

# Failed:  http://rlsscn.in/?s=Killjoys+s04e04
# Failed:  http://rlsscn.in/?s=killjoys+season+4+episode+4+s04e04+hdtv
# Failed:  http://rlsscn.in/killjoys-s04e04-hdtv/
# Working: http://rlsscn.in/killjoys-season-4-episode-4-s04e04-hdtv/
# Failed:  http://rlsscn.in/killjoys-s04e04-hdtv/
# Working: http://rlsscn.in/killjoys-season-4-episode-4-s04e04
# Working: http://rlsscn.in/Killjoys-season-4-episode-4-s04e04
# Working: http://rlsscn.in/killjoys-season-4-episode-4
# Working: http://rlsscn.in/deadpool-2-2018-unrated-720p-bluray-x264-sparks/
# Working: http://rlsscn.in/deadpool-2-2018

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domain = 'rlsscn.in'
		self.base_link = 'http://rlsscn.in/'
		self.search_link = '%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'localtitle': localtitle, 'aliases': aliases, 'year': year}
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:

			url['episode'] = episode
			url['season'] = season
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):

		hostDict = hostDict + hostprDict
		
		sources = []
		
		
		# they use a peculiar full-word url scheme
		if 'tvshowtitle' in url: 
			request = '%s season %s episode %s' % (url['tvshowtitle'], int(url['season']), int(url['episode'])) 
		else: 
			request = '%s %s' % (url['title'], url['year'])
		request = re.sub('\W+','-',request) 
		request = self.base_link + self.search_link % request
		
		
		# grab the relevent div and chop off the footer
		# log_utils.log('*** request: %s' % request)
		html = client.request(request) 
		html = client.parseDOM(html, "div", attrs={"id": "content"})[0]
		html = re.sub('class="crp_related.+','', html, flags=re.DOTALL)
		
		
		# pre-load *some* size (for movies, mostly)
		try: size0 = re.findall('([0-9,\.]+ ?(?:GB|GiB|MB|MiB))', html)[0] 
		except: size0 = ''
		
		
		# this split is based on TV shows, soooo... might screw up movies
		sects = html.split('<strong>') 
		
		for sect in sects:
			hrefs = client.parseDOM(sect, "a", attrs={"class": "autohyperlink"}, ret='href')
			if not hrefs: continue
		
		
			# filenames (with useful info) seem predictably located
			try: fn = re.match('(.+?)</strong>',sect).group(1)
			except: fn = ''
			
			# sections under filenames usually have sizes (for tv at least)
			try: 
				size = re.findall('([0-9,\.]+ ?(?:GB|GiB|MB|MiB))', sect)[0]
				div = 1 if size.endswith(('GB', 'GiB')) else 1024
				size = float(re.sub('[^0-9\.]', '', size)) / div
				size = '%.2f GB' % size
			except: size = size0
			

			for url in hrefs:
				quality, info = source_utils.get_release_quality(url,fn)
				info.append(size)
				info = ' | '.join(info)
				# log_utils.log(' ** (%s %s) url=%s' % (quality,info,url))

				url = url.encode('utf-8')
				hostDict = hostDict + hostprDict

				valid, host = source_utils.is_host_valid(url, hostDict)
				if not valid: continue
				
				log_utils.log(' ** VALID! (host=%s)' % host)
				sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
								'info': info, 'direct': False, 'debridonly': False})

		return sources


	def resolve(self, url):
		return url

