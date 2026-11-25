import re, json, math, sys, colorsys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
IMG='/home/mic/Downloads/Gemini_Generated_Image_mb4jtwmb4jtwmb4j.jpg'
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
src=open('/home/mic/Documents/michelangelo/cad/mx_led/logo_pts.scad').read()
Wl=float(re.search(r'LOGO_W = ([\d.]+)',src).group(1)); S=300/Wl
P=np.array([(float(a)*S,float(b)*S) for a,b in re.findall(r'\[(-?[\d.]+),(-?[\d.]+)\]', src.split('LOGO_PTS')[1])])
n=len(P)
photo=Image.open(IMG).convert('RGB'); IW,IH=photo.size
H=np.array(json.load(open('H.json')))

# ---- scala e posizione reali dalle due viti nel muro (interasse 238 mm)
Hi=np.linalg.inv(H)
def img2plane(u,v):
    q=Hi@np.array([u,v,1.0]); return q[:2]/q[2]
SL,SR=img2plane(390,1650),img2plane(970,1653)
Du=np.linalg.norm(SR-SL); k=Du/238.0                     # unita' piano per mm
print('logo sul legno largo circa %.0f mm'%(300/k))
LW=260.0
Pmm=np.array([(float(a)*LW/Wl,float(b)*LW/Wl) for a,b in re.findall(r'\[(-?[\d.]+),(-?[\d.]+)\]', src.split('LOGO_PTS')[1])])
scr_mm=np.array([10.75,89.75])
ang=math.atan2(SR[1]-SL[1],SR[0]-SL[0]); ca,sa=math.cos(ang),math.sin(ang)
Rot=np.array([[ca,-sa],[sa,ca]])
P=((Pmm-scr_mm)*k)@Rot.T+SL
SCREWS=np.array([SL,SR])
n=len(P)

# ---- camera da omografia (f dal vincolo di ortogonalita')
cx,cy=IW/2,IH/2
def a(h): return np.array([h[0]-cx*h[2], h[1]-cy*h[2]])
f=math.sqrt(-(a(H[:,0])@a(H[:,1]))/(H[2,0]*H[2,1]))
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]]); Ki=np.linalg.inv(K)
M=Ki@H; lam=2/(np.linalg.norm(M[:,0])+np.linalg.norm(M[:,1])); M*=lam
if M[2,2]<0: M=-M
U,_,Vt=np.linalg.svd(M[:,:2],full_matrices=False); R12=U@Vt
r1,r2=R12[:,0],R12[:,1]; r3=np.cross(r1,r2); t=M[:,2]
R=np.c_[r1,r2,r3]; C=-R.T@t
if C[2]<0: r3=-r3; R=np.c_[r1,r2,r3]; C=-R.T@t
print('f=%.0f  camera (mm, sistema logo):'%f, C.round(0))
def proj(X):
    X=np.atleast_2d(X); q=(K@(R@X.T+t[:,None])).T; return q[:,:2]/q[:,2:]

# ---- geometria (mm): retro a 10 dal muro, fronte a 34
Z_BACK, Z_FRONT = 10.0*k, 34.0*k
BANDS=[(10.0*k,18.25*k,'k'),(18.25*k,29.15*k,'w'),(29.15*k,34.0*k,'k')]   # nero / diffusore / nero
area=sum(P[i,0]*P[(i+1)%n,1]-P[(i+1)%n,0]*P[i,1] for i in range(n))/2
sg=1 if area>0 else -1
seglen=np.linalg.norm(np.roll(P,-1,0)-P,axis=1); cum=np.r_[0,np.cumsum(seglen)]; per=cum[-1]

