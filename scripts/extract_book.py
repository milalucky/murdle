#!/usr/bin/env python3
"""Extract only option labels, icon crops and short answer keys from the supplied PDF."""
import fitz,json,re,statistics,difflib,sys,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdf', type=Path)
parser.add_argument('--skip-icons', action='store_true')
args=parser.parse_args()
PDF=args.pdf
ROOT=Path(__file__).resolve().parents[1]
doc=fitz.open(PDF)

def lines(page):
 return [(fitz.Rect(l['bbox']),''.join(s['text'] for s in l['spans']).strip()) for b in page.get_text('dict', flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] for l in b.get('lines',[]) if ''.join(s['text'] for s in l['spans']).strip()]
def norm(s):
 s=s.lower().replace('’',"'").replace('—',' ').replace('-', ' ')
 return ' '.join(re.findall(r'[a-z0-9]+',s))
def clean(s):
 s=re.sub(r'\s+',' ',s).strip();s=s.replace('- ', '')
 return s.title().replace('Iii','III').replace(' Ii ',' II ').replace('Mx.','Mx.').replace("They'Re","They're")
def titlecase(s):return clean(re.sub(r'[^A-Z0-9 .,&!?\-\']+$','',s))
def upper(t):return sum(c.isupper() for c in t)>3 and t.upper()==t

def start(n):
 return 19+(n-1)*2 if n<=25 else 71+(n-26)*2 if n<=50 else 123+(n-51)*4 if n<=75 else 225+(n-76)*4

def labels(n):
 st=start(n);sz=3 if n<=50 else 4
 sl=lines(doc[st]); sus_y=next((r.y1 for r,t in sl if 'SUSPECTS' in t),140)
 lochead=next((r.y0 for r,t in sl if 'LOCATIONS' in t and r.y0>sus_y+100),430)
 bottom=lochead if sz==3 else doc[st].rect.height-30
 def isname(t):
  letters=[c for c in t if c.isalpha()]
  return len(letters)>=4 and sum(c.isupper() for c in letters)/len(letters)>.78
 candidates=[(r,t) for r,t in sl if r.x0<112 and r.x1<120 and r.y0>sus_y and r.y1<bottom and isname(t) and not re.search(r'HANDED|HAIR|EYES|SUSPECTS|LOCATIONS',t)]
 groups=[]
 for r,t in sorted(candidates,key=lambda a:a[0].y0):
  if not groups or r.y0-groups[-1][-1][0].y1>27:groups.append([])
  groups[-1].append((r,t))
 suspects=[clean(' '.join(t for r,t in g)) for g in groups]
 objs={}
 for cat,page in [('locations',doc[st] if sz==3 else doc[st+1]),('weapons',doc[st+1])]:
  ll=lines(page);res=[]
  if sz==4:
   ranges=([(50,92),(207,250)] if cat=='locations' else [(370,399),(515,544)])
   regions=[(0,190,y0,y1) for y0,y1 in ranges]
   regions=[(a,b,y0,y1) for y0,y1 in ranges for a,b in [(0,195),(195,385)]]
  else:
   ys=(lochead+43,lochead+90) if cat=='locations' else (48,86)
   regions=[(a,b,*ys) for a,b in [(0,130),(130,250),(250,385)]]
  for x0,x1,y0,y1 in regions:
   candidates=[(r,t) for r,t in ll if x0<=(r.x0+r.x1)/2<x1 and y0<=r.y0<y1 and isname(t)]
   out=[]
   for r,t in sorted(candidates,key=lambda a:a[0].y0):
    if re.search(r'WEIGHT|WE!GHT|MADE OF|INDOORS|OUTDOORS|OMITHOOLS|WINTOS',t):break
    if len(t)>90:continue
    out.append(t)
   res.append(clean(' '.join(out)))
  objs[cat]=res
 motives=[]
 if sz==4:
  ml=lines(doc[st+2]);end=next((r.y0 for r,t in ml if 'CLUES' in t),200)
  mh=next((r.y1 for r,t in ml if t=='MOTIVES'),20)
  split=(mh+end)/2
  for row in range(2):
   for col in range(2):
    sel=[(r,t) for r,t in ml if r.y0>mh+8 and r.y1<end-10 and isname(t) and (r.x0<190)==(col==0) and (r.y0<split)==(row==0)]
    text=' '.join(t for r,t in sorted(sel,key=lambda a:a[0].y0))
    text=re.sub(r'^.*?\b(TO|OUT OF|FOR|BECAUSE|ON BEHALF|AS|BY|IN|WHILE)\b',r'\1',text)
    motives.append(clean(text))
 return {'suspects':suspects,**objs,**({'motives':motives} if sz==4 else {})}


