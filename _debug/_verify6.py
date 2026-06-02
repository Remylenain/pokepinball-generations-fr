from PIL import Image, ImageDraw
import re, os
base='C:/Users/Remy/PhpstormProjects'; os.chdir(base)
repo='pokepinball-generations-fr'
im=Image.open(repo+'/gfx/titlescreen/titlescreen.png').convert('RGB')
def tile(tid,xf=False):
    c=tid%16;r=tid//16;t=im.crop((c*8,r*8,c*8+8,r*8+8))
    return t.transpose(Image.FLIP_LEFT_RIGHT) if xf else t
def parse(label):
    txt=open(repo+'/data/oam_frames.asm').read()
    m=re.search(label+r':[^\n]*\n(.*?)\n\s*db \$80',txt,re.S)
    out=[]
    for ln in m.group(1).splitlines():
        mm=re.findall(r'\$([0-9a-fA-F]{2})',ln)
        if len(mm)==4:
            y,x,t,a=[int(v,16) for v in mm]
            if x>=128:x-=256
            if y>=128:y-=256
            out.append((y,x,t,a))
    return out

for label in ['OAMData_58','OAMData_59']:
    oam=parse(label)
    # add 6th column: top $68 @Y8 X40, bottom $69 @Y16 X40, blank $60 @Y24 X40
    oam+=[(8,40,0x68,0),(16,40,0x69,0),(24,40,0x60,0)]
    minx=min(o[1] for o in oam);miny=min(o[0] for o in oam)
    maxx=max(o[1] for o in oam)+8;maxy=max(o[0] for o in oam)+8
    cv=Image.new('RGB',(maxx-minx,maxy-miny),(255,0,255))
    for y,x,t,a in oam: cv.paste(tile(t,bool(a&0x20)),(x-minx,y-miny))
    z=18; cv=cv.resize((cv.width*z,cv.height*z),Image.NEAREST)
    cv.save(repo+'/_debug/_VERIFY_'+label+'.png')
print('ok')