# ---- 1) cancella il pannello di legno
# Ogni pixel coperto viene interpolato tra i due punti di muro che si trovano
# uscendo dal pannello nelle due direzioni parallele al confine sole/ombra:
# cosi' la zona al sole e quella in ombra restano ognuna dalla sua parte.
board=[(425,1345),(1035,1338),(1078,1385),(1068,2030),(1015,2110),(245,2060),(215,1985),(375,1395)]
mimg=Image.new('L',(IW,IH),0); dm=ImageDraw.Draw(mimg); dm.polygon(board,fill=255)
dm.line(board+[board[0]],fill=255,width=120,joint='curve')   # include l'ombra del pannello sul muro
arr=np.asarray(photo).astype(float); mk=np.asarray(mimg)>0
X0,Y0,X1,Y1=40,1000,1400,2330
d=np.array([1447-518,1652-2390],float); d/=np.linalg.norm(d)
ys,xs=np.nonzero(mk)
def exit_dist(sign):
    dist=np.full(len(xs),-1.0)
    for st in range(0,1600,2):
        px=np.clip((xs+sign*d[0]*st).round().astype(int),0,IW-1)
        py=np.clip((ys+sign*d[1]*st).round().astype(int),0,IH-1)
        out=(~mk[py,px])&(dist<0)
        dist[out]=st
        if (dist>=0).all(): break
    dist[dist<0]=1600
    return dist+22
def sample(sign,dist):
    px=np.clip((xs+sign*d[0]*dist).round().astype(int),0,IW-1)
    py=np.clip((ys+sign*d[1]*dist).round().astype(int),0,IH-1)
    return arr[py,px]
