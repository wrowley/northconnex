import urllib
import urllib2
from HTMLParser import HTMLParser
import os
import re
import time
import sys

class NorthConnexHTMLParser(HTMLParser):
	HTTP_NORTH_CONNEX_BASE    = r'http://northconnex.com.au/'
	HTTP_NORTH_CONNEX_LIBRARY = HTTP_NORTH_CONNEX_BASE + r'library.php'

	def __init__(self):
		HTMLParser.__init__(self)

		self._care_about_data = False
		self._attrs = None
		self._docs  = []

		north_connex_html = urllib2.urlopen(self.HTTP_NORTH_CONNEX_LIBRARY).read()
		self.feed(north_connex_html)

	@staticmethod
	def find_href(attrs):
		# We just want to find where the document lives
		for attr in attrs:
			if 'href' == attr[0]:
				return attr[1]
		return None

	def handle_starttag(self, tag, attrs):
		# We only care about links
		if 'a' == tag:
			self._care_about_data = True
			self._attrs = attrs

	def handle_endtag(self, tag):
		# We only care about links
		if 'a' == tag:
			self._care_about_data = False
			self._attrs = None

	def handle_data(self, data):
		# Capture where the PDF lives
		if self._care_about_data:
			href = self.find_href(self._attrs)
			if href and href.endswith('.pdf'):
				true_href = self.HTTP_NORTH_CONNEX_BASE + href
				self._docs.append((data,true_href))

	def get_docs(self):
		# Return everything we know
		return self._docs

start_time = time.time()
def reporthook(count, block_size, total_size):
	'''Original taken from http://blog.moleculea.com/2012/10/04/urlretrieve-progres-indicator/'''
	duration = time.time() - start_time
	progress_size = int(count * block_size)
	speed = int(progress_size / (1024 * duration))
	percent = min(int(count * block_size * 100 / total_size), 100)
	sys.stdout.write("\r...%d%%, %d KB, %d KB/s, %d seconds passed" %
	                (percent, progress_size / (1024), speed, duration)
	                )
	sys.stdout.flush()

BASE_FOLDER = 'northconnex'

def main():
	# Find where all the docs are
	parser = NorthConnexHTMLParser()
	docs = parser.get_docs()

	# Download them all
	for name,link in docs:
		# We can do something clever about where we want to save them to
		save_location = None
		parts = name.split(' - ')
		if len(parts) >= 2:
			folder = parts[0]
			mo = re.match(r'Section ([0-9])',folder)
			if mo:
				folder = 'Chapter ' + str(mo.group(1))
			folder = os.path.join(BASE_FOLDER,folder)
			document = name + '.pdf'
		else:
			folder = BASE_FOLDER
			document = name + '.pdf'

		# Try and make the folder if it doesn't exist
		try:
			if not os.path.isdir(folder):
				os.mkdir(folder)
		except:
			print "couldn't make directory:",folder
			continue

		# Download it
		save_location = os.path.join(folder,document)
		if save_location:
			print 'Downloading', document, 'to\n', save_location
			urllib.urlretrieve(link, save_location, reporthook)
			print '\n'

if __name__ == '__main__':
	main()
