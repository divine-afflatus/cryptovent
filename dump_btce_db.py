#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('btce-log.db')
cur = conn.cursor()

with open('btce-log.txt', 'w') as f:
    for row in cur.execute('select * from messages order by time'):
        f.write('\t'.join(map(str, row)) + '\n')
