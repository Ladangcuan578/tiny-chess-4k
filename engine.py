import json,os,sys,urllib.request,urllib.error,random
ENV=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("no env")
# 0x88 board: a1=0,h8=119. White pieces 1..6 (P N B R Q K),black -1..-6.
KN=[33,31,18,14,-14,-18,-31,-33]
KI=[1,-1,16,-16,15,17,-15,-17]
BI=[15,17,-15,-17]
RO=[1,-1,16,-16]
V=[0,100,320,330,500,900,0]
# Piece-square tables,white perspective,rank 1 first (index=rank*8+file).
PST=[0,'kkkkkkkklmmggmmlljikkijlkkkookkkllmppmllmmoqqommuuuuuuuukkkkkkkk','aceeeecacgkllkgcelmnnmleeknoonkeelnoonleekmnnmkecgkkkkgcaceeeeca','giiiiiigilkkkkliimmmmmmiikmmmmkiillmmlliiklmmlkiikkkkkkigiiiiiig','kkkllkkkjkkkkkkjjkkkkkkjjkkkkkkjjkkkkkkjjkkkkkkjlmmmmmmlkkkkkkkk','giijjiigiklkkkkiilllllkikkllllkjjkllllkjikllllkiikkkkkkigiijjiig','oqmkkmqoookkkkooiggggggigeecceegeccaacceeccaacceeccaacceeccaacce']
M=100000
ND=150000
R=random.Random(1)
Z=[[R.getrandbits(64) for _ in range(128)] for _ in range(12)]
ZS=R.getrandbits(64)
ZC=[R.getrandbits(64) for _ in range(16)]
ZE=[R.getrandbits(64) for _ in range(8)]
b=[0]*128
wk=0
bk=0
NW=0
NB=0
tn=1
rg=0
ep=-1
hf=0
h=0
ev=0
st=[]
nd=0
sn=set()
TT={}
KILL=[[0,0] for _ in range(256)]
H=[[0]*128 for _ in range(12)]
def zi(p):
 return p - 1 if p > 0 else -p+5
def pst(p,s):
 if p<0:s^=0x70
 return (ord(PST[abs(p)][(s>>4)*8+(s&7)])-107)*5
def ct(p,s):
 v=V[abs(p)]+pst(p,s)
 return v if p > 0 else -v
def at(sq,by_white):
 if by_white:
  for t in (sq - 15,sq - 17):
   if not (t & 0x88) and b[t]==1:
    return True
 else:
  for t in (sq+15,sq+17):
   if not (t & 0x88) and b[t]==-1:
    return True
 wn=2 if by_white else -2
 for d in KN:
  t=sq+d
  if not (t & 0x88) and b[t]==wn:
   return True
 wk=6 if by_white else -6
 for d in KI:
  t=sq+d
  if not (t & 0x88) and b[t]==wk:
   return True
 wb=3 if by_white else -3
 wq=5 if by_white else -5
 for d in BI:
  t=sq+d
  while not (t & 0x88):
   c=b[t]
   if c:
    if c==wb or c==wq:
     return True
    break
   t += d
 wr=4 if by_white else -4
 for d in RO:
  t=sq+d
  while not (t & 0x88):
   c=b[t]
   if c:
    if c==wr or c==wq:
     return True
    break
   t += d
 return False
def ks(white):
 return wk if white else bk
def ic():
 return at(ks(tn > 0),tn < 0)
