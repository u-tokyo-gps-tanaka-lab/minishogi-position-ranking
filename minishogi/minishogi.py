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
def unpromote(ptype):
    return ptype & 7

def is_promoted(ptype):
    return (ptype & 8) != 0

# promote可能か?
def can_promote_ptype(ptype):
    assert ptype > 0
    return ptype & 8 == 0 and ptype != KING and ptype != GOLD


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
def ptype2piece(player, ptype):
    return player * ptype

def is_on_board(y, x):
    return 0 <= x < 5 and 0 <= y < 5

SENTE = 1
GOTE = -1
def player2offset(player):
    return 0 if player > 0 else 1
offset2player = [SENTE, GOTE]

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

# 先手の陣地はy=0, 後手ならy=4
ZONE_Y_AXIS = {
    SENTE: 0,
    GOTE: 4
}
def can_promote_y(player, y):
    return y == ZONE_Y_AXIS[player]

def color2c(color):
    if color < 0:
        return 'b'
    else:
        return 'w'

# square は (y, x) の順で指定する．
# drop move は (10, ptype) で指定する．

def s2sq(s):
    assert len(s) == 2
    if s[1] == '@':
        i = ptype_chars.index(s[0].lower())
        if s[0].islower():
            i = -i
        return (Move.DROP_Y, i)
    assert 'a' <= s[0] <= 'e'
    x = ord(s[0]) - ord('a')
    assert '1' <= s[1] <= '5'
    y = 5 - int(s[1])
    return (y, x)
def sq2s(sq):
    y, x = sq
    if y == Move.DROP_Y:
        c = ptype_chars[piece2ptype(x)].upper()
        return f'{c}@'
    return f'{"abcde"[x]}{"54321"[y]}'
class Move:
    DROP_Y = 10
    def __init__(self, from_sq, to_sq, is_promote):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.is_promote = is_promote
    def __str__(self):
        return f'Move({self.from_sq, self.to_sq, self.is_promote})'
    def __repr__(self):
        return self.__str__()
    def make_drop_move(piece, to_sq):
        return Move((Move.DROP_Y, piece), to_sq, False)
    def from_uci(s):
        assert len(s) in [4, 5]
        from_sq, to_sq = s2sq(s[:2]), s2sq(s[2:4])
        is_promote = len(s) == 5 and s[4] == '+'
        return Move(from_sq, to_sq, is_promote)
    def to_uci(self):
        return sq2s(self.from_sq) + sq2s(self.to_sq) + ('+' if self.is_promote else '')
    def is_drop(self):
        return self.from_sq[0] == Move.DROP_Y
    def __hash__(self):
        return hash((self.from_sq, self.to_sq, self.is_promote))
    def __eq__(self, other):
        return self.from_sq == other.from_sq and self.to_sq == other.to_sq and self.is_promote == other.is_promote
# fairy-stockfish では UCI::move でMoveからStringに変換する．


