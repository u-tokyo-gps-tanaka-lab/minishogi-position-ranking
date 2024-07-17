#!/usr/bin/env python
# coding: utf-8

# # 55将棋を定義する
# 
# piece については，
# - piece は相手は負，promoteすると +8(相手駒は-8)
# - promoteしていない番号が小さい順
# - promoteしていない駒 < promoteしている駒
# - 自分の駒 < 相手の駒　でソートする．
# 
# 

# ## 駒と局面の定義

# In[ ]:


# ptype
BLANK = 0
KING = 1 # 相手は-1
ROOK = 2 # 相手は-2
BISHOP = 3 # 相手は-3
GOLD = 4 # 相手は-4
SILVER = 5 # 相手は-5
PAWN = 6 # 相手は-6
# 成り駒: 自分なら+8、相手なら-8する

ptype_chars = '.krbgsp'
ptype_kchars = '　玉飛角金銀歩　　　竜馬　全と'

def piece2str(pt):
    isplus = True
    if pt < 0:
        isplus = False
        pt = -pt
    ispromoted = False
    if pt & 8 != 0:
        ispromoted = True
        pt -= 8
    ans = ptype_chars[pt] if not isplus else ptype_chars[pt].upper()
    if ispromoted:
        ans = '+' + ans
    return ans

# if promoted ptype  | 8
def promote(ptype):
    return ptype | 8

def is_promoted(ptype):
    return (ptype & 8) != 0

# player: 1 (先手) or -1 (後手)
# pieceがplayerから見たときに相手の駒かどうか
# pieceとしてBLANKは指定できない
def is_opposite(piece, player):
    if piece == BLANK:
        raise 'BLANK is not a piece'
    if piece > 0:
        return player == -1
    if piece < 0:
        return player == 1

# piece type
def piece2ptype(piece):
    return abs(piece)

def is_in_board(x, y):
    return 0 <= x < 5 and 0 <= y < 5

SENTE = 1
GOTE = -1

# 先手の(y=0, x=0)から見た相対座標
N = (-1, 0)
S = (1, 0)
E = (0, 1)
W = (0, -1)
NW = (-1, -1)
NE = (-1, 1)
SW = (1, -1)
SE = (1, 1)

PTYPE_SHORT_DIRECTIONS: dict[int, list[tuple[int, int]]] = {
    KING : [N, S, E, W, NW, NE, SW, SE],
    ROOK : [],
    BISHOP : [],
    GOLD : [N, S, E, W, NW, NE],
    SILVER: [N, NW, NE, SW, SE],
    PAWN: [N],
    promote(ROOK) : [NE, NW, SW, SE],
    promote(BISHOP) : [E, N, W, S],
}
for ptype in [SILVER, PAWN]:
    PTYPE_SHORT_DIRECTIONS[promote(ptype)] = PTYPE_SHORT_DIRECTIONS[GOLD]

PIECE_SHORT_DIRECTIONS: dict[int, list[tuple[int, int]]] = {}

PTYPE_LONG_DIRECTIONS: dict[int, list[tuple[int, int]]] = {
    ROOK : [N, S, E, W],
    BISHOP : [NE, NW, SW, SE],
}
for ptype in [ROOK, BISHOP]:
    PTYPE_LONG_DIRECTIONS[promote(ptype)] = PTYPE_LONG_DIRECTIONS[ptype]

PIECE_SHORT_DIRECTIONS: dict[int, list[tuple[int, int]]] = {}
PIECE_LONG_DIRECTIONS: dict[int, list[tuple[int, int]]] = {}
for ptype, ds in PTYPE_SHORT_DIRECTIONS.items():
    PIECE_SHORT_DIRECTIONS[ptype] = ds
    PIECE_SHORT_DIRECTIONS[-ptype] = []
    for y, x in ds:
        PIECE_SHORT_DIRECTIONS[-ptype].append((-y, -x))
    if ptype in PTYPE_LONG_DIRECTIONS:
        lds = PTYPE_LONG_DIRECTIONS[ptype]      
    else:
        lds = []        
    PIECE_LONG_DIRECTIONS[ptype] = lds
    PIECE_LONG_DIRECTIONS[-ptype] = []
    for y, x in lds:
        PIECE_LONG_DIRECTIONS[-ptype].append((-y, -x))    






