import minishogi
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
    piece2img[i] = kimage(kchar, isize)
    img = piece2img[i].crop((0, 0, isize, isize))
    piece2img[-i] = img.rotate(180)
def position_image(pos):
    grid = 40
    offset = 20
    W, H = 5, 5
    im = Image.new("RGB", (grid * W + 90, grid * H + 90))
    draw = ImageDraw.Draw(im)
    draw.rectangle([(0,0),(grid * W + 90, grid * H + 90)],fill=(255,255,255))
    #fnt = ImageFont.truetype("Humor-Sans.ttf",)
    fnt = ImageFont.truetype(IPAfont_path,25)
    for y in range(H + 1):
        draw.line([(offset, offset + y * grid), (offset + W * grid, offset + y * grid)],fill=(0,0,0),width=3)
    for x in range(W + 1):
        draw.line([(offset + x * grid, offset), (offset + x * grid, offset + H * grid)],fill=(0,0,0),width=3)
    for x in range(W):
        draw.text((offset + (x + 0.4)*grid , offset + (H + 0.01) * grid),chr(ord('a') + x), font=fnt,fill=(0,0,0))
    for y in range(H):
        draw.text((offset - 0.4*grid , offset + (y + 0.2) * grid),str(H - y), font=fnt,fill=(0,0,0))
    for y in range(H):
        for x in range(W):
            piece = pos.board[y][x]
            if piece == 0:
                continue
            pimage = piece2img[piece]
            cx, cy = (offset + grid * (x * 2 + 1) // 2 - pimage.width // 2, offset + grid * (y * 2 + 1) // 2 - pimage.height // 2)
            im.paste(pimage, (cx, cy))
    turnx, turny = grid * W + offset * 2, int(grid * 0.5 + offset)
    if pos.side_to_move > 0:
        turny = int(grid * (H - 0.5)+ offset)
    r = 10
    draw.ellipse((turnx - r, turny - r, turnx + r, turny + r),fill=(0, 0, 0))
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