class Position:
    # 実際にはfenは2つ目以上のフィールドを省略できるが，ここでは4に決め打ちする
    def __init__(self, fen="rbsgk/4p/5/P4/KGSBR[-] w 0 1", tdata=None):
        if fen == '' and tdata is not None:
            self.board, self.hands, self.side_to_move, self.check_count, self.nmoves = tdata
            return
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
        return f'{b}[{"".join(hands)}] {color2c(self.side_to_move)} {self.check_count} {self.nmoves}'

    def can_move_on(self, player, y, x):
        return self.board[y][x] * player <= 0

    # plm: pseudo legal moves
    # rook, bishop, promoted rook, promoted bishop
    def plm_piece(self, moves, player, ptype, y, x):
        for dy, dx in PIECE_LONG_DIRECTIONS[player * ptype]:
            ny, nx = y + dy, x + dx
            while is_on_board(ny, nx): # これだとqueenの動きになってしまっている..
                # quiet
                if self.can_move_on(player, ny, nx):
                    moves.append(Move((y, x), (ny, nx), False))
                    if can_promote_ptype(ptype) and (can_promote_y(player, y) or can_promote_y(player, ny)):
                        moves.append(Move((y, x), (ny, nx), True))
                if self.board[ny][nx] != BLANK:
                    break
                ny += dy
                nx += dx
        for dy, dx in PIECE_SHORT_DIRECTIONS[player * ptype]:
            ny, nx = y + dy, x + dx
            if not is_on_board(ny, nx): continue
            if self.can_move_on(player, ny, nx):
                if not (ptype == PAWN and can_promote_y(player, ny)):
                    moves.append(Move((y, x), (ny, nx), False))
                if can_promote_ptype(ptype) and (can_promote_y(player, y) or can_promote_y(player, ny)):
                    moves.append(Move((y, x), (ny, nx), True))
    def all_drop_moves(self, moves, player):
        all_hand_piece = set(self.hands[player2offset(player)])
        if len(all_hand_piece) == 0:
            return
        for x in range(5):
            xpawncount = sum(self.board[y][x] == ptype2piece(player, PAWN) for y in range(5))
            for y in range(5):
                if self.board[y][x] != BLANK:
                    continue
                for p in all_hand_piece:
                    if not(p == PAWN and (xpawncount == 1 or can_promote_y(player, y))):
                        moves.append(Move.make_drop_move(piece2ptype(p), (y, x)))

    def plm(self, player):
        moves = []
        for y in range(5):
            for x in range(5):
                piece = self.board[y][x]
                if player * piece > 0:
                    self.plm_piece(moves, player, piece2ptype(piece), y, x)
        self.all_drop_moves(moves, player)
        print(f'moves={moves}')
        return moves
    def king_pos(self, player):
        kp = ptype2piece(player, KING)
        for y in range(5):
            for x in range(5):
                if self.board[y][x] == kp:
                    return (y, x)
        return (-1, -1)                
    def in_check(self, player):
        kingpos = self.king_pos(player)
        op = -player
        moves = self.plm(op)
        for m in moves:
            if m.to_sq == kingpos:
                return True
        return False 
    def apply_move(self, player, move):
        new_board = list(list(l) for l in self.board)
        new_hands = list(list(l) for l in self.hands)
        to_sq = move.to_sq
        to_y, to_x = to_sq
        oldp = self.board[to_y][to_x]
        from_sq = move.from_sq
        pi = player2offset(player)
        if move.is_drop():
            ptype = from_sq[1]
            drop_piece = ptype2piece(player, ptype)
            new_board[to_y][to_x] = drop_piece
            new_hands[pi].remove(drop_piece)
        else:
            from_y, from_x = from_sq
            piece = self.board[from_y][from_x]
            if move.is_promote:
                piece = promote(piece)
            new_board[to_y][to_x] = piece
            new_board[from_y][from_x] = BLANK
            if oldp != BLANK:
                new_hands[pi].append(ptype2piece(player, unpromote(piece2ptype(oldp))))
                new_hands[pi].sort()
        return Position(fen='', tdata=(new_board, new_hands, -player, 0, self.nmoves + 1))
    def in_checkmate(self):
        player = self.side_to_move
        op = -player
        if not self.in_check(player):
            return False
        for m in self.plm(player):
            pos1 = self.apply_move(player, m)
            if not pos1.can_capture_op_king():
                return False
        return True            
    def legal_pawn_positions(self):
        # 二歩
        for x in range(5):
            if sum(self.board[y][x] == PAWN for y in range(5)) > 1:
                return False
            if sum(self.board[y][x] == -PAWN for y in range(5)) > 1:
                return False
        # 行きどころのない歩
        for x in range(5):
            if self.board[0][x] == PAWN:
                return False
            if self.board[4][x] == -PAWN:
               return False
        return True
    def can_capture_op_king(self):
        return self.in_check(-self.side_to_move)
    def __str__(self):
        return f'Position{(self.side_to_move, self.board, self.hands, self.check_count, self.nmoves)}'


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