class Position:
    # 実際にはfenは2つ目以上のフィールドを省略できるが，ここでは4に決め打ちする
    def __init__(self, fen="rbsgk/4p/5/P4/KGSBR[-] w 0 1"):
        fenParts = fen.split(' ')
        if len(fenParts) != 4:
            raise 'fen format error'
        self.board = [[0] * 5 for _ in range(5)] # board: 段ごとのリストで盤面を表現する
        sbstart = fenParts[0].index('[')
        bstr = fenParts[0][:sbstart]
        for y, l in enumerate(bstr.split('/')):
            x = 0
            lastplus = False
            for c in l:
                if c == '+':
                    lastplus = True
                elif c.isdigit():
                    x += int(c)
                else:
                    i = ptype_chars.index(c.lower())
                    if lastplus:
                        i = promote(i)
                    if c.islower():
                        i = -i
                    self.board[y][x] = i
                    x += 1
                    lastplus = False
        handstr = fenParts[0][(sbstart + 1):-1]
        self.hands = [[] for _ in range(2)]
        for c in handstr:
            if c == '-':
                continue
            i = ptype_chars.index(c.lower())
            if c.islower():
                self.hands[1].append(-i)
            else:
                self.hands[0].append(i)
        self.side_to_move = 1 if fenParts[1] == 'w' else -1
        self.check_count = int(fenParts[2])
        self.nmoves = int(fenParts[3])

    def fen(self):
        b = []
        for y in range(5):
            line = []
            lastx = -1
            for x in range(5):
                piece = self.board[y][x]
                if piece != 0:
                    if x - lastx > 1:
                        line.append(str(x - lastx - 1))
                    line.append(piece2str(piece))
                    lastx = x
            if lastx < 4:
                line.append(str(5 - lastx - 1))
            b.append(''.join(line))
        b = '/'.join(b)
        hands = []
        for p in range(2):
            for piece in self.hands[p]:
                hands.append(piece2str(piece))
        return f'{b}[{"".join(hands)}] w 0 1'

    def __str__(self):
        return f'Position{(self.side_to_move, self.board, self.hands, self.check_count, self.nmoves)}'


# In[ ]:


p = Position()
print(p)
print(p.fen())

p = Position('1bs1k/4g/5/P4/KGSB1[Prr] w 0 2')
print(p)
print(p.fen())

p = Position('1bs1k/4g/5/P4/KGSB1[Prr] b 0 2')
print(p)
print(p.fen())


# ## 盤面の画像出力

# In[ ]:


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


# In[ ]:


pos = Position('+B+b3/4+R/G1k2/P+SsP1/2K+R1[G] w 0 1')
print(pos.fen())
showstate(pos)


# ## 二歩, 行きどころのない歩の判定
# 

# In[ ]:


def legal_pawn_positions(pos):
    # 二歩
    for x in range(5):
        if sum([1 for y in range(5) if pos.board[y][x] == PAWN]) > 1:
            return False
        if sum([1 for y in range(5) if pos.board[y][x] == -PAWN]) > 1:
            return False

    # 行きどころのない歩
    for x in range(5):
        if pos.board[0][x] == PAWN:
            return False
        if pos.board[4][x] == -PAWN:
           return False

    return True


# ## pseudo legal move生成器

# In[ ]:


import copy

# 先手の陣地はy=0, 後手ならy=4
ZONE_Y_AXIS = {
    SENTE: 0,
    GOTE: 4
}

"""
move:
    {'type'; 'quiet', from': (y, x), 'to': (y, x), 'promote': bool}
    {'type'; 'capture', 'from': (y, x), 'to': (y, x), 'promote': bool, 'capture': piece}
    {'type'; 'drop', 'to': (y, x), 'piece': piece}
"""

