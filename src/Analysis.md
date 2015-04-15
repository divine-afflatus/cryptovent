```python
>>> %matplotlib inline
>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> import sqlite3
>>> import re
>>> from collections import Counter
```

```python
>>> conn = sqlite3.connect('../data/text.btce.db')
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
>>> df = Counter()
>>> tf = Counter()
>>> for row in cur.execute('select text from messages'):
...     sentence = stupid_tokenize(row[0])
...     words = set(sentence)
...     for word in sentence:
...         tf[word] += 1
...     for word in words:
...         df[word] += 1
...
>>> for word in STOPLIST:
...     del tf[word]
...     del df[word]
...
>>> tfidf = []
>>> for word in tf:
...     tfidf.append((word, tf[word] / (1 + math.log(1 + df[word]))))
>>> tfidf.sort(key=lambda t: -t[1])
...
>>> top100 = list(map(lambda t:t[0], tfidf[:100]))
...
>>> top100[:10]
```

```python

```
