from collections import Counter
import minishogi
from minishogi import Ptype, BLACK, WHITE, Player
from minishogi.minishogi import ptype_kchars

from PIL import Image, ImageDraw, ImageFont
# ryzen0
# IPAfont_path = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
# thinkpad
IPAfont_path = '/usr/share/fonts/OTF/ipag.ttf'

def kimage(kchar, grid=40):
    im = Image.new("RGB", (grid, grid))
    draw = ImageDraw.Draw(im)
    draw.rectangle([(0,0),(grid, grid)],fill=(255,255,255))
    fnt = ImageFont.truetype(IPAfont_path, grid)
    draw.text((0, 0), kchar, font=fnt, fill=(0, 0, 0))
    return im
piece2img = {}
for i, kchar in enumerate(ptype_kchars):
    if kchar == '　':
        continue
    isize = 30
    piece2img[Ptype(i).to_piece(WHITE)] = kimage(kchar, isize)
    img = piece2img[i].crop((0, 0, isize, isize))
    piece2img[Ptype(i).to_piece(BLACK)] = img.rotate(180)
piece2img2 = {}
for piece, img in piece2img.items():
    piece2img2[piece] = img.resize((img.width // 2, img.height // 2))

def position_image(pos):
    grid = 40
    offset_y = 20
    offset_x = 70
    W, H = 5, 5
    im = Image.new("RGB", (grid * W + 130, grid * H + 50))
    draw = ImageDraw.Draw(im)
    draw.rectangle([(0,0),(grid * W + 130, grid * H + 50)],fill=(255,255,255))
    #fnt = ImageFont.truetype("Humor-Sans.ttf",)
    fnt = ImageFont.truetype(IPAfont_path,25)
    smallfnt = ImageFont.truetype(IPAfont_path,15)
    for y in range(H + 1):
        draw.line([(offset_x, offset_y + y * grid), (offset_x + W * grid, offset_y + y * grid)],fill=(0,0,0),width=3)
    for x in range(W + 1):
        draw.line([(offset_x + x * grid, offset_y), (offset_x + x * grid, offset_y + H * grid)],fill=(0,0,0),width=3)
    for x in range(W):
        draw.text((offset_x + (x + 0.4)*grid , offset_y + (H + 0.01) * grid),chr(ord('a') + x), font=fnt,fill=(0,0,0))
    for y in range(H):
        draw.text((offset_x - 0.4*grid , offset_y + (y + 0.2) * grid),str(H - y), font=fnt,fill=(0,0,0))
    for y in range(H):
        for x in range(W):
            piece = pos.board[y][x]
            if piece == 0:
                continue
            pimage = piece2img[piece]
            cx, cy = (offset_x + grid * (x * 2 + 1) // 2 - pimage.width // 2, offset_y + grid * (y * 2 + 1) // 2 - pimage.height // 2)
            im.paste(pimage, (cx, cy))
    turnx, turny = int(grid * (W + 0.5) + offset_x), int(grid * 0.5 + offset_y)
    if pos.side_to_move == WHITE:
        turny = int(grid * (H - 0.5)+ offset_y)
    r = 10
    draw.ellipse((turnx - r, turny - r, turnx + r, turny + r),fill=(0, 0, 0))
    # hands
    for pl in range(2):
        hands = pos.hands[pl]
        counts = Counter(hands)
        kvs = list(counts.items())
        for i, (k, v) in enumerate(kvs):
            piece = k.to_piece(WHITE)
            pimage = piece2img2[piece]
            if pl == 0:
                cx, cy = int(grid * W + offset_x + 0.5 * grid - 6), int(grid * (H - 1 - 0.5 * (i + 1)) + offset_y)
            else:
                cx, cy = int(offset_x - 1 * grid - 17), int(grid * (0.1 + 0.5 * i)+ offset_y)
            im.paste(pimage, (cx, cy))
            draw.text((cx + 20, cy + 2),'x ' + str(v), smallfont=fnt,fill=(0,0,0))
    return im
def showstate(state, filename=None):
    #rstate = flip_vertical(state)
    #print(f'(canwin, candraw)[{state}]={(canwin[state], candraw[state])}')
    #print(f'(canwin, candraw)[{rstate}]={(canwin[rstate], candraw[rstate])}')
    img =  position_image(state)
    if filename:
        img.save(filename)
    return img
def show_images_hv(images, w, filename=None, showarrow=True):
    width = images[0].width
    height = images[0].height
    for im in images:
        assert im.width == width and im.height == height
    allwidth = width * w
    n = len(images)
    h = (n + w - 1) // w
    ans = Image.new('RGB', (w * width, h * height))
    draw = ImageDraw.Draw(ans)
    draw.rectangle([(0,0),(w * width, h * height)],fill=(255,255,255))
    fnt = ImageFont.truetype(IPAfont_path,25)
    x, y = 0, 0
    for i, im in enumerate(images):
        ans.paste(im, (x, y))
        if showarrow and i != n - 1:
            draw = ImageDraw.Draw(ans)
            draw.text((x + width * 0.9 , y + height * 0.35),">", font=fnt,fill=(0,0,0))
        x += width
        if x >= w * width:
            x = 0
            y += height
    if filename:
        ans.save(filename)
    return ans