# plm: pseudo legal moves

# rook, bishop, promoted rook, promoted bishop
def plm_for_rider(pos: Position, player, piece, y, x):
    pseudo_legal_moves = []
    for dy, dx in PIECE_DIRECTIONS[player * piece]:
        ny, nx = y, x
        while True: # これだとqueenの動きになってしまっている..
            ny += dy
            nx += dx
            if 0 <= ny < 5 and 0 <= nx < 5:
                # quiet
                if pos.board[ny][nx] == BLANK:
                    pseudo_legal_moves.append({'type': 'quiet', 'from': (y, x), 'to': (ny, nx), 'promote': False})
                    if (player == SENTE and ny == ZONE_Y_AXIS[SENTE]) or (player == GOTE and ny == ZONE_Y_AXIS[GOTE]):
                        pseudo_legal_moves.append({'type': 'quiet', 'from': (y, x), 'to': (ny, nx), 'promote': True})
                        # promote済の駒は成れない

                        # 相手の陣地から出て成る動きは？
                # capture
                else:
                    if is_opposite(pos.board[ny][nx], player):
                        pseudo_legal_moves.append({'type': 'capture', 'from': (y, x), 'to': (ny, nx), 'promote': False, 'capture': pos.board[ny][nx]})
                    break
            else:
                break
    return pseudo_legal_moves

# other pieces
def plm_for_walker(pos: Position, player, piece, y, x):
    pseudo_legal_moves = []
    from_sq = (y, x)

    for dy, dx in PIECE_DIRECTIONS[player * piece]:
        to_sq = (y + dy, x + dx)
        if not is_in_board(x + dx, y + dy):
            continue

        to_sq_piece = pos.board[y + dy][x + dx]
        if PAWN == piece2ptype(piece):
            # 進む先が最上段なら成るしかない
            if y + dy == ZONE_Y_AXIS[player]:
                pseudo_legal_moves.append({'type': 'quiet', 'from': from_sq, 'to': to_sq, 'promote': True})
                if to_sq_piece != BLANK:
                    pseudo_legal_moves.append({'type': 'capture', 'from': from_sq, 'to': to_sq, 'promote': True, 'capture': to_sq_piece})
            else: # 進む先が最上段でないなら成らない
                pseudo_legal_moves.append({'type': 'quiet', 'from': from_sq, 'to': to_sq, 'promote': False})
                if to_sq_piece != BLANK:
                    pseudo_legal_moves.append({'type': 'capture', 'from': from_sq, 'to': to_sq, 'promote': False, 'capture': to_sq_piece})
            continue

        if to_sq_piece == BLANK:
            pseudo_legal_moves.append({'type': 'quiet', 'from': from_sq, 'to': to_sq, 'promote': False})
            if y + dy == ZONE_Y_AXIS[player]:
                pseudo_legal_moves.append({'type': 'quiet', 'from': from_sq, 'to': to_sq, 'promote': True})
                # 後ろに下がって成る動きは？
            continue

        if is_opposite(to_sq_piece, player):
            pseudo_legal_moves.append({'type': 'capture', 'from': from_sq, 'to': to_sq, 'promote': False, 'capture': to_sq_piece})
            # promotable
            if y + dy == ZONE_Y_AXIS[player]:
                pseudo_legal_moves.append({'type': 'capture', 'from': from_sq, 'to': to_sq, 'promote': True, 'capture': to_sq_piece})
                # 後ろに下がって成る動きは？
            continue

    return pseudo_legal_moves

