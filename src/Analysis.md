```python
>>> %matplotlib inline
>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> import sqlite3
>>> import re
>>> import math
>>> import nltk
>>> import twitter
>>> import ux
>>> import fx
>>> from itertools import islice
>>> from collections import Counter
```

```python
>>> conn = sqlite3.connect('../data/heavy/text.btce.db')
>>> cur = conn.cursor()
```

```python
>>> MIN_TIME = cur.execute('select min(time) from messages').fetchone()[0]
>>> MAX_TIME = cur.execute('select max(time) from messages').fetchone()[0]
...
>>> MIN_TIME, MAX_TIME
(1366518122, 1428171902)
```

```python
>>> def stupid_normalize(string):
...     return re.sub(r"[^a-zA-Z]+", ' ', string).lower().strip()
...
>>> def stupid_tokenize(string):
...     return stupid_normalize(string).split()
...
>>> STOPLIST = set(stupid_normalize(s.decode('latin1')) for s in open('../data/stoplist.english.txt', 'rb'))
>>> STOPLIST.add('is')
...
>>> list(STOPLIST)[:10]
[u'lest',
 u'all',
 u'o',
 u'yea',
 u'over',
 u'half',
 u'via',
 u'through',
 u'yourselves',
 u'go']
```

```python
>>> def tfdf(documents):
...     df = Counter()
...     tf = Counter()
...
...     for document in documents:
...         words = set(document)
...         for word in document:
...             tf[word] += 1
...         for word in words:
...             df[word] += 1
...
...     return tf, df
...
>>> def tfidf(tf, df):
...     return tf / (1 + math.log(1 + df))
```

```python
>>> tf, df = tfdf(nltk.word_tokenize(row[0].lower())
...               for row in cur.execute('select text from messages'))
...
>>> result = []
>>> for word in tf:
...     x, y = tf[word], df[word]
...     result.append((word, x, y, tfidf(x, y)))
>>> result.sort(key=lambda t: -t[-1])
```

```python
>>> with open('../data/btce.all.txt', 'w') as f:
...     for w in result:
...         f.write(('\t'.join(unicode(x) for x in w) + '\n').encode('utf-8'))
```

```python
>>> lines = (line for line in ux.line_reader('/media/alex/Data/data/twitter_stream_ner_temp_event_5pc.gz'))
>>> tweets = (twitter.parse_tweet(line, True) for line in lines)
...
>>> tf, df = tfdf(tweet.words for tweet in tweets)
```

```python

```