# sfocatura normalizzata: ignora i pixel del pannello
valid=(~mk).astype(float)
def gblur(a,r): return np.asarray(Image.fromarray(a.clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float)
def nblur(img,r):
    num=gblur(img*valid[...,None],r)
    den=np.asarray(Image.fromarray((valid*255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float)[...,None]/255
    return num/np.maximum(den,1e-2)
blurred=nblur(arr,10)
fine=arr-gblur(arr,5)
fine[:1260,1075:1190]=0        # niente corda bianca nella texture
da,db=exit_dist(1),exit_dist(-1)
pa=np.clip((xs+d[0]*da).round().astype(int),0,IW-1); qa=np.clip((ys+d[1]*da).round().astype(int),0,IH-1)
pb=np.clip((xs-d[0]*db).round().astype(int),0,IW-1); qb=np.clip((ys-d[1]*db).round().astype(int),0,IH-1)
A=blurred[qa,pa]; B=blurred[qb,pb]
wa=(db/(da+db))[:,None]
low=A*wa+B*(1-wa)
# texture fine: muro in ombra sopra il pannello, stesse colonne
tex_shade=fine[np.clip(ys-865,0,IH-1),xs]
sx=np.clip((xs+d[0]*420).round().astype(int),0,IW-1); sy=np.clip((ys+d[1]*420).round().astype(int),0,IH-1)
tex_sun=fine[sy,sx]
line_y=2390+(xs-518)*d[1]/d[0]
sun=(1/(1+np.exp(-(ys-line_y)/4)))[:,None]
tex=(tex_shade*(1-sun)+tex_sun*sun)*1.1
fillv=low+tex*0.9
out=arr.copy(); out[ys,xs]=fillv
feather=np.asarray(Image.fromarray((mk*255).astype('uint8')).filter(ImageFilter.GaussianBlur(14))).astype(float)[...,None]/255
arr=arr*(1-feather)+out*feather
clean=arr.clip(0,255).astype('uint8')
Image.fromarray(clean).save(f'{OUT}/muro_pulito.png')

# colore del muro locale (per illuminare il diffusore come il muro in ombra)
wall=np.asarray(Image.fromarray(clean).filter(ImageFilter.GaussianBlur(40))).astype(float)

def render(mode):
    base=clean.astype(float).copy()
    if mode=='night':
        base=base*np.array([0.20,0.22,0.30])          # sera: foto scurita e piu' fredda
    SS=3                                               # supersampling
    cw,ch=(X1-X0)*SS,(Y1-Y0)*SS
    def tocanvas(q): return [((x-X0)*SS,(y-Y0)*SS) for x,y in q]
    # ombra / alone sul muro
    foot=proj(np.c_[P,np.zeros(n)])
    if mode=='day':
        sh=Image.new('L',(cw,ch),0)
        footd=proj(np.c_[P+[0,-6],np.zeros(n)])
        ImageDraw.Draw(sh).polygon(tocanvas(footd),fill=255)
        sh=sh.resize((X1-X0,Y1-Y0),Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
        s=np.asarray(sh).astype(float)[...,None]/255
        base[Y0:Y1,X0:X1]*=1-0.45*s
    else:
        glow=np.zeros((ch//SS,cw//SS,3))
        g=Image.new('RGB',(cw,ch),(0,0,0)); dg=ImageDraw.Draw(g)
        for i in range(n):
            hue=(cum[i]/per)%1.0; col=np.array(colorsys.hsv_to_rgb(hue,0.85,1.0))*255
            mid=(P[i]+P[(i+1)%n])/2; nrm=np.array([P[(i+1)%n,1]-P[i,1], -(P[(i+1)%n,0]-P[i,0])])*sg
            nrm/=np.linalg.norm(nrm)+1e-9
            q=proj(np.array([[*(P[i]+nrm*1),0],[*(P[(i+1)%n]+nrm*1),0],[*(P[(i+1)%n]+nrm*28),0],[*(P[i]+nrm*28),0]]))
            dg.polygon(tocanvas(q),fill=tuple(int(c) for c in col))
        g=g.resize((X1-X0,Y1-Y0),Image.LANCZOS)
        for rad,k in ((25,0.55),(70,0.45)):
            glow+=np.asarray(g.filter(ImageFilter.GaussianBlur(rad))).astype(float)*k
        base[Y0:Y1,X0:X1]+=glow*np.array([1,1,1])*0.9
    # facce laterali visibili, dalla piu' lontana
    quads=[]
    for i in range(n):
        p0,p1=P[i],P[(i+1)%n]; d=p1-p0; L=np.linalg.norm(d)
        if L<1e-6: continue
        nrm=np.array([d[1],-d[0]])*sg/L
        mid=(p0+p1)/2
        view=C-np.r_[mid,(Z_BACK+Z_FRONT)/2]
        if view[:2]@nrm<=0: continue
        # luce: cielo dall'alto (+y) e un po' di diffusa
        sky=0.55+0.45*nrm[1]
        for z0,z1,kind in BANDS:
            X=np.array([[*p0,z0],[*p1,z0],[*p1,z1],[*p0,z1]])
            dist=np.linalg.norm(X.mean(0)-C)
            quads.append((dist,X,kind,sky,i))
    quads.sort(key=lambda q:-q[0])
    im=Image.new('RGBA',(cw,ch),(0,0,0,0)); dr=ImageDraw.Draw(im)
    for dist,X,kind,sky,i in quads:
        q=proj(X); px=int(np.clip(q[:,0].mean(),0,IW-1)); py=int(np.clip(q[:,1].mean(),0,IH-1))
        if kind=='k':
            v=18+22*sky
            col=(v,v,v*1.02)
            if mode=='night': col=tuple(c*0.35 for c in col)
        else:
            if mode=='day':
                col=tuple(wall[py,px]*(0.62+0.38*sky)*np.array([1.0,1.0,1.03]))
            else:
                hue=(cum[i]/per)%1.0
                # punti morbidi: 75 LED lungo il perimetro
                ph=(cum[i]/per*75)%1.0; dot=0.55+0.45*math.cos(math.pi*ph)**4
                col=tuple(np.array(colorsys.hsv_to_rgb(hue,0.55,1.0))*255*dot)
        dr.polygon(tocanvas(q),fill=tuple(int(max(0,min(255,c))) for c in col)+(255,))
    # faccia frontale (nero opaco, leggero gradiente di luce dall'alto)
    front=proj(np.c_[P,np.full(n,Z_FRONT)])
    fm=Image.new('L',(cw,ch),0); ImageDraw.Draw(fm).polygon(tocanvas(front),fill=255)
    yy=np.linspace(0,1,ch)[:,None]
    fv=(46-10*yy)*np.ones((1,cw)) if mode=='day' else (14-3*yy)*np.ones((1,cw))
    fimg=Image.fromarray(np.dstack([fv,fv,fv*1.03]).clip(0,255).astype('uint8')).convert('RGBA')
    im.paste(fimg,(0,0),fm)
    im=im.resize((X1-X0,Y1-Y0),Image.LANCZOS)
    a=np.asarray(im).astype(float); al=a[...,3:4]/255
    reg=base[Y0:Y1,X0:X1]
    base[Y0:Y1,X0:X1]=reg*(1-al)+a[...,:3]*al
    out=Image.fromarray(base.clip(0,255).astype('uint8'))
    return out
for mode in ('day','night'):
    o=render(mode); o.save(f'{OUT}/render_{mode}.jpg',quality=92)
    o.crop((100,1150,1250,2250)).save(f'{OUT}/render_{mode}_zoom.jpg',quality=92)
print('ok')
