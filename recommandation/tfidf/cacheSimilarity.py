import operator
import pickle
import time

import psycopg2
import numpy
import math
import math
from collections import Counter
from nltk import cluster
import redis
r = redis.Redis(host='localhost', port=6379, db=2)
conn = psycopg2.connect("dbname='django123' user='postgres' host='localhost' password=''")
def cosine_distance(serie_id, u, v):
    """
    Returns the cosine of the angle between vectors v and u. This is equal to
    u.v / |u||v|.
    """
    return serie_id, numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))

def buildVector(seriename, serie1, serie2):

    counter1 = serie1
    counter2 = serie2

    counter1_c = Counter()
    counter2_c = Counter()

    for k in counter1:
        #print(k)
        counter1_c[k[0]] = k[1]
    for k in counter2:
        counter2_c[k[0]] = k[1]

    all_items = set(counter1_c.keys()).union(set(counter2_c.keys()))
    vector1 = [float(counter1_c[k]) for k in all_items]
    vector2 = [float(counter2_c[k]) for k in all_items]

    return seriename, vector1, vector2
def construct(serie_pk):

    cur.execute(
        "select s.id from recommandation_series s where s.id='{}'".format(serie_pk))
    serie_id = cur.fetchall()[0][0]

    cur.execute(
        "select * from mv_{}".format(serie_id))
    serie_comparer = cur.fetchall()

    cur.execute("select s.id from recommandation_series s where s.id <> '{}'".format(serie_id))
    others = cur.fetchall()
    resultat = []
    start = time.time()
    for other in others:
        cur.execute("select s.name from recommandation_series s where s.id='{}'".format(other[0]))
        seriename = cur.fetchall()[0][0]

        cur.execute("select * from mv_{}".format(other[0]))
        other_words = cur.fetchall()

        seriename, v1, v2 = buildVector(seriename, serie_comparer, other_words)

        resultat.append(cosine_distance(seriename, v1, v2))

    resultat_trier = sorted(resultat, key=operator.itemgetter(1), reverse=True)
    #print(resultat_trier)
    r.set(serie_pk, pickle.dumps(resultat_trier))



cur = conn.cursor()
cur.execute(
        "select s.id from recommandation_series s")
series= cur.fetchall()
for serie in series:
    construct(serie[0])


