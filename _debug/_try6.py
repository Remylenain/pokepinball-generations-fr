from PIL import Image, ImageDraw
import re, os
base='C:/Users/Remy/PhpstormProjects'; os.chdir(base)
repo='pokepinball-generations-fr'
im=Image.open(repo+'/gfx/titlescreen/titlescreen.png').convert('RGB')
def tile(tid,xf=False):
    c=tid%16;r=tid//16;t=im.crop((c*8,r*8,c*8+8,r*8+8))
    return t.transpose(Image.FLIP_LEFT_RIGHT) if xf else t
# base 5-col grid (top row tiles, mid row tiles) for line1 NOUVEAU JEU
top=[0x55,0x56,0x57,0x58,0x59]
bot=[0x5b,0x5c,0x5d,0x5e,0x5f]
cands=[('5a_60',0x5a,0x60),('69_68',0x69,0x68),('5a_68',0x5a,0x68),('6a_68',0x6a,0x68)]
z=20
rowsimg=[]
for name,t6,b6 in cands:
    cv=Image.new('RGB',(6*8,16),(255,0,255))
    for i,t in enumerate(top): cv.paste(tile(t),(i*8,0))
    for i,t in enumerate(bot): cv.paste(tile(t),(i*8,8))
    cv.paste(tile(t6),(5*8,0)); cv.paste(tile(b6),(5*8,8))
    cv=cv.resize((6*8*z,16*z),Image.NEAREST)
    d=ImageDraw.Draw(cv); d.text((2,2),name,fill=(255,255,0))
    rowsimg.append(cv)
W=max(i.width for i in rowsimg); H=sum(i.height for i in rowsimg)+10*len(rowsimg)
out=Image.new('RGB',(W,H),(30,30,30)); y=0
for i in rowsimg: out.paste(i,(0,y)); y+=i.height+10
out.save(repo+'/_debug/_try6.png'); print('ok')