def gn(caps):
 ms=[]
 for s in range(128):
  if s & 0x88:
   continue
  p=b[s]
  if p==0 or (p > 0)!=(tn > 0):
   continue
  ap=abs(p)
  if ap==1:
   d=16 if p > 0 else -16
   t=s+d
   if not (t & 0x88) and b[t]==0:
    if (t>>4)==7 or (t>>4)==0:
     for q in (5,4,3,2):
      ms.append(s|(t<<7)|(q<<14))
    elif not caps:
     ms.append(s|(t<<7))
     if ((s>>4)==1 and p > 0) or ((s>>4)==6 and p < 0):
      t2=s+2*d
      if b[t2]==0:
       ms.append(s|(t2<<7))
   for dd in (d - 1,d+1):
    t=s+dd
    if t & 0x88:
     continue
    c=b[t]
    if c!=0 and (c > 0)!=(p > 0):
     if (t>>4)==7 or (t>>4)==0:
      for q in (5,4,3,2):
       ms.append(s|(t<<7)|(q<<14))
     else:
      ms.append(s|(t<<7))
    elif t==ep and ep>=0:
     ms.append(s|(t<<7))
  elif ap==2 or ap==6:
   for dd in (KN if ap==2 else KI):
    t=s+dd
    if t & 0x88:
     continue
    c=b[t]
    if c==0:
     if not caps:
      ms.append(s|(t<<7))
    elif (c > 0)!=(p > 0):
     ms.append(s|(t<<7))
  else:
   dirs=BI if ap==3 else RO if ap==4 else BI+RO
   for dd in dirs:
    t=s+dd
    while not (t & 0x88):
     c=b[t]
     if c==0:
      if not caps:
       ms.append(s|(t<<7))
     else:
      if (c > 0)!=(p > 0):
       ms.append(s|(t<<7))
      break
     t += dd
 if not caps:
  if tn>0:
   for bit,t,es,u in ((1,6,(5,6),(4,5,6)),(2,2,(3,2,1),(4,3,2))):
    if rg&bit and all(not b[e] for e in es) and all(not at(a,False) for a in u):
     ms.append(4|(t<<7))
  else:
   for bit,t,es,u in ((4,118,(117,118),(116,117,118)),(8,114,(115,114,113),(116,115,114))):
    if rg&bit and all(not b[e] for e in es) and all(not at(a,True) for a in u):
     ms.append(116|(t<<7))
 return ms
def mk(m):
 global tn,rg,ep,hf,h,ev,wk,bk,NW,NB
 f=m & 127
 t=(m>>7) & 127
 pr=(m>>14) & 7
 p=b[f]
 c=b[t]
 cap_sq=t
 rf=rt=-1
 if abs(p)==1 and c==0 and t==ep and ep>=0:
  cap_sq=t - 16 if p > 0 else t+16
  c=b[cap_sq]
 if abs(p)==6 and abs(t - f)==2:
  if t==6:
   rf,rt=7,5
  elif t==2:
   rf,rt=0,3
  elif t==118:
   rf,rt=119,117
  else:
   rf,rt=112,115
 st.append((m,c,cap_sq,rf,rt,rg,ep,hf,h,ev,NW,NB))
 old_rights=rg
 old_ep=ep
 h ^= Z[zi(p)][f] ^ ZS
 if old_rights:
  h ^= ZC[old_rights]
 if old_ep>=0:
  h ^= ZE[old_ep & 7]
 ev -= ct(p,f)
 if c:
  b[cap_sq]=0
  h ^= Z[zi(c)][cap_sq]
  ev -= ct(c,cap_sq)
  if abs(c) not in (1,6):
   if c > 0:
    NW -= V[abs(c)]
   else:
    NB -= V[abs(c)]
 b[f]=0
 np=(pr if p > 0 else -pr) if pr else p
 b[t]=np
 if pr:
  if p > 0:
   NW += V[pr]
  else:
   NB += V[pr]
 if abs(p)==6:
  if p > 0:
   wk=t
  else:
   bk=t
 h ^= Z[zi(np)][t]
 ev += ct(np,t)
 if rf>=0:
  r=b[rf]
  b[rf]=0
  b[rt]=r
  h ^= Z[zi(r)][rf] ^ Z[zi(r)][rt]
  ev -= ct(r,rf)
  ev += ct(r,rt)
 if abs(p)==6:
  rg &= ~3 if p > 0 else ~12
 elif abs(p)==4:
  if f==0:
   rg &= ~2
  elif f==7:
   rg &= ~1
  elif f==112:
   rg &= ~8
  elif f==119:
   rg &= ~4
 if c and abs(c)==4:
  if cap_sq==0:
   rg &= ~2
  elif cap_sq==7:
   rg &= ~1
  elif cap_sq==112:
   rg &= ~8
  elif cap_sq==119:
   rg &= ~4
 if rg:
  h ^= ZC[rg]
 if abs(p)==1 and abs(t - f)==32:
  ep=f+16 if p > 0 else f - 16
  h ^= ZE[ep & 7]
 else:
  ep=-1
 hf=0 if abs(p)==1 or c else hf+1
 tn=-tn
