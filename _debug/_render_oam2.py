from PIL import Image, ImageDraw
import re, os

def get_tile(im, tid, xflip=False):
    col = tid % 16; row = tid // 16
    t = im.crop((col*8, row*8, col*8+8, row*8+8))
    if xflip:
        t = t.transpose(Image.FLIP_LEFT_RIGHT)
    return t

def parse_oam(asmpath, label):
    txt = open(asmpath).read()
    m = re.search(label + r':[^\n]*\n(.*?)\n\s*db \$80', txt, re.S)
    out = []
    for line in m.group(1).splitlines():
        mm = re.findall(r'\$([0-9a-fA-F]{2})', line)
        if len(mm) == 4:
            y = int(mm[0],16); x = int(mm[1],16); tid = int(mm[2],16); attr = int(mm[3],16)
            if x >= 128: x -= 256
            if y >= 128: y -= 256
            out.append((y, x, tid, attr))
    return out

base = 'C:/Users/Remy/PhpstormProjects'
os.chdir(base)
repo = 'pokepinball-generations-fr'
im = Image.open(repo + '/gfx/titlescreen/titlescreen.png').convert('RGB')
oam = parse_oam(repo + '/data/oam_frames.asm', 'OAMData_59')
# also show one extra column to the right (X=40) for the next tile in each row
extra = [(8,40,0x5a,0),(16,40,0x60,0),(24,40,0x66,0)]
minx=min(o[1] for o in oam); miny=min(o[0] for o in oam)
maxx=max([o[1] for o in oam]+[40])+8; maxy=max(o[0] for o in oam)+8
z=26
canvas=Image.new('RGB',((maxx-minx)*z,(maxy-miny)*z),(255,0,255))
d=ImageDraw.Draw(canvas)
def draw(lst, outline):
    for y,x,tid,attr in lst:
        t=get_tile(im,tid,bool(attr&0x20)).resize((8*z,8*z),Image.NEAREST)
        canvas.paste(t,((x-minx)*z,(y-miny)*z))
        d.rectangle([(x-minx)*z,(y-miny)*z,(x-minx)*z+8*z,(y-miny)*z+8*z],outline=outline,width=2)
        d.text(((x-minx)*z+3,(y-miny)*z+2),format(tid,'02x'),fill=(255,255,0))
draw(oam,(0,150,255))
canvas.save(repo+'/_debug/_FR59_labeled.png'); print('ok')
