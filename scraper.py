# -*- coding: utf-8 -*-

import sys
import os
import math
from variables import *
from bs4 import BeautifulSoup


def main(): 
	s = requests.Session()
	url1 = "http://www.jeuxvideo.com/forums/0-1000021-0-1-0-"
	page = 1
	url2 = "-0-communaute.htm"
	url = url1 + str(page) + url2
	topic_list = get25Topics(url, s)
	fromLastPage(topic_list, s)

def get25Topics(url, s):
	r = singleRequest(url, s)
	if r != False:
		soup = BeautifulSoup(r.text, "html.parser")
		topics = soup.find_all('li')
		topic_list = []
		for topic in topics:
			topic_name = topic.find('a', 'lien-jv topic-title')
			if (topic_name):
				topic_link = topic_name['href']
				topic_nbmsg = topic.find('span', 'topic-count')
				topic_nbmsg = topic_nbmsg.text.replace(' ', '').replace('\n', '')
				topic_nbmsg = int(topic_nbmsg) + 1
				if topic_nbmsg:
					topic_nbpage = float(topic_nbmsg) / 20
					topic_nbpage = int(math.ceil(topic_nbpage))
					if topic_nbpage == 0:
						topic_nbpage = 1
					topic_lastpage = topic_link.split('-')
					topic_lastpage[3] = str(topic_nbpage + 1)
					topic_lastpage = '-'.join(topic_lastpage)
					topic_list.append('https://www.jeuxvideo.com' + topic_lastpage)
	return topic_list

def fromLastPage(topic_list, s):
	i = 0
	for topic in topic_list:
		previous = topic.split('-')
		previous_page = int(previous[3]) - 1
		if previous_page < 1:
			return
		previous[3] = str(previous_page)
		topic = '-'.join(previous)
		print cyan + topic + white
		singleRequest(topic, s)

main()















