#!/usr/bin/env python3
"""Build the compact Seven Skulls catalog from reviewed labels and solution matrices.
Only UI labels, glyph references and answer indices are published, never page scans.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 rows=json.loads((ROOT/'scripts/skulls-reviewed.json').read_text())
 result=[]
 for row in rows:
  c={k:v for k,v in row.items() if k!='labels'}
  c['categories']=[{'id':cat,'label':row.get('categoryLabels',{}).get(cat,{'suspects':'Suspects','weapons':'Weapons','locations':'Locations','motives':'Motives'}[cat]),'question':row.get('questions',{}).get(cat,{'suspects':'Who?','weapons':'What?','locations':'Where?','motives':'Why?'}[cat]),'items':[{'label':label,'icon':f'assets/skulls/{row["id"]:03}-{cat}-{i}.svg'} for i,label in enumerate(row['labels'][cat])]} for cat in row['categories']]
  for cat in c['categories']:
   assert len(cat['items'])==c['size']
   assert sorted(a[cat['id']] for a in c['assignments'])==list(range(c['size']))
  assert c['solution'] in c['assignments']
  result.append(c)
 (ROOT/'data/skulls.json').write_text(json.dumps({'bookId':'skulls','title':'Murdle: The Case of the Seven Skulls','cases':result},ensure_ascii=False,separators=(',',':'))+'\n')
if __name__=='__main__':build()
