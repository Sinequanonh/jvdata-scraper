# -*- coding: utf-8 -*-

import sys
import re
import os
import math
from datetime import datetime
import threading
from variables import *
from get_messages import *
from bs4 import BeautifulSoup, SoupStrainer
import MySQLdb
from cgi import escape
from collections import Counter

# connect
db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="jvdata", unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock')

# Main Function
def main(): 
	s = requests.Session()
	url1 = "http://www.jeuxvideo.com/forums/0-1000021-0-1-0-"
	page = 1
	url2 = "-0-communaute.htm"

	while 1:
		url = url1 + str(page) + url2
		print red + url + white
		topic_list = get25Topics(url, s)
		fromLastPage(topic_list, s)
		page += 25

# Get the 25 topics from the page
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

# Get to the first page from the last one
def fromLastPage(topic_list, s):
	for topic in topic_list:
		while int(topic.split('-')[3]) > 1:
			previous = topic.split('-')
			previous_page = int(previous[3]) - 1
			previous[3] = str(previous_page)
			topic = '-'.join(previous)
			print cyan + topic + white
			r = singleRequest(topic, s)
			if type(r) != bool:
				if get_messages(r) == 1:
					break

# Parse each message
def get_messages(page):
	bloc_message = SoupStrainer('div', {'class': 'bloc-message-forum '})
	soup = BeautifulSoup(page.text, "html.parser", parse_only=bloc_message)
	bulk_insert = []
	trends = []
	for s in soup:
		# PSEUDO
		try:
			pseudo = s.find('span', attrs={'class': 'bloc-pseudo-msg'})
			pseudo = pseudo.getText().replace(' ', '').replace('\n', '')
		except:
			pseudo = "Pseudo supprime"
		# ANCRE
		ancre = s['data-id']
		# MESSAGE
		message_raw = s.find('div', attrs={'class': 'text-enrichi-forum'})
		message = message_raw.renderContents().replace('\n', '')
		message_raw = message_raw.getText()
		message_raw = ' '.join(message_raw.split())

		each_word = message_raw.split(' ')
		for word in each_word:
			trends.append(word)

		nb_mots = len(message_raw.split(' '))
		nb_chars = len(message_raw)

		# DATE
		date = s.find('div', attrs={'class': 'bloc-date-msg'}).text.replace('\n', '').replace('"', '').lstrip()
		date = parse_date(date)

		# AVATAR
		try:
			avatar = s.find('img', attrs={'class': 'user-avatar-msg'})
			avatar = avatar['data-srcset'].replace('avatar-sm', 'avatar-md').replace('//image.jeuxvideo.com/', '') # Add 'image.jeuxvideo.com' in frontend
		except:
			avatar = "image.jeuxvideo.com/avatar-md/default.jpg"	
		print ancre + ' ' + pseudo

		row_list = (pseudo, ancre, message_raw, date, avatar)
		bulk_insert.append(row_list)
		# cursor.execute("""INSERT INTO messages (pseudo,ancre,message,date,avatar) VALUES (%s,%s,%s,%s,%s) """,(pseudo,ancre,message_raw,date,avatar))
	# threads = []
	# t = threading.Thread(target=bulkinsert, args=(bulk_insert,))
	# threads.append(t)
	# t.start()
	
	# c=Counter(trends)
	# k = c.most_common()
	# ban_loop = 1
	# ban = 0

	# print 'Most Common Word 1: ' + yellow + k[ban][0] + white

	bulk_insert = bulk_insert[::-1]
	# print bulk_insert
	if bulkinsert(bulk_insert) == 1:
		return 1
	return 0
	
def bulkinsert(bulk_insert):
	cursor = db.cursor()
	for row in bulk_insert:
		try:
			cursor.execute("""INSERT INTO messages (pseudo,ancre,message,date,avatar) VALUES (%s,%s,%s,%s,%s) """, row)
			db.commit()
		except MySQLdb.IntegrityError:
			return 1
	return 0

def parse_date(date):
	p_date = date.split(' ')
	# Encode characters
	d = p_date[0]
	p_date[1] = p_date[1].encode('utf8', 'replace')
	if 'janvier' in p_date[1]:
		m = '01'
	elif 'février' in p_date[1]:
		m = '02'
	elif 'mars' in p_date[1]:
		m = '03'
	elif 'avril' in p_date[1]:
		m = '04'
	elif 'mai' in p_date[1]:
		m = '05'
	elif 'juin' in p_date[1]:
		m = '06'
	elif 'juillet' in p_date[1]:
		m = '07'
	elif 'août' in p_date[1]:
		m = '08'
	elif 'septembre' in p_date[1]:
		m = '09'
	elif 'octobre' in p_date[1]:
		m = '10'
	elif 'novembre' in p_date[1]:
		m = '11'
	elif 'décembre' in p_date[1]:
		m = '12'
	y = p_date[2]
	h = p_date[4].split(':')
	ladate = datetime(int(y), int(m), int(d), int(h[0]), int(h[1]), int(h[2]))
	return ladate

main()









