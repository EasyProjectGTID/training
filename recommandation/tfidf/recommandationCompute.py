import collections
import functools
import operator
import pickle
from collections import Counter

import numpy as np
import redis

r = redis.Redis(host='localhost', port=6379, db=2)
def compute(like: list, dislike: list) -> list:
    like_series_similar = []
    dislike_series_similar = []
    # Traitement des series que j'aime en les récuperant dans redis
    for id in like:
        like_series_similar.append(dict(pickle.loads(r.get(id))))

    result_i_like = dict(functools.reduce(operator.add, map(collections.Counter, like_series_similar)))

    for id in dislike:
         dislike_series_similar.append(dict(pickle.loads(r.get(id))))
    result_i_dislike = dict(functools.reduce(operator.add, map(collections.Counter, dislike_series_similar)))

    resultat_list = [result_i_like, result_i_dislike]
    #Resultat final
    resultat = dict(functools.reduce(operator.sub, map(collections.Counter, resultat_list)))
    print('i like', result_i_like)
    print('i dislike', result_i_dislike)
    print('resultat final', resultat)
like =[284]
dislike = [233]
print(compute(like=like, dislike=dislike))