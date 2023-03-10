# -*- coding: utf-8 -*-
"""DA1AS3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AW8pkri2grV0eseeSxUHNv-n5RDFL8BI
"""

import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

# from google.colab import drive
# drive.mount('/content/gdrive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gdrive/My Drive/ml-latest-small

df_ratings = pd.read_csv('../ml-latest-small/ratings.csv')

df_ratings.head()

df_movies = pd.read_csv('../ml-latest-small/movies.csv')

df_movies.head()
print("ok")

"""transactional data set, which consists of entries of the form
<user id, {movies rated above 2}>.
"""

txn_st  = {}
for ind,x in df_ratings.iterrows():
  if(x[2]<=2):
    continue
  if x[0] in txn_st:
    txn_st[x[0]].append(x[1])
  else:
    txn_st[x[0]]=[x[1]]

"""filtering out the users whose rated movies ar eless than 10"""

txn_st_moviesgt10 = {}
for user in txn_st:
  if(len(txn_st[user]) >10):
    txn_st_moviesgt10[user] = txn_st[user]

print(len(txn_st))
print(len(txn_st_moviesgt10))

"""Dividing the data into train and test sets"""

import random
txn_st_train={}
txn_st_test = {}
for user in txn_st_moviesgt10:
  mvs = txn_st_moviesgt10[user]
  random.shuffle(mvs)
  split = int(len(mvs)*0.8)
  train_mvs = mvs[:split]
  test_mvs  = mvs[split:]
  txn_st_train[user] = train_mvs
  txn_st_test[user]  = test_mvs

movies_train = []
for user in txn_st_train:
  for movie in txn_st_train[user]:
    movies_train.append(movie)

movies_train_unique = np.unique(np.array(movies_train))

print(len(txn_st_train))
print(len(movies_train))
print(len(movies_train_unique))

minsup = 0.09
minconf = 0.1

def support(movies):
  cnt=0
  for user in txn_st_train:
    f = True
    for movie in movies:
      if(movie in txn_st_train[user]):
        f = f & True
      else:
        f = f & False
        break
    if(f):
      cnt+=1

  return cnt/len(txn_st_train)

asr_movies_sup = {}
for movie in movies_train_unique:
  sup = support([movie])
  if(sup >= minsup):
    asr_movies_sup[movie]=sup

print(len(asr_movies_sup))

movies_train_dec_sup = sorted(asr_movies_sup.items(), key=lambda kv:kv[1], reverse=True)

print(movies_train_dec_sup)

movies_stminsup = list(asr_movies_sup.keys())

print(len(movies_stminsup))

l1_movies = movies_stminsup

l2_movies=[]
for i in range(len(l1_movies)):
  for j in range(i+1, len(l1_movies)):
    l2 = [l1_movies[i],l1_movies[j]]
    sup = support(l2)
    if(sup>=minsup):
      l2_movies.append(l2)

print(len(l2_movies))

l3_movies=[]
for i in range(len(l2_movies)):
  for j in range(i+1,len(l2_movies)):
    if(sorted(l2_movies[i][:-1])==sorted(l2_movies[j][:-1])):
      l3 = l2_movies[i][:-1]
      l3.append(l2_movies[i][-1])
      l3.append(l2_movies[j][-1])
      sup = support(l3)
      if(sup>=minsup):
        l3_movies.append(l3)

print(len(l3_movies))

print(l3_movies)

l4_movies=[]
for i in range(len(l3_movies)):
  for j in range(i+1,len(l3_movies)):
    if(sorted(l3_movies[i][:-1])==sorted(l3_movies[j][:-1])):
      l4 = l3_movies[i][:-1]
      l4.append(l3_movies[i][-1])
      l4.append(l3_movies[j][-1])
      sup = support(l4)
      if(sup>=minsup):
        l4_movies.append(l4)

print(len(l4_movies))

ass_rules=[]
for x in l2_movies:
  s = support(x)
  conf1 = s/support([x[0]])
  conf2 = s/support([x[1]])
  if(conf1 >= minconf):
    ass_rules.append([x[0],[x[1]],s,conf1])
  if(conf2 >= minconf):
    ass_rules.append([x[1],[x[0]],s,conf2])

