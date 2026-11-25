import re, json, numpy as np
from PIL import Image, ImageDraw
IMG='/home/mic/Downloads/Gemini_Generated_Image_mb4jtwmb4jtwmb4j.jpg'
src=open('/home/mic/Documents/michelangelo/cad/mx_led/logo_pts.scad').read()
W=float(re.search(r'LOGO_W = ([\d.]+)',src).group(1)); S=300/W
P=np.array([(float(a)*S,float(b)*S) for a,b in re.findall(r'\[(-?[\d.]+),(-?[\d.]+)\]', src.split('LOGO_PTS')[1])])
im=np.asarray(Image.open(IMG).convert('RGB')).astype(float)
X0,Y0,X1,Y1=330,1340,1060,1820           # zona del logo sul legno (senza scritta)
lum=im[Y0:Y1,X0:X1].mean(2)
mask=(lum<75)
def dlt(src,dst):
    A=[]
    for (x,y),(u,v) in zip(src,dst):
        A+= [[-x,-y,-1,0,0,0,u*x,u*y,u],[0,0,0,-x,-y,-1,v*x,v*y,v]]
    _,_,Vt=np.linalg.svd(np.array(A)); H=Vt[-1].reshape(3,3); return H/H[2,2]
def proj(H,pts):
    q=np.c_[pts,np.ones(len(pts))]@H.T; return q[:,:2]/q[:,2:]
src_pts=[(11.5,103.9),(103.9,103.9),(196.5,11.9),(287.8,103.0),(150,184.6),(207.7,140),(287.1,13),(0,150)]
dst_pts=[(430,1543),(609,1540),(760,1750),(980,1560),(703,1402),(825,1486),(970,1755),(412,1467)]
H0=dlt(src_pts,dst_pts)
def raster(H):
    c=Image.new('L',(X1-X0,Y1-Y0),0)
    q=proj(H,P)-[X0,Y0]
    ImageDraw.Draw(c).polygon([tuple(p) for p in q],fill=1)
    return np.asarray(c).astype(bool)
def cost(v):
    H=np.append(v,1).reshape(3,3)
    r=raster(H); inter=(r&mask).sum(); uni=(r|mask).sum()
    return 1-inter/uni
v0=H0.flatten()[:8]
# Nelder-Mead semplice
def nm(f,x0,steps,it=1500):
    n=len(x0); pts=[x0]+[x0+np.eye(n)[i]*steps[i] for i in range(n)]
    vals=[f(p) for p in pts]
    for k in range(it):
        o=np.argsort(vals); pts=[pts[i] for i in o]; vals=[vals[i] for i in o]
        c=np.mean(pts[:-1],0); xr=c+(c-pts[-1]); fr=f(xr)
        if fr<vals[0]:
            xe=c+2*(c-pts[-1]); fe=f(xe)
            pts[-1],vals[-1]=(xe,fe) if fe<fr else (xr,fr)
        elif fr<vals[-2]: pts[-1],vals[-1]=xr,fr
        else:
            xc=c+0.5*(pts[-1]-c); fc=f(xc)
            if fc<vals[-1]: pts[-1],vals[-1]=xc,fc
            else:
                pts=[pts[0]]+[pts[0]+0.5*(p-pts[0]) for p in pts[1:]]; vals=[vals[0]]+[f(p) for p in pts[1:]]
    i=int(np.argmin(vals)); return pts[i],vals[i]
print('IoU iniziale',1-cost(v0))
steps=np.abs(v0)*0.02+1e-6
v,c=nm(cost,v0,steps)
v,c=nm(cost,v,np.abs(v)*0.005+1e-7)
print('IoU finale',1-c)
H=np.append(v,1).reshape(3,3)
json.dump(H.tolist(),open('H.json','w'))
# overlay di controllo
o=Image.open(IMG).convert('RGB'); d=ImageDraw.Draw(o)
d.line([tuple(p) for p in proj(H,P)]+[tuple(proj(H,P)[0])],fill=(255,0,0),width=3)
o.crop((200,1250,1150,2150)).save('fit_check.png')