# 二手・行きどころのない歩を考慮しない合法手
# →行きどころのない歩は考慮すべき
def generate_pseudo_legal_moves(pos: Position, player=SENTE):
    pseudo_legal_moves = []
    hands = pos.hands[0] if player == SENTE else pos.hands[1]

    # drop move
    for hand_piece in hands:
        for x in range(5):
            for y in range(5):
                to_sq_piece = pos.board[y][x]
                if to_sq_piece == BLANK:
                    pseudo_legal_moves.append({'type': 'drop', 'to': (y, x), 'piece': hand_piece})
        # 重複している持ち駒の考慮は？

    # quiet/capture moves
    for y in range(5):
        for x in range(5):
            piece = pos.board[y][x]
            if piece == BLANK:
                continue
            elif is_opposite(piece, player):
                continue

            if (
                piece2ptype(piece) == ROOK or
                piece2ptype(piece) == BISHOP or
                piece2ptype(piece) == promote(ROOK) or
                piece2ptype(piece) == promote(BISHOP)
            ):
                pseudo_legal_moves.extend(plm_for_rider(pos, player, piece, y, x))
            else:
                pseudo_legal_moves.extend(plm_for_walker(pos, player, piece, y, x))

    return pseudo_legal_moves

def apply_move(pos: Position, move):
    new_pos = copy.deepcopy(pos) # deep copyを自分で書いたほうが安全

    to_y, to_x = move['to']

    if move['type'] == 'drop':
        new_pos.board[to_y][to_x] = move['piece']
        if move['piece'] > 0:
            new_pos.hands[0].remove(move['piece'])
        else:
            new_pos.hands[1].remove(move['piece'])

    # type == 'quiet' or 'capture'
    from_y, from_x = move['from']
    new_pos.board[to_y][to_x] = new_pos.board[from_y][from_x] if move['promote'] == False else promote(new_pos.board[from_y][from_x])
    new_pos.board[from_y][from_x] = BLANK

    new_pos.side_to_move *= -1

    return new_pos




# ## あるプレイヤが詰んでいるかどうか? -> 「直前の手が打ち歩詰め」を判定するためには必要 in_checkmate

# checkmateであるための必要十分条件:
# 1. 王手がかかっている
# 2. 王手を回避する合法手がない
# 
# 合法手がないことはどう書けばいいか？
# 1. 自分の駒を動かす
# 2. 動かした後のposでin_checkを呼ぶ
# 3. これを繰り返す途中で一度でもTrueが返ってきたら，その時点でreturn False

# In[ ]:
def in_check(pos, player):
    return False

def is_checkmate(pos, player):
    if not in_check(pos, player):
        return False

    legal_moves = generate_pseudo_legal_moves(pos, player)
    if legal_moves == None:
        return True

    for move in legal_moves:
        new_pos = apply_move(pos, move)
        if not in_check(new_pos, player):
            return False  # 王手を解消できる合法手がある場合

    return True


# In[ ]:


pos = Position('2kg1/2g2/1g3/1s1G1/1K3[RBBSSSr] w 0 1')
print(is_checkmate(pos, SENTE)) # should be True
print(is_checkmate(pos, GOTE)) # should be False
showstate(pos)


# In[ ]:


pos = Position('2KG1/2G2/1G3/1S1g1/1k3[rbbsssR] w 0 1')
print(is_checkmate(pos, SENTE))
print(is_checkmate(pos, GOTE))
showstate(pos)


# In[ ]:


pos = Position('4k/1g2p/K2S1/Pr1+r1/1B3[BGs] w 0 1')
print(is_checkmate(pos, SENTE)) # should be True
print(is_checkmate(pos, GOTE)) # should be False
showstate(pos)


# In[ ]:


pos = Position('4K/1G2P/k2s1/pR1+R1/1b3[bgS] w 0 1')
print(is_checkmate(pos, SENTE)) # should be False
print(is_checkmate(pos, GOTE)) # should be True
showstate(pos)


# ## 一手前の局面をすべて作成する generate_previous_positions

# In[ ]:


def generate_previous_positions(pos: Position):
    previous_positions = []
    current_player = pos.side_to_move
    previous_player = -current_player

    for y in range(5):
        for x in range(5):
            piece = pos.board[y][x]
            if not is_opposite(piece, current_player):
                continue


    return previous_positions

