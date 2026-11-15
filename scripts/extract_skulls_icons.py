#!/usr/bin/env python3
"""Extract printed glyph contours as SVG UI assets from normalized Seven Skulls scans.
Input: normalized page PNGs + Apple Vision OCR coordinates + reviewed case layouts.
No complete book pages are copied into the website.
"""
import argparse,json,math
from pathlib import Path
import cv2
import numpy as np
P=argparse.ArgumentParser();P.add_argument('--layout',default='/private/tmp/skulls-layout.json');P.add_argument('--pages',default='/private/tmp/skulls-pages');P.add_argument('--ocr',default='/private/tmp/skulls-ocr');P.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'assets/skulls'));P.add_argument('--audit',default='/private/tmp/skulls-icon-audit');args=P.parse_args()
OUT=Path(args.out);OUT.mkdir(parents=True,exist_ok=True);AUDIT=Path(args.audit);AUDIT.mkdir(parents=True,exist_ok=True)

def vectorize(tile,path):
 gray=cv2.cvtColor(tile,cv2.COLOR_BGR2GRAY)
 gray=cv2.GaussianBlur(gray,(3,3),.55)
 _,mask=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
 count,labels,stats,centroids=cv2.connectedComponentsWithStats(mask,8)
 if count<2:raise ValueError('Empty icon')
 largest=max(stats[1:,cv2.CC_STAT_AREA]);keep=np.zeros_like(mask)
 for k in range(1,count):
  x,y,w,h,area=stats[k]
  if area>=max(2,largest*.008) and not (w>mask.shape[1]*.9 and h<mask.shape[0]*.12):keep[labels==k]=255
 ys,xs=np.where(keep>0)
 if len(xs)<5:raise ValueError('No glyph contours')
 x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
 small=keep[y0:y1,x0:x1]
 scale=112/max(small.shape);resized=cv2.resize(small,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
 resized=cv2.GaussianBlur(resized,(3,3),.65);_,resized=cv2.threshold(resized,127,255,cv2.THRESH_BINARY)
 canvas=np.zeros((128,128),np.uint8);oy=(128-resized.shape[0])//2;ox=(128-resized.shape[1])//2;canvas[oy:oy+resized.shape[0],ox:ox+resized.shape[1]]=resized
 contours,_=cv2.findContours(canvas,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 paths=[]
 for contour in contours:
  if cv2.contourArea(contour)<1.5:continue
  points=cv2.approxPolyDP(contour,.45,True).reshape(-1,2)
  if len(points)<3:continue
  paths.append('M'+' L'.join(f'{x},{y}' for x,y in points)+'Z')
 path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><path fill="#18241d" fill-rule="evenodd" d="'+' '.join(paths)+'"/></svg>')
 return canvas,float(np.mean(canvas>0))

def get_geometry(img,ocr,n,cats):
 h,w=img.shape[:2]
 headers=[r for r in ocr if r['text'].strip().upper()=='SUSPECTS' and r['box'][2]>r['box'][3]*2]
 if not headers:raise ValueError('No SUSPECTS header')
 # Printed grid header is the last horizontal SUSPECTS label on a spread.
 head=max(headers,key=lambda r:r['box'][1]);x,y,bw,bh=head['box'];cx=x+bw/2
 peers=[r for r in ocr if r['text'].strip().upper() in ['LOCATIONS','MOTIVES'] and r['box'][0]>cx and abs(r['box'][1]-y)<max(100,bh*4) and r['box'][2]>r['box'][3]*2]
 peers.sort(key=lambda r:r['box'][0]);
 if not peers:raise ValueError('No peer column header')
 gap=2 if len(cats)==4 and peers[0]['text'].strip().upper()=='LOCATIONS' else 1
 dx=(peers[0]['box'][0]+peers[0]['box'][2]/2-cx)/(n*gap)
 xguess=cx-n*dx/2;yguess=y+bh+dx*1.2
 blocks=len(cats)-1;total=n*blocks
 gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY);edges=cv2.Canny(gray,65,150)
 roi=np.zeros_like(edges);xa=max(0,int(xguess-dx*.5));xb=min(w,int(xguess+dx*(total+2)));ya=max(0,int(y+bh+dx*.55));yb=min(h,int(yguess+dx*(total+1)))
 roi[ya:yb,xa:xb]=edges[ya:yb,xa:xb]
 raw=cv2.HoughLinesP(roi,1,np.pi/1800,threshold=max(25,int(dx)),minLineLength=dx*n*.75,maxLineGap=dx*.3)
 lines=[] if raw is None else raw.reshape(-1,4)
 horizontal=[];vertical=[]
 for a,b,c,d in lines:
  if abs(c-a)>abs(d-b)*4:
   slope=(d-b)/(c-a);yy=b+slope*(xguess-a);horizontal.append((a,b,c,d,slope,yy,abs(c-a)))
  elif abs(d-b)>abs(c-a)*4:
   slope=(c-a)/(d-b);xx=a+slope*(yguess-b);vertical.append((a,b,c,d,slope,xx,abs(d-b)))
 tops=[l for l in horizontal if abs(l[5]-yguess)<dx*.75]
 if not tops:raise ValueError('No top grid line')
 top=max(tops,key=lambda l:l[6]-abs(l[5]-yguess)*.5);hs=top[4]
 lefts=[l for l in vertical if abs(l[5]-xguess)<dx*.55]
 if not lefts:raise ValueError('No left grid line')
 left=max(lefts,key=lambda l:l[6]-abs(l[5]-xguess));vs=left[4]
 # Intersection of fitted top and left edges.
 topC=top[1]-hs*top[0];leftC=left[0]-vs*left[1];x0=(leftC+vs*topC)/(1-vs*hs);y0=hs*x0+topC
 # Detect the full-width right endpoint of the top border to refine width.
 if top[6]>dx*total*.80:
  right=max(top[0],top[2]);newdx=(right-x0)/total
  if .82*dx<newdx<1.18*dx:dx=newdx
 # Repeated horizontal lines at first block's center reveal actual cell height.
 ys=[]
 for l in horizontal:
  mid=x0+n*dx*.5
  if min(l[0],l[2])<=mid<=max(l[0],l[2]):
   yy=l[1]+l[4]*(mid-l[0])-hs*(mid-x0)
   if y0-dx*.15<yy<y0+dx*(total+1):ys.append(yy)
 ys.sort();clusters=[]
 for yy in ys:
  if clusters and abs(yy-np.mean(clusters[-1]))<dx*.15:clusters[-1].append(yy)
  else:clusters.append([yy])
 ypos=[float(np.mean(q)) for q in clusters]
 # Estimate row spacing from adjacent detected lines (not missing far-away borders).
 gaps=[b-a for a,b in zip(ypos,ypos[1:]) if .65*dx<b-a<1.4*dx]
 dy=float(np.median(gaps)) if gaps else dx
 xs=[]
 midy=y0+dy*.5
 for l in vertical:
  if min(l[1],l[3])<=midy<=max(l[1],l[3]):
   xx=l[0]+l[4]*(midy-l[1])-vs*(midy-y0)
   if x0-dx*.2<xx<x0+dx*(total+.5):xs.append(xx)
 xs.sort();xc=[]
 for xx in xs:
  if xc and abs(xx-np.mean(xc[-1]))<dx*.15:xc[-1].append(xx)
  else:xc.append([xx])
 xp=[float(np.mean(q)) for q in xc]
 gaps=[b-a for a,b in zip(xp,xp[1:]) if .65*dx<b-a<1.4*dx]
 if len(xp)>=total+1:
  dx=(xp[total]-xp[0])/total; x0=xp[0]
 return dict(xp=xp,yp=ypos,x=x0,y=y0,dx=dx,dy=dy,hs=hs,vs=vs,n=n,cats=cats)

def extract(row):
 number=row['gridPage'];img=cv2.imread(str(Path(args.pages)/f'{number:03}.png'));ocr=json.loads((Path(args.ocr)/f'{number:03}.json').read_text())
 n=row['size'];cats=row['categories'];cats=[c['id'] if isinstance(c,dict) else c for c in cats]
 geo=get_geometry(img,ocr,n,cats);cid=row['id'];
 if cid==4:geo.update(y=1163,hs=-.01587)
 x,y,dx,dy,hs,vs=[geo[k] for k in ['x','y','dx','dy','hs','vs']]
 columns=['suspects']+(['motives'] if 'motives' in cats else [])+['locations']
 crops=[];audit=img.copy()
 for cat in cats:
  for i in range(n):
   if cat=='weapons':u=-.65;v=i+.5
   else:u=columns.index(cat)*n+i+.5;v=-.65
   cx=x+u*dx+v*dy*vs;cy=y+v*dy+u*dx*hs
   if cat!='weapons' and len(geo['xp'])>=len(columns)*n+1:
    j=columns.index(cat)*n+i;cx=(geo['xp'][j]+geo['xp'][j+1])/2+v*dy*vs
   # Recenter on the actual printed glyph; photographed pages curve between grid lines.
   radius=int(max(dx,dy)*.85);xa=max(0,int(cx-radius));ya=max(0,int(cy-radius));xb=min(img.shape[1],int(cx+radius));yb=min(img.shape[0],int(cy+radius))
   region=img[ya:yb,xa:xb];gray=cv2.cvtColor(region,cv2.COLOR_BGR2GRAY)
   _,binary=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
   count,labels,stats,centroids=cv2.connectedComponentsWithStats(binary,8)
   candidates=[]
   for k in range(1,count):
    xx,yy,ww,hh,area=stats[k];ccx,ccy=centroids[k]+[xa,ya]
    if area>max(5,dx*dy*.015) and ww<dx*1.05 and hh<dy*1.1 and abs(ccx-cx)<dx*.55 and abs(ccy-cy)<dy*.55:
     candidates.append(((ccx-cx)**2+(ccy-cy)**2,k))
   if not candidates and cid==49 and cat=='motives' and i==0:
    half=min(dx,dy)*.45;tile=img[int(cy-half):int(cy+half),int(cx-half):int(cx+half)]
    path=OUT/f'{cid:03}-{cat}-{i}.svg';mask,density=vectorize(tile,path);cv2.imwrite(str(AUDIT/f'{cid:03}-{cat}-{i}.png'),255-mask);continue
   if not candidates:raise ValueError(f'No glyph candidate: {cat} {i}')
   k=min(candidates)[1];xx,yy,ww,hh,area=stats[k];group={k};bounds=[xx,yy,xx+ww,yy+hh]
   for _ in range(3):
    for j in range(1,count):
     if j in group:continue
     ax,ay,aw,ah,aa=stats[j]
     if aa<max(2,area*.007):continue
     bx0,by0,bx1,by1=bounds
     gapx=max(0,bx0-(ax+aw),ax-bx1);gapy=max(0,by0-(ay+ah),ay-by1)
     proposed=[min(bx0,ax),min(by0,ay),max(bx1,ax+aw),max(by1,ay+ah)]
     if gapx<dx*.14 and gapy<dy*.14 and proposed[2]-proposed[0]<dx*.98 and proposed[3]-proposed[1]<dy*1.02:
      group.add(j);bounds=proposed
   mask=np.isin(labels,list(group)).astype('uint8')*255
   xx,yy,xx1,yy1=map(int,bounds);tile=cv2.cvtColor(255-mask[max(0,yy-2):yy1+2,max(0,xx-2):xx1+2],cv2.COLOR_GRAY2BGR)
   cx=xa+(xx+xx1)/2;cy=ya+(yy+yy1)/2;half=max(xx1-xx,yy1-yy)/2
   corners=np.float32([[xa+xx,ya+yy],[xa+xx1,ya+yy],[xa+xx1,ya+yy1],[xa+xx,ya+yy1]])
   if cid==43 and cat=='weapons' and i==1:tile=img[555:638,90:165]
   path=OUT/f'{cid:03}-{cat}-{i}.svg';mask,density=vectorize(tile,path)
   cv2.imwrite(str(AUDIT/f'{cid:03}-{cat}-{i}-raw.png'),tile);cv2.imwrite(str(AUDIT/f'{cid:03}-{cat}-{i}.png'),255-mask)
   crops.append(dict(cat=cat,index=i,box=[cx-half,cy-half,half*2,half*2],density=density))
   cv2.polylines(audit,[corners.astype(int)],True,(0,0,255),2)
 cv2.imwrite(str(AUDIT/f'page-{cid:03}.jpg'),cv2.resize(audit,None,fx=min(1,1400/img.shape[1]),fy=min(1,1400/img.shape[1])))
 return dict(id=cid,gridPage=number,geometry=geo,crops=crops)

if __name__=='__main__':
 layout=json.loads(Path(args.layout).read_text());layout=layout.get('cases',layout) if isinstance(layout,dict) else layout;results=[];errors=[]
 for row in layout:
  try:results.append(extract(row));print('icons',row['id'],flush=True)
  except Exception as e:errors.append({'id':row.get('id'),'error':str(e)});print('ERROR',row.get('id'),e,flush=True)
 (AUDIT/'geometry.json').write_text(json.dumps(results,indent=2));(AUDIT/'errors.json').write_text(json.dumps(errors,indent=2))
 print('done',len(results),'errors',errors)