labels={n:labels(n) for n in range(1,101)}
# Corrections checked against the page images and repeated option names.
fix={
 3:{'suspects':{2:'Blackstone, Esq.'}},4:{'locations':{0:'The Locomotive'},'weapons':{2:'A Rolled-up Newspaper (with a Crowbar Inside)'}},5:{'locations':{0:'The Parking Lot'}},6:{'locations':{1:'The Dumpster'}},9:{'locations':{0:'The Fountain'}},10:{'locations':{0:'The Center Bar'}},11:{'suspects':{0:'General Coffee'},'locations':{0:'The Courtyard',2:'The Front Counter'}},17:{'suspects':{1:'Chairman Chalk'}},18:{'weapons':{2:'A Fountain Pen'}},21:{'suspects':{0:'Chairman Chalk'}},22:{'suspects':{2:'Blackstone, Esq.'},'locations':{1:"An Associate's Office"},'weapons':{2:'A Poisoned Inkwell'}},23:{'locations':{1:'The Parking Lot'}},25:{'locations':{1:'The Parking Lot'},'weapons':{0:'A Quarter-million-dollar Lawyer'}},26:{'suspects':{2:'General Coffee'}},28:{'locations':{1:'The Observatory'},'weapons':{1:'A Dowsing Rod'}},29:{'weapons':{2:'An Exclusive Pin'}},32:{'suspects':{0:'Vice President Mauve'},'weapons':{0:'A Brain in a Jar'}},33:{'weapons':{1:'A Skeleton Arm'}},34:{'locations':{0:'The Columbarium'},'weapons':{0:'A Skeleton Arm'}},41:{'weapons':{1:'A Dowsing Rod'}},42:{'suspects':{1:'Grandmaster Rose'},'locations':{0:'The Parking Lot',1:'The Bathroom',2:'The Courtyard'}},50:{'locations':{2:'The Generator'},'weapons':{1:'A Bottle of Oil'}},
52:{'weapons':{2:'A Quasi-perpetual Motion Machine'},'motives':{0:"To Prove They're Tough"}},53:{'motives':{3:'To Get Revenge'}},54:{'locations':{3:'The Cliffs'},'motives':{1:'To Steal a Treasure Map',2:'To Impress a Lady'}},55:{'locations':{3:'The Entrance Gate'},'weapons':{0:'A Poisonous Spider',1:'A Pair of Gardening Shears',2:'A Bow and Arrow',3:'A Climbing Axe'}},56:{'locations':{0:'The New Development',2:'The Chapel',3:'The Quaint Garden'},'motives':{0:'To Steal an Idea'}},57:{'motives':{1:'Because a Ghost Made Them'}},59:{'suspects':{1:'Chairman Chalk'},'weapons':{1:'Confusing Contracts'},'motives':{3:'To Improve Book Sales'}},61:{'locations':{1:'The Wrecked Cruise Ship'},'weapons':{0:'An Axe'},'motives':{0:'To Close a Business Deal'}},63:{'locations':{2:'The Chapel'},'weapons':{3:'A Bottle of Sacred Oil'}},65:{'locations':{1:'The Roof'}},67:{'locations':{0:'Avalon'},'weapons':{1:'An Antique Helmet'}},68:{'suspects':{3:'General Coffee'},'motives':{0:'To Get Revenge'}},69:{'motives':{3:'Because a Ghost Made Them'}},70:{'suspects':{1:'Blackstone, Esq.'}},71:{'motives':{0:"While Trippin' Out"}},72:{'suspects':{2:'Blackstone, Esq.',3:'Dr. Seashell, DDS'},'motives':{0:'For Money'}},74:{'suspects':{3:'Dr. Seashell, DDS'}},75:{'motives':{1:'To Promote the Occult'}},79:{'suspects':{0:'Pearl, AGE'},'motives':{0:'To See If They Could',1:'To Get Their Movie Made'},'weapons':{2:'A Stale Candy Bar'}},80:{'weapons':{0:"A Stranglin' Scarf"}},81:{'motives':{1:'To Get Good Footage',3:'To Steal a Part'}},82:{'suspects':{1:'Pearl, AGE'},'motives':{0:'Because They Could',1:"To Destroy a Rival's Career"}},83:{'locations':{0:'Parking Lot A'},'suspects':{3:'Pearl, AGE'}},86:{'weapons':{2:'A Booby-trapped Fedora'}},88:{'weapons':{2:'A Crystal Dagger'},'motives':{1:'To Promote the Occult'}},89:{'suspects':{3:'Pearl, AGE'},'locations':{3:'The Water Tower Bar & Grill'},'motives':{0:'To Save Face',1:'For Political Purposes'}},90:{'locations':{2:'The Lobby'}},91:{'suspects':{3:'Blackstone, Esq.'}},94:{'motives':{3:'To Take Over Hollywood'}},98:{'suspects':{0:'Pearl, AGE',1:'Officer Copper'},'motives':{1:'To Take Over a Studio'}},99:{'suspects':{2:'President Amaranth',3:'Chairman Chalk'}},100:{'suspects':{3:'Inspector Irratino'},'weapons':{2:'A Selenite Wand'},'motives':{2:'To Get Revenge'}}}
labels[20]['suspects']=['Cosmonaut Bluski','Dr. Crimson','General Coffee']
labels[44]['suspects']=['Earl Grey','Sister Lapis','Judge Pine']
labels[54]['suspects']=['Vice President Mauve','Admiral Navy','Agent Ink','Grandmaster Rose']
labels[69]['suspects']=['Mister Shadow','High Alchemist Raven','The Amazing Aureolin','Superfan Smoky']
labels[73]['suspects']=['Coach Raspberry','General Coffee','Chef Aubergine','Earl Grey']
labels[75]['suspects']=['Mister Shadow','Mayor Honey','Blackstone, Esq.','Dr. Seashell, DDS']
for n,cats in fix.items():
 for cat,items in cats.items():
  for i,value in items.items():labels[n][cat][i]=value
