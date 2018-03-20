# -*- coding: utf-8 -*-
import os
import urllib
import xbmcplugin, xbmcgui, xbmcaddon
from urlparse import parse_qs

__addon__ = xbmcaddon.Addon()
__language__  = __addon__.getLocalizedString
sys.path.append(os.path.join( xbmc.translatePath( __addon__.getAddonInfo('path') ), 'resources', 'lib' ))
from logic import *

def Main():
	for menu in TOP_MENU_LIST:
		tmp = menu.split(':')
		if tmp[1] == 'EBS':
			addDir(tmp[0], None, None, True, 'EpisodeList', tmp[1], 'dummy', 1)
		else:
			addDir(tmp[0], None, None, True, 'Menu', tmp[1], None, None)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Menu(p):
	type = p['param']
	list = GetMenuList(type)
	for item in list:
		tmp = item.split(':')
		title = tmp[0]
		param = tmp[1]
		addDir(title, None, None, True, 'ContentList', type, param, 1)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def ContentList(p):
	type = p['param']
	param = p['param2'] if 'param2' in p else None
	pageNo = p['pageNo'] if 'pageNo' in p else None

	hasMore = 'N'
	if type == 'PODBBANG' or type == 'PODTY':
		hasMore, data = GetContentList(type, param, pageNo)
		for item in data:
			title = item['title']
			addDir(title, item['img'], None, True, 'EpisodeList', type, item['id'], '1')
	elif type == 'ITUNES' and (param == 'Audio' or param == 'Video'):
		data = GetItunesGenre(param)
		for item in data:
			addDir(item['name'], None, None, True, 'ContentList', type, item['json'], '1')
	elif type == 'ITUNES' and (param != 'Audio' and param != 'Video'):
		data = GetItunesProgramList(param)
		for item in data:
			plot = item['summary'] + '\n\n' + item['releaseDate']
			infoLabels = {"mediatype":"music","label":item['name'] ,"title":item['name'],"plot":plot}
			addDir(item['name'], item['img'], infoLabels, True, 'EpisodeList', type, item['id'], '1')
	if pageNo != '1':
		addDir('<< ' + __language__(30002).encode('utf8'), None, None, True, 'ContentList', type, param, str(int(pageNo)-1))
	if hasMore == 'Y':
		addDir(__language__(30003).encode('utf8') + ' >>', None, None, True, 'ContentList', type, param, str(int(pageNo)+1))	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def EpisodeList(p):
	type = p['param']
	id = p['param2']
	pageNo = p['pageNo']
	has_more, data = GetEpisodeList(type, id, pageNo)
	isUrl = 'N' if type == 'EBS' else 'Y'
	for item in data:
		param = item['id'] if type == 'EBS' else item['url']
		title = item['title']
		title = '[VIDEO] ' + item['title'] if item['video'] == 'Y' else item['title']
		duration = item['duration'] if 'duration' in item else 0
		infoLabels = {"mediatype":"music","label":item['title'] ,"title":item['title'],"plot":item['plot'], "duration":duration}
		addDir(title, None, infoLabels, False, 'PlayVideo', type, param, isUrl)
	if pageNo != '1':
		addDir('<< Previous', None, None, True, 'EpisodeList', type, id, str(int(pageNo)-1))

	if has_more == 'Y':
		addDir('Next >>', None, None, True, 'EpisodeList', type, id, str(int(pageNo)+1))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
def PlayVideo( p ):
	LOG('PlayVideo : %s' % p)
	type = p['param']
	param = p['param2']
	isUrl = p['pageNo']
	
	if isUrl == 'Y':
		url = param
	else:
		url = GetURL(type, param)
		if url is None:
			addon_noti('Can\'t see')
			return
	item = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


#########################
def addDir(title, img, infoLabels, isFolder, mode, param, param2, pageNo):
	params = {'mode': mode, 'param':param, 'param2':param2, 'pageNo':pageNo}
	url = '%s?%s' %(sys.argv[0], urllib.urlencode(params))
	listitem = xbmcgui.ListItem(title, thumbnailImage=img)
	if infoLabels: listitem.setInfo(type="Video", infoLabels=infoLabels)
	if not isFolder: listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, isFolder)

def addon_noti(sting):
	try:
		dialog = xbmcgui.Dialog()
		dialog.notification(__addon__.getAddonInfo('name'), sting)
	except:
		LOG('addonException: addon_noti')

def get_params():
	p = parse_qs(sys.argv[2][1:])
	for i in p.keys():
		p[i] = p[i][0]
	return p


params = get_params()
try:
	mode = params['mode']
except:
	mode = None
if mode == None: Main()
elif mode == 'Menu': Menu(params)
elif mode == 'ContentList': ContentList(params)
elif mode == 'EpisodeList': EpisodeList(params)
elif mode == 'PlayVideo': PlayVideo(params)
elif mode == 'Test': Test(params)
#else: LOG('NOT FUNCTION!!')