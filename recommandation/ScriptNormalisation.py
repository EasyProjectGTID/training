import collections
import fnmatch
import os

import nltk
import psycopg2
import pysrt
import re
from nltk.corpus import stopwords
import operator
from collections import Counter
import time
from nltk.stem.snowball import FrenchStemmer, EnglishStemmer
from flashtext.keyword import KeywordProcessor
from textblob import TextBlob
from nltk import word_tokenize
cachedStopWords = stopwords.words("french") + stopwords.words("english")
print(cachedStopWords)

def _calculate_languages_ratios(text):
    """
    Calculate probability of given text to be written in several languages and
    return a dictionary that looks like {'french': 2, 'spanish': 4, 'english': 0}

    @param text: Text whose language want to be detected
    @type text: str

    @return: Dictionary with languages and unique stopwords seen in analyzed text
    @rtype: dict
    """

    languages_ratios = {}

    '''
    nltk.wordpunct_tokenize() splits all punctuations into separate tokens

    >>> wordpunct_tokenize("That's thirty minutes away. I'll be there in ten.")
    ['That', "'", 's', 'thirty', 'minutes', 'away', '.', 'I', "'", 'll', 'be', 'there', 'in', 'ten', '.']
    '''

    tokens = nltk.wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    # Compute per language included in nltk number of unique stopwords appearing in analyzed text
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        languages_ratios[language] = len(common_elements)  # language "score"

    return languages_ratios


# ----------------------------------------------------------------------
def detect_language(text):
    """
    Calculate probability of given text to be written in several languages and
    return the highest scored.

    It uses a stopwords based approach, counting how many unique stopwords
    are seen in analyzed text.

    @param text: Text whose language want to be detected
    @type text: str

    @return: Most scored language guessed
    @rtype: str
    """

    ratios = _calculate_languages_ratios(text)

    most_rated_language = max(ratios, key=ratios.get)

    return most_rated_language


def getWords(text):
    return re.findall('\w+', text)

def getKey(item):
    return item[1]

def calculTf(corpus, maxi):
    resultat = dict()
    for word, number in corpus.items():
        resultat[word] = (number, number / maxi)

    return resultat

def maxNB(corpus):
    return corpus[max(corpus, key=corpus.get)]

# def read_srt_files(listSrt):
#     stemmer = FrenchStemmer()
#     list = []
#
#     for episode in listSrt:
#         subs = pysrt.open(episode, encoding='iso-8859-1')
#
#         for ligne in range(len(subs)):
#             for mot in getWords(subs[ligne].text):
#                 if len(mot) > 2:
#                     list.append(mot.lower())
#
#
#     filtered_words = []
#     for word in list:
#         if word not in cachedStopWords:
#             filtered_words.append(stemmer.stem(word))
#
#     corpus = Counter(' '.join(filtered_words).split())
#     maxi = maxNB(corpus)
#     corpusWithTf = calculTf(corpus, maxi)
#     return {'corpus':corpusWithTf, 'lenCorpus':maxi}

def read_srt_files(listSrt):
    corpus = collections.Counter()


    for episode in listSrt:

        subs = pysrt.open(episode, encoding='iso-8859-1')
        language = detect_language(subs.text[0:1000])
        if language == 'french':
            stemmer = FrenchStemmer()
        elif language == 'english':
            stemmer = EnglishStemmer()

        tokens = nltk.word_tokenize(subs.text)

        words = [stemmer.stem(w.lower()) for w in tokens if w.lower() not in cachedStopWords and len(w) > 2 and w.lower().isalpha()]



        corpus.update(words)

    maxi = maxNB(corpus)
    print(len(corpus))
    corpusWithTf = calculTf(corpus, maxi)
    return {'corpus':corpusWithTf, 'lenCorpus':maxi}

def insertInDatabase(serieName, corpus, lenCorpus):

    cur = conn.cursor()
    cur.execute("INSERT INTO recommandation_series (name, max_keyword_nb) VALUES ('{0}', '{1}') returning id".format(serieName, lenCorpus))
    conn.commit()
    serie_id = cur.fetchone()[0]

    for word, value in corpus.items():
        # try:
        key_id =cur.execute(
            "INSERT INTO recommandation_keywords (key) VALUES ('{0}') ON CONFLICT (key) DO UPDATE set key='{0}' returning id".format(word))

        key_id = cur.fetchone()[0]


        # except Exception as e:
        #     print(e)
        #     # conn.rollback()
        #     # cur.execute("SELECT k.id from recommandation_keywords as k where k.key='{}'".format(word))
        #     # key_id = cur.fetchone()[0]

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


conn = psycopg2.connect("dbname='django123' user='postgres' host='localhost' password=''")
subs = walk_sub('/home/hadrien/Bureau/test/') # Ne pas oublier le slash a la fin

tot = 0
totals = time.time()
for key, value in subs.items():
    start = time.time()
    text = read_srt_files(value)
    end = time.time()

    startbdd = time.time()
    insertInDatabase(key, text['corpus'], text['lenCorpus'])
    tot += 1
    endbdd = time.time()
    print('INSERT IN BDD:{0} READ SRT :{1} --- {2} / {3}'.format(endbdd - startbdd, end - start, tot, len(subs.items())))

fin = time.time()
print('TOTAL DU TRAITEMENT :', fin - totals)