import collections
import fnmatch
import operator
import os
import nltk
import psycopg2
import pysrt
import re

from django.core.management import BaseCommand
from nltk.corpus import stopwords
import time
from nltk.stem import PorterStemmer
import unidecode
import sys
from django.conf import settings
import sys
import django

cachedStopWords = stopwords.words("french") + stopwords.words("english")


class Command(BaseCommand):
	help = 'Charge et traite les soustitres en BDD'

	def add_arguments(self, parser):
		parser.add_argument('path', nargs='+', type=str)
		parser.add_argument('number_of_core', nargs='+', type=int)
	def handle(self, *args, **options):
		subs = walk_sub(options['path'][0])  # Ne pas oublier le slash a la fin
		totals = time.time()
		import multiprocessing
		pool = multiprocessing.Pool(options['number_of_core'][0])
		pool.map(processing, subs.items())


def getWords(text):
	return re.findall('\w+', text)


def getKey(item):
	return item[1]


def calculTf(corpus, maxi):
	resultat = dict()
	for word, number in corpus.items():
		resultat[word] = (number, round(number / maxi, 4))
	# print(sorted(resultat.items(), key=operator.itemgetter(1), reverse=True))
	return resultat


def maxNB(corpus):
	return corpus[max(corpus, key=corpus.get)]


def read_srt_files(listSrt):
	corpus = collections.Counter()

	for episode in listSrt:
		subs = pysrt.open(episode, encoding='iso-8859-1')

		stemmer = PorterStemmer()

		tokens = nltk.word_tokenize(subs.text)

		#words = [stemmer.stem(unidecode.unidecode(w.lower())) for w in tokens if
				 #w.lower() not in cachedStopWords and len(w) > 2 and w.lower().isalpha()]
		words = [w.lower() for w in tokens if unidecode.unidecode(w.lower()) not in cachedStopWords and len(w) > 2 and w.lower().isalpha()]

		corpus.update(words)

	maxi = maxNB(corpus)

	corpusWithTf = calculTf(corpus, maxi)

	return {'corpus': corpusWithTf, 'lenCorpus': maxi}


def insertInDatabase(serieName, corpus, lenCorpus):
	conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(settings.DATABASES['default']['NAME'],
																					   settings.DATABASES['default']['USER'],
																					   settings.DATABASES['default']['HOST'],
																					   settings.DATABASES['default']['PASSWORD']))
	cur = conn.cursor()
	cur.execute("INSERT INTO recommandation_series (name, max_keyword_nb) VALUES ('{0}', '{1}') returning id".format(serieName, lenCorpus))
	conn.commit()
	serie_id = cur.fetchone()[0]

	for word, value in corpus.items():
		# try:
		key_id = cur.execute(
			"INSERT INTO recommandation_keywords (key) VALUES ('{0}') ON CONFLICT (key) DO UPDATE set key='{0}' returning id".format(word))

		key_id = cur.fetchone()[0]

		cur.execute(
			"INSERT INTO recommandation_posting (number, keywords_id, series_id, tf) VALUES ('{0}','{1}','{2}', '{3}')".format(
				value[0], key_id, serie_id, value[1]))
		conn.commit()


def walk_sub(directory):
	""" Parcours du dossier de sous titres retourne un dictionnaire"""
	seriesPath = dict()
	for root in os.scandir(directory):

		listPath = []
		for racine, dir, files in os.walk(directory + root.name):

			for basename in files:
				if fnmatch.fnmatch(basename, '*.srt'):
					filename = os.path.join(racine, basename)
					listPath.append(filename)

			seriesPath[root.name] = listPath
	return seriesPath


def processing(i):
	key, value = i
	print(key)
	start = time.time()
	text = read_srt_files(value)
	end = time.time()
	startbdd = time.time()
	insertInDatabase(key, text['corpus'], text['lenCorpus'])
	endbdd = time.time()