for cats in labels.values():
 for cat,arr in cats.items():
  cats[cat]=[re.sub(r'\s+(?:Qutdoors|Gutdoors|Qutdcors|Tnatidc|Iinao)$','',v).replace('’',"'").replace("'S","'s").replace("'Re","'re") for v in arr]
# The key indices were individually reviewed against all 100 printed solutions.
SOLUTION_KEYS = {
 1: {'suspects': 0, 'locations': 0, 'weapons': 2},
 2: {'suspects': 1, 'locations': 2, 'weapons': 2},
 3: {'suspects': 0, 'locations': 1, 'weapons': 0},
 4: {'suspects': 1, 'locations': 1, 'weapons': 0},
 5: {'suspects': 0, 'locations': 0, 'weapons': 0},
 6: {'suspects': 0, 'locations': 1, 'weapons': 0},
 7: {'suspects': 2, 'locations': 0, 'weapons': 2},
 8: {'suspects': 1, 'locations': 0, 'weapons': 1},
 9: {'suspects': 2, 'locations': 1, 'weapons': 2},
 10: {'suspects': 2, 'locations': 0, 'weapons': 2},
 11: {'suspects': 1, 'locations': 0, 'weapons': 1},
 12: {'suspects': 1, 'locations': 0, 'weapons': 1},
 13: {'suspects': 1, 'locations': 2, 'weapons': 2},
 14: {'suspects': 2, 'locations': 2, 'weapons': 2},
 15: {'suspects': 0, 'locations': 1, 'weapons': 0},
 16: {'suspects': 1, 'locations': 1, 'weapons': 1},
 17: {'suspects': 0, 'locations': 0, 'weapons': 2},
 18: {'suspects': 0, 'locations': 2, 'weapons': 1},
 19: {'suspects': 1, 'locations': 2, 'weapons': 1},
 20: {'suspects': 0, 'locations': 2, 'weapons': 0},
 21: {'suspects': 2, 'locations': 0, 'weapons': 1},
 22: {'suspects': 2, 'locations': 2, 'weapons': 0},
 23: {'suspects': 0, 'locations': 2, 'weapons': 1},
 24: {'suspects': 0, 'locations': 1, 'weapons': 2},
 25: {'suspects': 1, 'locations': 1, 'weapons': 1},
 26: {'suspects': 2, 'locations': 0, 'weapons': 2},
 27: {'suspects': 0, 'locations': 1, 'weapons': 1},
 28: {'suspects': 2, 'locations': 2, 'weapons': 2},
 29: {'suspects': 1, 'locations': 2, 'weapons': 1},
 30: {'suspects': 1, 'locations': 0, 'weapons': 2},
 31: {'suspects': 0, 'locations': 2, 'weapons': 2},
 32: {'suspects': 0, 'locations': 0, 'weapons': 1},
 33: {'suspects': 1, 'locations': 0, 'weapons': 1},
 34: {'suspects': 1, 'locations': 1, 'weapons': 1},
 35: {'suspects': 2, 'locations': 2, 'weapons': 1},
 36: {'suspects': 2, 'locations': 1, 'weapons': 2},
 37: {'suspects': 1, 'locations': 1, 'weapons': 0},
 38: {'suspects': 2, 'locations': 2, 'weapons': 1},
 39: {'suspects': 2, 'locations': 2, 'weapons': 0},
 40: {'suspects': 1, 'locations': 0, 'weapons': 1},
 41: {'suspects': 1, 'locations': 1, 'weapons': 1},
 42: {'suspects': 2, 'locations': 2, 'weapons': 2},
 43: {'suspects': 1, 'locations': 1, 'weapons': 0},
 44: {'suspects': 2, 'locations': 2, 'weapons': 2},
 45: {'suspects': 0, 'locations': 1, 'weapons': 1},
 46: {'suspects': 2, 'locations': 0, 'weapons': 0},
 47: {'suspects': 1, 'locations': 0, 'weapons': 0},
 48: {'suspects': 2, 'locations': 0, 'weapons': 2},
 49: {'suspects': 1, 'locations': 1, 'weapons': 0},
 50: {'suspects': 1, 'locations': 0, 'weapons': 0},
 51: {'suspects': 1, 'locations': 2, 'weapons': 0, 'motives': 0},
 52: {'suspects': 3, 'locations': 3, 'weapons': 1, 'motives': 1},
 53: {'suspects': 3, 'locations': 1, 'weapons': 1, 'motives': 2},
 54: {'suspects': 1, 'locations': 3, 'weapons': 1, 'motives': 2},
 55: {'suspects': 0, 'locations': 0, 'weapons': 0, 'motives': 1},
 56: {'suspects': 1, 'locations': 2, 'weapons': 2, 'motives': 3},
 57: {'suspects': 3, 'locations': 0, 'weapons': 3, 'motives': 3},
 58: {'suspects': 3, 'locations': 3, 'weapons': 3, 'motives': 0},
 59: {'suspects': 1, 'locations': 3, 'weapons': 0, 'motives': 3},
 60: {'suspects': 1, 'locations': 2, 'weapons': 3, 'motives': 0},
 61: {'suspects': 1, 'locations': 2, 'weapons': 1, 'motives': 2},
 62: {'suspects': 2, 'locations': 3, 'weapons': 2, 'motives': 1},
 63: {'suspects': 1, 'locations': 0, 'weapons': 3, 'motives': 0},
 64: {'suspects': 2, 'locations': 0, 'weapons': 3, 'motives': 2},
 65: {'suspects': 0, 'locations': 0, 'weapons': 1, 'motives': 2},
 66: {'suspects': 0, 'locations': 3, 'weapons': 3, 'motives': 1},
 67: {'suspects': 2, 'locations': 2, 'weapons': 2, 'motives': 3},
 68: {'suspects': 1, 'locations': 3, 'weapons': 0, 'motives': 3},
 69: {'suspects': 1, 'locations': 3, 'weapons': 1, 'motives': 3},
 70: {'suspects': 2, 'locations': 2, 'weapons': 1, 'motives': 3},
 71: {'suspects': 2, 'locations': 3, 'weapons': 1, 'motives': 2},
 72: {'suspects': 2, 'locations': 3, 'weapons': 2, 'motives': 0},
 73: {'suspects': 2, 'locations': 0, 'weapons': 2, 'motives': 0},
 74: {'suspects': 3, 'locations': 3, 'weapons': 2, 'motives': 0},
 75: {'suspects': 0, 'locations': 3, 'weapons': 1, 'motives': 1},
 76: {'suspects': 1, 'locations': 3, 'weapons': 3, 'motives': 2},
 77: {'suspects': 2, 'locations': 2, 'weapons': 1, 'motives': 2},
 78: {'suspects': 0, 'locations': 2, 'weapons': 1, 'motives': 3},
 79: {'suspects': 3, 'locations': 0, 'weapons': 1, 'motives': 3},
 80: {'suspects': 0, 'locations': 3, 'weapons': 0, 'motives': 3},
 81: {'suspects': 0, 'locations': 0, 'weapons': 1, 'motives': 3},
 82: {'suspects': 3, 'locations': 1, 'weapons': 1, 'motives': 2},
 83: {'suspects': 1, 'locations': 0, 'weapons': 2, 'motives': 1},
 84: {'suspects': 0, 'locations': 2, 'weapons': 0, 'motives': 1},
 85: {'suspects': 2, 'locations': 3, 'weapons': 1, 'motives': 3},
 86: {'suspects': 3, 'locations': 3, 'weapons': 2, 'motives': 1},
 87: {'suspects': 0, 'locations': 0, 'weapons': 3, 'motives': 3},
 88: {'suspects': 1, 'locations': 2, 'weapons': 1, 'motives': 3},
 89: {'suspects': 1, 'locations': 1, 'weapons': 2, 'motives': 3},
 90: {'suspects': 2, 'locations': 1, 'weapons': 0, 'motives': 1},
 91: {'suspects': 0, 'locations': 0, 'weapons': 3, 'motives': 3},
 92: {'suspects': 3, 'locations': 0, 'weapons': 2, 'motives': 0},
 93: {'suspects': 0, 'locations': 3, 'weapons': 1, 'motives': 3},
 94: {'suspects': 2, 'locations': 3, 'weapons': 3, 'motives': 1},
 95: {'suspects': 0, 'locations': 3, 'weapons': 3, 'motives': 2},
 96: {'suspects': 1, 'locations': 2, 'weapons': 0, 'motives': 2},
 97: {'suspects': 2, 'locations': 2, 'weapons': 2, 'motives': 2},
 98: {'suspects': 0, 'locations': 2, 'weapons': 1, 'motives': 2},
 99: {'suspects': 0, 'locations': 2, 'weapons': 3, 'motives': 0},
 100: {'suspects': 0, 'locations': 0, 'weapons': 0, 'motives': 1},
}
ASSIGNMENTS = json.loads((ROOT/'scripts/assignments-reviewed.json').read_text())
cases=[]
for n,cats in labels.items():
 size=3 if n<=50 else 4
 assert all(len(v)==size and all(v) for v in cats.values()),(n,cats)
 title=doc[start(n)].get_text().splitlines()[0]
 title=re.sub(r'^\d+[.,]\s*','',title).strip();title=re.sub(r'\s*[AQ29&.]+$','',title).strip()
 if n==41:title="THE PSYCHIC WHO DIDN'T FORESEE HIS DEATH"
 if n==59:title='I YACHT TO KILL YOU FOR THIS'
 if n==66:title='VIVE LA REVOLUTION!'
 if n==78:title='PLENTY OF KILLS IN THE SEA'
 case={'id':n,'title':title.title().replace("'T", "'t").replace("’T", "’t"),'size':size,'categories':[], 'solution':SOLUTION_KEYS[n],'sourcePages':list(range(start(n)+1,start(n)+1+(2 if size==3 else 4))), 'verification':'verified'}
 for cat in ['suspects','weapons','locations','motives']:
  if cat not in cats:continue
  case['categories'].append({'id':cat,'label':{'suspects':'Suspects','weapons':'Weapons','locations':'Locations','motives':'Motives'}[cat],'items':[{'label':value.replace('Ufo','UFO').replace('Dvd','DVD').replace('Adr','ADR'),'icon':f'assets/icons/{n:03}-{cat}-{i}.png'} for i,value in enumerate(cats[cat])]})
 case['assignments']=ASSIGNMENTS[str(n)]
 case['assignmentsVerification']='reviewed'
 for cat in case['categories']:
  assert sorted(a[cat['id']] for a in case['assignments'])==list(range(size))
 assert any(all(a[k]==v for k,v in case['solution'].items()) for a in case['assignments'])
 cases.append(case)
