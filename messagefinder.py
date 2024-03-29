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
db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="jvdata", charset='utf8', unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock')
db.set_character_set('utf8')

# GLOBALS
nb_posts = 0
nb_integrityErrors = 0
current_page = 1

# Main Function
def main():
	global current_page
	s = requests.Session()
	i = 10700000 - 10000
	while 1:
		r = singleRequest('https://www.jeuxvideo.com/ultrapoutch/forums/message/' + str(i), s)
		get_messages(r)
		print 'https://www.jeuxvideo.com/ultrapoutch/forums/message/' + str(i)
		i += 1

# Parse each message
def get_messages(page):
	global current_page
	global nb_posts
	global nb_integrityErrors
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
		try:
			message_raw = s.find('div', attrs={'class': 'text-enrichi-forum'})
			message = unicode(message_raw.renderContents(), 'utf8')
		except:
			message = ""

		# DATE
		date = s.find('div', attrs={'class': 'bloc-date-msg'}).text.replace('\n', '').replace('"', '').lstrip()
		date = parse_date(date)

		# AVATAR
		try:
			avatar = s.find('img', attrs={'class': 'user-avatar-msg'})
			avatar = avatar['data-srcset'].replace('avatar-sm', 'avatar-md').replace('//image.jeuxvideo.com/', '') # Add 'image.jeuxvideo.com' in frontend
		except:
			avatar = "image.jeuxvideo.com/avatar-md/default.jpg"
		print str(current_page) + 'th page | ' + magenta + str(date.strftime('%d %b %Y')) + white + ' | ' + str(nb_posts) + ' posts | ' + red + str(nb_integrityErrors) + ' IE' + white + ' | ' + yellow +  pseudo + white

		# NOELSHACKS 
		if "noelshack.com" in message:
			try:
				noelshack = BeautifulSoup(message, "html.parser")
				les_noels = noelshack.find_all('a', attrs={'data-def': 'NOELSHACK'})
				for le_noel in les_noels:
					shack = str(le_noel.img['src']).replace('//image.noelshack.com/minis/', '') # Add 'image.noelshack.com/minis/' in frontend for a miniature
					cursor = db.cursor()														# Add 'http://image.noelshack.com/fichiers/' in frontend for fullpicture
					cursor.execute("""INSERT INTO gallery (pseudo,ancre,shack,date,avatar) VALUES (%s,%s,%s,%s,%s) """,(pseudo,ancre,shack,date,avatar))
					db.commit()
			except:
				pass

		row_list = (pseudo, ancre, message, date, avatar)
		bulk_insert.append(row_list)
		# cursor.execute("""INSERT INTO messages (pseudo,ancre,message,date,avatar) VALUES (%s,%s,%s,%s,%s) """,(pseudo,ancre,message_raw,date,avatar))
	# threads = []
	# t = threading.Thread(target=bulkinsert, args=(bulk_insert,))
	# threads.append(t)
	# t.start()

	bulk_insert = bulk_insert[::-1]
	if bulkinsert(bulk_insert) == 1:
		return 1
	return 0
	
def bulkinsert(bulk_insert):
	global nb_posts
	global nb_integrityErrors
	cursor = db.cursor()
	for row in bulk_insert:
		try:
			cursor.execute("""INSERT INTO messages (pseudo,ancre,message,date,avatar) VALUES (%s,%s,%s,%s,%s) """, row)
			nb_posts += 1
			# cursor.execute("""INSERT INTO messages (pseudo,ancre,date) VALUES (%s,%s,%s) """, row)
		# except Exception, e: print repr(e)
		except MySQLdb.IntegrityError:
			print red + 'IE' + white
			nb_integrityErrors += 1
			db.commit()
			return 1
		except MySQLdb.OperationalError, e:
			pass
			# cursor.execute("""INSERT INTO messages (pseudo,ancre,date,avatar) VALUES (%s,%s,%s,%s) """, row)
			# db.commit()
		# except Exception, e: print repr(e)
	db.commit()
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