def um():
 global tn,rg,ep,hf,h,ev,wk,bk,NW,NB
 m,c,cap_sq,rf,rt,orights,oep,ohalf,oh,oev,onw,onb=st.pop()
 f=m & 127
 t=(m>>7) & 127
 pr=(m>>14) & 7
 p=b[t]
 if abs(p)==6:
  if p > 0:
   wk=f
  else:
   bk=f
 b[t]=0
 if c:
  b[cap_sq]=c
 if rf>=0:
  r=b[rt]
  b[rt]=0
  b[rf]=r
 b[f]=(1 if p > 0 else -1) if pr else p
 tn=-tn
 rg,ep,hf,h,ev,NW,NB=orights,oep,ohalf,oh,oev,onw,onb
def uci(m):
 f=m & 127
 t=(m>>7) & 127
 pr=(m>>14) & 7
 s="abcdefgh"[f & 7]+str((f>>4)+1)+"abcdefgh"[t & 7]+str((t>>4)+1)
 return s+("nbrq"[pr - 2] if pr else "")
def pu(u):
 f="abcdefgh".index(u[0])+16*(int(u[1]) - 1)
 t="abcdefgh".index(u[2])+16*(int(u[3]) - 1)
 pr=("nbrq".index(u[4])+2) if len(u)==5 else 0
 return f|(t<<7)|(pr<<14)
def pf(fen):
 global tn,rg,ep,hf,h,ev,wk,bk,NW,NB
 parts=fen.split()
 for i in range(128):
  b[i]=0
 del st[:]
 row=7
 col=0
 for ch in parts[0]:
  if ch=="/":
   row -= 1
   col=0
  elif ch.isdigit():
   col += int(ch)
  else:
   v="PNBRQKpnbrqk".index(ch)
   b[row*16+col]=v+1 if v<6 else 5-v
   if ch=="K":
    wk=row*16+col
   elif ch=="k":
    bk=row*16+col
   col += 1
 tn=1 if parts[1]=="w" else -1
 rg=0
 if len(parts) > 2:
  if "K" in parts[2]:
   rg |= 1
  if "Q" in parts[2]:
   rg |= 2
  if "k" in parts[2]:
   rg |= 4
  if "q" in parts[2]:
   rg |= 8
 ep=-1
 if len(parts) > 3 and parts[3]!="-":
  ep="abcdefgh".index(parts[3][0])+16*(int(parts[3][1]) - 1)
 hf=int(parts[4]) if len(parts) > 4 else 0
 h=0
 ev=0
 NW=0
 NB=0
 for s in range(128):
  if s & 0x88:
   continue
  p=b[s]
  if p:
   h ^= Z[zi(p)][s]
   ev += ct(p,s)
   if abs(p) not in (1,6):
    if p > 0:
     NW += V[abs(p)]
    else:
     NB += V[abs(p)]
 if tn < 0:
  h ^= ZS
 if rg:
  h ^= ZC[rg]
 if ep>=0:
  h ^= ZE[ep & 7]
class Timeout(Exception):
 pass
def od(ms,tt_move,ply):
 def sc(m):
  if m==tt_move:
   return 1<<28
  f=m & 127
  t=(m>>7) & 127
  c=b[t]
  if not c and abs(b[f])==1 and (f & 7)!=(t & 7):
   c=-1 if b[f] > 0 else 1
  if c:
   return (1<<24)|V[abs(c)]*16 - V[abs(b[f])]
  if m==KILL[ply][0]:
   return 1<<22
  if m==KILL[ply][1]:
   return 1<<21
  return H[zi(b[f])][t]
 ms.sort(key=sc,reverse=True)
 return ms
