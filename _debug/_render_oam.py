from PIL import Image
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
    body = m.group(1)
    out = []
    for line in body.splitlines():
        mm = re.findall(r'\$([0-9a-fA-F]{2})', line)
        if len(mm) == 4:
            y = int(mm[0],16); x = int(mm[1],16); tid = int(mm[2],16); attr = int(mm[3],16)
            if x >= 128: x -= 256
            if y >= 128: y -= 256
            out.append((y, x, tid, attr))
    return out

def render(repo, label, outname):
    im = Image.open(repo + '/gfx/titlescreen/titlescreen.png').convert('RGB')
    oam = parse_oam(repo + '/data/oam_frames.asm', label)
    minx = min(o[1] for o in oam); miny = min(o[0] for o in oam)
    maxx = max(o[1] for o in oam)+8; maxy = max(o[0] for o in oam)+8
    canvas = Image.new('RGB', (maxx-minx, maxy-miny), (255,0,255))
    for y, x, tid, attr in oam:
        canvas.paste(get_tile(im, tid, bool(attr & 0x20)), (x-minx, y-miny))
    z = 16
    canvas = canvas.resize((canvas.width*z, canvas.height*z), Image.NEAREST)
    canvas.save('pokepinball-generations-fr/_debug/' + outname)
    print(outname, 'tiles:', [hex(o[2]) for o in oam])

base = 'C:/Users/Remy/PhpstormProjects'
os.chdir(base)
for lbl in ['OAMData_58', 'OAMData_59']:
    render('pokepinball-generations', lbl, '_EN_' + lbl + '.png')
    render('pokepinball-generations-fr', lbl, '_FR_' + lbl + '.png')