(ROOT/'data').mkdir(parents=True,exist_ok=True)
(ROOT/'data/volume1.json').write_text(json.dumps({'bookId':'volume1','title':'Murdle Volume 1','cases':cases},ensure_ascii=False,indent=2))

if not args.skip_icons:
 (ROOT/'assets/icons').mkdir(parents=True,exist_ok=True)
 geo=[]
 for n in range(1,101):
  size=3 if n<=50 else 4
  page=doc[start(n)+(1 if size==3 else 3)]
  ls=[]
  for b in page.get_text('dict', flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']:
   for l in b.get('lines',[]):
    t=''.join(s['text'] for s in l['spans']).strip();r=fitz.Rect(l['bbox'])
    if r.height<18:ls.append((r,t))
  sub=[(r,t) for r,t in ls if t=='SUSPECTS' and r.x0>60]
  loc=[(r,t) for r,t in ls if t=='LOCATIONS' and r.x0>100]
  if sub:
   r=sub[0][0];cx=(r.x0+r.x1)/2;hy=r.y1
  elif loc:
   r=loc[0][0];cx=(r.x0+r.x1)/2-(86 if size==3 else 208);hy=r.y1
  else:
   # First page has unrecognized header. Geometry relative to answer baseline.
   r=next((r for r,t in ls if t=='WHAT?'),None);cx=114;hy=r.y0-98 if r else (410 if size==3 else 81)
  cell=28.7 if size==3 else 26
  x0=cx-cell*size/2;y0=hy+37
  # refine grid-top by maximum darkness in narrow window below icon row.
  pix=page.get_pixmap(colorspace=fitz.csGRAY)
  data=pix.samples;w=pix.width
  left=int(x0);right=int(x0+cell*size*(2 if size==3 else 3))
  rows=[]
  for y in range(int(hy+29),int(hy+43)):
   score=sum(data[y*w+x]<85 for x in range(left,right))
   rows.append((score,y))
  top=max(rows)[1];y0=top
  # Refine left edge using tall vertical line score. Slant may move 1-3 px.
  cols=[]
  for x in range(int(x0)-6,int(x0)+7):
   score=sum(data[y*w+x]<85 for y in range(top+3,min(top+int(cell*size*2)-3,pix.height)))
   cols.append((score,x))
  x0=max(cols)[1]
  geo.append({'case':n,'x':x0,'y':y0,'cell':cell,'header':hy})
  crops={}
  for cat,offset in [('suspects',0),('locations',size if size==3 else 2*size)]+([('motives',size)] if size==4 else []):
   crops[cat]=[(x0+(offset+i+.5)*cell,y0-18) for i in range(size)]
  crops['weapons']=[(x0-18,y0+(i+.5)*cell) for i in range(size)]
  for cat,centers in crops.items():
   for i,(x,y) in enumerate(centers):
    half=12.7 if size==3 else 12.1
    rect=fitz.Rect(x-half,y-half,x+half,y+half)
    tile=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=rect,colorspace=fitz.csGRAY)
    s=tile.samples;bg=sorted(s)[int(len(s)*.7)];th=bg-30
    rgba=bytearray()
    for v in s:rgba.extend([24,36,29,max(0,min(255,int((th-v)*4)))])
    out=fitz.Pixmap(fitz.csRGB,tile.width,tile.height,rgba,True)
    out.save(str(ROOT/f'assets/icons/{n:03}-{cat}-{i}.png'))
  print(f"Extracted icons: {n}/100", flush=True)

assert len(cases)==100
for case in cases:
 for cat in case['categories']:
  assert 0<=case['solution'][cat['id']]<case['size']
  for item in cat['items']:assert (ROOT/item['icon']).exists(),item['icon']
print('Validated 100 cases, 1250 icon paths and 100 complete answer keys.')