for x in l3_movies:
  s = support(x)
  conf1 = s/support([x[0]])
  conf2 = s/support([x[1]])
  conf3 = s/support([x[2]])
  if(conf1 >= minconf):
    ass_rules.append([x[0],[x[1],x[2]],s,conf1])
  if(conf2 >= minconf):
    ass_rules.append([x[1],[x[0],x[2]],s,conf2])
  if(conf3 >= minconf):
    ass_rules.append([x[2],[x[0],x[1]],s,conf2])

print(ass_rules)

top_sup_rules=sorted(ass_rules, key=lambda x: x[2], reverse=True)
top_conf_rules=sorted(ass_rules, key=lambda x: x[3], reverse=True)

print(top_sup_rules)

print(top_conf_rules)

top100_sup_rules=top_sup_rules[:100]
top100_conf_rules=top_conf_rules[:100]

common_sup_conf_rules=[]
for x in top100_conf_rules:
  if x in top100_sup_rules:
    common_sup_conf_rules.append(x)

print(len(common_sup_conf_rules))
print(common_sup_conf_rules)

"""3"""

precision_avgs=[]
recall_avgs=[]
for k in range(1,11):
  for user in  txn_st_train:
    mvs_train = txn_st_train[user]
    mvs_test = txn_st_test[user]
    recall_sum=0
    precision_sum=0
    r=[]
    for x in mvs_train:
      y=[]
      c=0
      for asr in top_conf_rules:
        if(asr[0]==x):
          y = y+ asr[1]
          c+=1
          if(c==k):
            break
      r = r + y
    hs = []
    for m in r:
      if m in mvs_test:
        hs.append(m)
    recall = len(hs)/len(mvs_test)
    if(len(r)==0):
      precision=0
    else:
      precision = len(hs)/len(r)
    recall_sum+=recall
    precision_sum+=precision
  recall_avg = recall_sum / len(txn_st_train)
  precision_avg = precision_sum / len(txn_st_train)
  precision_avgs.append(precision_avg)
  recall_avgs.append(recall_avg)

print(precision_avgs)
print(recall_avgs)

x=[i for i in range(1,11)]
plt.plot(x,precision_avgs,label='precision')
plt.plot(x,recall_avgs, label='recall')
plt.legend()

"""4)"""

sample_test=random.sample(list(txn_st_train),10)
x1=[i for i in range(1,11)]
plt.figure(figsize=(25,5)) 
for i in  range(len(sample_test)):
  user = sample_test[i]
  mvs_train = txn_st_train[user]
  mvs_test = txn_st_test[user]
  y1=[]
  y2=[]
  for k in range(1,11):
    r=[]
    for x in mvs_train:
      y=[]
      c=0
      for asr in top_conf_rules:
        if(asr[0]==x):
          y = y+ asr[1]
          c+=1
          if(c==k):
            break
      r = r + y
    hs = []
    for m in r:
      if m in mvs_test:
        hs.append(m)
    recall = len(hs)/len(mvs_test)
    if(len(r)==0):
      precision=0
    else:
      precision = len(hs)/len(r)
    y1.append(precision)
    y2.append(recall)

  plt.subplot(1,10,i+1)
  plt.title('user = '+str(user))
  plt.plot(x1,y1)
  plt.plot(x1,y2)
plt.show()

# saving the association rules.
with open('Hakuna_matata_AssocRules.txt','w') as f:
  for row in ass_rules:
    line = ""
    for x in row:
      line += str(x) + " "
    f.write(line)
  f.close()

# saving the  max sup association rules.
with open('Hakuna_matata_RulesMaxSupport.txt','w') as f:
  for row in top100_sup_rules:
    line = ""
    for x in row:
      line += str(x) + " "
    f.write(line)
  f.close()

# saving the  max conf association rules.
with open('Hakuna_matata_RulesMaxConf.txt','w') as f:
  for row in top100_sup_rules:
    line = ""
    for x in row:
      line += str(x) + " "
    f.write(line)
  f.close()