def sr(depth,alpha,beta,ply):
 global nd,tn,ep,hf,h
 nd += 1
 if nd > ND:
  raise Timeout()
 if hf>=100:
  return 0
 if h in sn:
  return 0
 chk=ic()
 if depth<=0:
  return qc(alpha,beta,ply,chk)
 sn.add(h)
 try:
  e=TT.get(h)
  tt_move=0
  if e and e[0]>=depth:
   _,flag,val,mv=e
   if flag==0:
    return val
   if flag==1 and val>=beta:
    return val
   if flag==2 and val<=alpha:
    return val
   tt_move=mv
  elif e:
   tt_move=e[3]
  if depth>=3 and not chk and (NW if tn > 0 else NB) > 0 and beta < M - 1000:
   oep,ohalf,oh=ep,hf,h
   if ep>=0:
    h ^= ZE[ep & 7]
   ep=-1
   hf += 1
   h ^= ZS
   tn=-tn
   s=-sr(depth - 3,-beta,-beta+1,ply+1)
   tn=-tn
   ep,hf,h=oep,ohalf,oh
   if s>=beta:
    return beta
  ms=od(gn(False),tt_move,ply)
  best=-M
  best_m=0
  a=alpha
  nlegal=0
  for m in ms:
   q=not b[(m>>7)&127]
   mk(m)
   if at(ks(tn < 0),tn > 0):
    um()
    continue
   nlegal += 1
   if depth>2 and nlegal>3 and q and not chk:
    s=-sr(depth-2,-beta,-a,ply+1)
    if s>a:
     s=-sr(depth-1,-beta,-a,ply+1)
   else:
    s=-sr(depth-1,-beta,-a,ply+1)
   um()
   if s > best:
    best=s
    best_m=m
   if s > a:
    a=s
    if a>=beta:
     if not b[(m>>7) & 127]:
      KILL[ply][1]=KILL[ply][0]
      KILL[ply][0]=m
      H[zi(b[m&127])][(m>>7)&127]+=depth*depth
     break
  if nlegal==0:
   return -M+ply if chk else 0
  flag=1 if best>=beta else 2 if best<=alpha else 0
  TT[h]=(depth,flag,best,best_m)
  return best
 finally:
  sn.discard(h)
def qc(alpha,beta,ply,chk):
 global nd
 nd += 1
 if nd > ND:
  raise Timeout()
 if hf>=100:
  return 0
 if h in sn:
  return 0
 stand=ev*tn+8
 if not chk:
  if stand>=beta:
   return beta
  if stand > alpha:
   alpha=stand
 sn.add(h)
 try:
  ms=gn(not chk)
  if not chk:
   ms.sort(key=lambda m: V[abs(b[(m>>7) & 127])]*16 - V[abs(b[m & 127])],reverse=True)
  nlegal=0
  for m in ms:
   if not chk:
    v=b[(m>>7) & 127]
    if v and stand+V[abs(v)]+200 < alpha:
     continue
   mk(m)
   if at(ks(tn < 0),tn > 0):
    um()
    continue
   nlegal += 1
   s=-qc(-beta,-alpha,ply+1,ic())
   um()
   if s>=beta:
    return beta
   if s > alpha:
    alpha=s
  if chk and nlegal==0:
   return -M+ply
  return alpha
 finally:
  sn.discard(h)
def th(moves_uci,start_fen):
 global nd,sn,TT
 pf(start_fen)
 sn=set()
 for u in moves_uci:
  mk(pu(u))
  sn.add(h)
 sn.discard(h)
 TT={}
 for i in range(256):
  KILL[i][0]=KILL[i][1]=0
 ms=gn(False)
 if not ms:
  return None
 best=0
 for m in ms:
  mk(m)
  if not at(ks(tn < 0),tn > 0):
   um()
   best=m
   break
  um()
 if not best:
  return None
 nd=0
 def root(lo,hi):
  a=-M
  cur=best
  for m in od(ms,best,0):
   mk(m)
   if at(ks(tn < 0),tn > 0):
    um()
    continue
   try:
    s=-sr(depth - 1,-hi,-max(a,lo),1)
   except Timeout:
    um()
    raise
   um()
   if s > a:
    a=s
    cur=m
  return a,cur
 try:
  for depth in range(1,64):
   a,cur=root(-M,M)
   best=cur
   if a>=M - 100:
    break
 except Timeout:
  pass
 return uci(best)
def post(path,body):
 req=urllib.request.Request(
  ENV+path,
  data=json.dumps(body).encode(),
  headers={"content-type":"application/json"},
 )
 try:
  with urllib.request.urlopen(req) as res:
   return json.load(res)
 except urllib.error.HTTPError as e:
  sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")
def main():
 while True:
  g=post("/game",{})
  if g["status"]=="done":
   break
  while g["status"]=="your_move":
   try:
    mv=th(g["moves"],g["start_fen"])
   except Exception as e:
    print(f"th failed: {e}",file=sys.stderr)
    mv=None
   if mv is None:
    mv=g["legal_moves"][0]
   g=post("/move",{"game": g["game"],"move": mv})
  print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
 print(f"done: {g.get('wins')} won,{g.get('draws')} drawn,{g.get('losses')} lost",file=sys.stderr)
if __name__=="__main__":
 main()
