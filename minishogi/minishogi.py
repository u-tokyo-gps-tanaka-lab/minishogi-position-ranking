#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
from enum import Enum, IntEnum

# # 55将棋を定義する
# 
# piece については，
# - piece は相手は負，promoteすると +8(相手駒は-8)
# - promoteしていない番号が小さい順
# - promoteしていない駒 < promoteしている駒
# - 自分の駒 < 相手の駒　でソートする．
# 
# 

# プレイヤの定義
class Player(Enum):
    WHITE = 0
    BLACK = 1
    def flip(self):
        return Player(1 - self.value)
WHITE = Player.WHITE
BLACK = Player.BLACK    

# 先手の陣地はy=0, 後手ならy=4
ZONE_Y_AXIS = {
    WHITE: 0,
    BLACK: 4
}
def player2c(player):
    return ['w', 'b'][player.value]
def can_promote_y(player, y):
    return y == ZONE_Y_AXIS[player]


# ## 駒と局面の定義

# In[ ]:
ptype_chars = '.krbgsp'
ptype_kchars = '　玉飛角金銀歩　　　竜馬　全と'
# piece
# 5 bit
# bit 4 - player (0: white, 1: black)
# bit 3 - is_promoted 
# bit 0-2 - base piece number
class Piece(IntEnum):
    BLANK = 0
    W_KING = 1 
    W_ROOK = 2 
    W_BISHOP = 3
    W_GOLD = 4 
    W_SILVER = 5 
    W_PAWN = 6 
    W_PROOK = 2 | 8
    W_PBISHOP = 3 | 8
    W_PSILVER = 5 | 8
    W_PPAWN = 6 | 8
    B_KING = 16 | 1 
    B_ROOK = 16 |2 
    B_BISHOP = 16 |3 
    B_GOLD = 16 |4 
    B_SILVER = 16 |5 
    B_PAWN = 16 |6 
    B_PROOK = 16 |2 | 8
    B_PBISHOP = 16 |3 | 8
    B_PSILVER = 16 |5 | 8
    B_PPAWN = 16 |6 | 8
    def is_promoted(self) -> bool:
        return self.value & 8 != 0
    def promote(self):
        return Piece(self.value | 8)
    def unpromote(self):
        return Piece(self.value & 0x17)
    def player(self):
        return Player(self.value >> 4)
    def ptype(self):
        return Ptype(self.value & 15)
    def fen(self):
        s = ptype_chars[self.value & 7]
        s = s if self.player() == BLACK else s.upper()
        s = ('+' if self.is_promoted() else '') + s
        return s
BLANK = Piece.BLANK
# ptype
class Ptype(IntEnum):
    BLANK = 0
    BASIC_MIN = 1
    KING = 1 # 相手は-1
    ROOK = 2 # 相手は-2
    BISHOP = 3 # 相手は-3
    GOLD = 4 # 相手は-4
    SILVER = 5 # 相手は-5
    PAWN = 6 # 相手は-6
    BASIC_MAX = 6
    PROOK = 2 | 8
    PBISHOP = 3 | 8
    PSILVER = 5 | 8
    PPAWN = 6 | 8
    def promote(self):
        return Ptype(self.value | 8)
    def unpromote(self):
        return Ptype(self.value & 7)
    def is_promoted(self) -> bool:
        return self.value & 8 != 0
    def to_piece(self, player):
        if self != Ptype.BLANK:
            return Piece(self.value + (player.value << 4))
        return Piece(0)
    # promote可能か?
    def can_promote(self):
        return not self.is_promoted() and self != KING and self != GOLD

# 成り駒: 自分なら+8、相手なら-8する
KING = Ptype.KING
ROOK = Ptype.ROOK
BISHOP = Ptype.BISHOP
GOLD = Ptype.GOLD
SILVER = Ptype.SILVER
PAWN = Ptype.PAWN
ptype_counts = {
    PAWN: 2,
    SILVER: 2,
    BISHOP: 2, 
    ROOK: 2,
    GOLD: 2,
    KING: 2
}
# piece type

def is_on_board(y, x):
    return 0 <= x < 5 and 0 <= y < 5

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
    ROOK.promote() : [NE, NW, SW, SE],
    BISHOP.promote() : [E, N, W, S],
}
for ptype in [SILVER, PAWN]:
    PTYPE_SHORT_DIRECTIONS[ptype.promote()] = PTYPE_SHORT_DIRECTIONS[GOLD]

PTYPE_LONG_DIRECTIONS: dict[int, list[tuple[int, int]]] = {
    ROOK : [N, S, E, W],
    BISHOP : [NE, NW, SW, SE],
}
for ptype in [ROOK, BISHOP]:
    PTYPE_LONG_DIRECTIONS[ptype.promote()] = PTYPE_LONG_DIRECTIONS[ptype]

PIECE_SHORT_DIRECTIONS: dict[int, list[tuple[int, int]]] = {}
PIECE_LONG_DIRECTIONS: dict[int, list[tuple[int, int]]] = {}
for ptype, ds in PTYPE_SHORT_DIRECTIONS.items():
    PIECE_SHORT_DIRECTIONS[ptype.to_piece(WHITE)] = ds
    PIECE_SHORT_DIRECTIONS[ptype.to_piece(BLACK)] = []
    for y, x in ds:
        PIECE_SHORT_DIRECTIONS[ptype.to_piece(BLACK)].append((-y, -x))
    if ptype in PTYPE_LONG_DIRECTIONS:
        lds = PTYPE_LONG_DIRECTIONS[ptype]      
    else:
        lds = []        
    PIECE_LONG_DIRECTIONS[ptype.to_piece(WHITE)] = lds
    PIECE_LONG_DIRECTIONS[ptype.to_piece(BLACK)] = []
    for y, x in lds:
        PIECE_LONG_DIRECTIONS[ptype.to_piece(BLACK)].append((-y, -x))    


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
        c = ptype_chars[Ptype(x)].upper()
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
    def make_drop_move(ptype, to_sq):
        return Move((Move.DROP_Y, ptype.value), to_sq, False)
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
    H = 5
    W = 5
    # 実際にはfenは2つ目以上のフィールドを省略できるが，ここでは4に決め打ちする
    def __init__(self, side_to_move, board, hands):
        self.side_to_move, self.board, self.hands = side_to_move, board, hands
    @classmethod
    def from_fen(cls, fen="rbsgk/4p/5/P4/KGSBR[-] w"):
        fen_parts = fen.split(' ')
        if len(fen_parts) != 2:
            raise 'fen format error'
        board = [[Piece(0)] * 5 for _ in range(5)] # board: 段ごとのリストで盤面を表現する
        sbstart = fen_parts[0].index('[')
        bstr = fen_parts[0][:sbstart]
        for y, l in enumerate(bstr.split('/')):
            x = 0
            lastplus = False
            for c in l:
                if c == '+':
                    lastplus = True
                elif c.isdigit():
                    x += int(c)
                else:
                    pt = Ptype(ptype_chars.index(c.lower()))
                    if lastplus:
                        pt = pt.promote()
                    if c.islower():
                        piece = pt.to_piece(BLACK)
                    else:
                        piece = pt.to_piece(WHITE)
                    board[y][x] = piece
                    x += 1
                    lastplus = False
        handstr = fen_parts[0][(sbstart + 1):-1]
        hands = [[] for _ in range(2)]
        for c in handstr:
            if c == '-':
                continue
            pt = Ptype(ptype_chars.index(c.lower()))
            if c.islower():
                hands[1].append(pt)
            else:
                hands[0].append(pt)
        for pi in range(2):
            hands[pi].sort()
        side_to_move = Player(0) if fen_parts[1] == 'w' else Player(1)
        return cls(side_to_move, board, hands)
    def to_tuple(self):
        board = tuple(tuple(l) for l in self.board)
        hands = tuple(tuple(l) for l in self.hands)
        return (self.side_to_move, board, hands)
    def __hash__(self):
        return hash(self.to_tuple())
    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()
    def __lt__(self, other): # to heap
    #    return True
        return self.to_tuple() < other.to_tuple()
    # 駒の数の合計数が正しいことを確認する．
    # 双方のkingが盤上にあることを確認する．
    def is_consistent(self):
        piececount = defaultdict(int)
        for y in range(5):
            for x in range(5):
                piececount[self.board[y][x]] += 1
        if piececount[KING.to_piece(WHITE)] != 1 or piececount[KING.to_piece(BLACK)] != 1:
            #print('type1')
            return False
        for pi in range(2):
            for ptype in self.hands[pi]:
                piececount[ptype.to_piece(Player(pi))] += 1
        #print(f'piececount={piececount}')
        basecount = defaultdict(int)     
        for piece, v in piececount.items():
            basecount[piece.ptype().unpromote()] += v
        
        for ptype in Ptype:
            if ptype != Ptype.BLANK and not ptype.is_promoted() and basecount[ptype] != 2:
                #print(f'type2, ptype={ptype}')
                return False
        return True            

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
                    line.append(piece.fen())
                    lastx = x
            if lastx < 4:
                line.append(str(5 - lastx - 1))
            b.append(''.join(line))
        b = '/'.join(b)
        hands = []
        for pi in range(2):
            self.hands[pi].sort()
            for ptype in self.hands[pi]:
                hands.append(ptype.to_piece(Player(pi)).fen())
        return f'{b}[{"".join(hands)}] {player2c(self.side_to_move)}'

    def can_move_on(self, player, y, x):
        p = self.board[y][x]
        return p == BLANK or player != p.player()

    # plm: pseudo legal moves
    # rook, bishop, promoted rook, promoted bishop
    def plm_piece(self, moves, player, ptype, y, x):
        #print(f'piece={ptype.to_piece(player)}, short_directions={PIECE_SHORT_DIRECTIONS[ptype.to_piece(player)]}')
        for dy, dx in PIECE_LONG_DIRECTIONS[ptype.to_piece(player)]:
            ny, nx = y + dy, x + dx
            while is_on_board(ny, nx): # これだとqueenの動きになってしまっている..
                # quiet
                if self.can_move_on(player, ny, nx):
                    moves.append(Move((y, x), (ny, nx), False))
                    if ptype.can_promote() and (can_promote_y(player, y) or can_promote_y(player, ny)):
                        moves.append(Move((y, x), (ny, nx), True))
                if self.board[ny][nx] != BLANK:
                    break
                ny += dy
                nx += dx
        for dy, dx in PIECE_SHORT_DIRECTIONS[ptype.to_piece(player)]:
            ny, nx = y + dy, x + dx
            if not is_on_board(ny, nx): continue
            if self.can_move_on(player, ny, nx):
                if not (ptype == PAWN and can_promote_y(player, ny)):
                    moves.append(Move((y, x), (ny, nx), False))
                if ptype.can_promote() and (can_promote_y(player, y) or can_promote_y(player, ny)):
                    moves.append(Move((y, x), (ny, nx), True))
    def all_drop_moves(self, moves, player):
        all_hand_ptype = set(self.hands[player.value])
        if len(all_hand_ptype) == 0:
            return
        for x in range(5):
            xpawncount = sum(self.board[y][x] == PAWN.to_piece(player) for y in range(5))
            for y in range(5):
                if self.board[y][x] != BLANK:
                    continue
                for pt in all_hand_ptype:
                    if not(pt == PAWN and (xpawncount == 1 or can_promote_y(player, y))):
                        moves.append(Move.make_drop_move(pt, (y, x)))

    def plm(self, player):
        moves = []
        for y in range(5):
            for x in range(5):
                piece = self.board[y][x]
                if piece != BLANK and piece.player() == player:
                    self.plm_piece(moves, player, piece.ptype(), y, x)
        self.all_drop_moves(moves, player)
        #print(f'moves={moves}')
        return moves
    def king_pos(self, player):
        kp = KING.to_piece(player)
        for y in range(5):
            for x in range(5):
                if self.board[y][x] == kp:
                    return (y, x)
        return (-1, -1)                
    def in_check(self, player):
        kingpos = self.king_pos(player)
        op = player.flip()
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
        if move.is_drop():
            ptype = Ptype(from_sq[1])
            drop_piece = ptype.to_piece(player)
            new_board[to_y][to_x] = drop_piece
            new_hands[player.value].remove(ptype)
        else:
            from_y, from_x = from_sq
            piece = self.board[from_y][from_x]
            if move.is_promote:
                piece = piece.promote()
            new_board[to_y][to_x] = piece
            new_board[from_y][from_x] = BLANK
            if oldp != BLANK:
                new_hands[player.value].append(oldp.ptype().unpromote())
                new_hands[player.value].sort()
        return Position(player.flip(), new_board, new_hands)
    def apply_unmove(self, player, move, oldpiece):
        assert self.side_to_move == player.flip()
        new_board = list(list(l) for l in self.board)
        new_hands = list(list(l) for l in self.hands)
        to_sq = move.to_sq
        to_y, to_x = to_sq
        piece = self.board[to_y][to_x]
        from_sq = move.from_sq
        if move.is_drop():
            ptype = Ptype(from_sq[1])
            drop_piece = ptype.to_piece(player)
            new_board[to_y][to_x] = BLANK
            new_hands[player.value].append(ptype)
            new_hands[player.value].sort()
        else:
            from_y, from_x = from_sq
            piece = self.board[to_y][to_x]
            if move.is_promote:
                piece = piece.unpromote()
            new_board[to_y][to_x] = oldpiece
            new_board[from_y][from_x] = piece
            if oldpiece != BLANK:
                oldptype = oldpiece.ptype()
                new_hands[player.value].remove(oldptype.unpromote())
        pos1 = Position(player, new_board, new_hands)
        assert pos1.is_consistent()
        #if not pos1.is_consistent():
        #    print(f'pos={self.fen()}, player={player}, move={move}, oldpiece={oldpiece}')
        return pos1

    # ## あるプレイヤが詰んでいるかどうか? -> 「直前の手が打ち歩詰め」を判定するためには必要 in_checkmate
    # checkmateであるための必要十分条件:
    # 1. 王手がかかっている
    # 2. 王手を回避する合法手がない
    # 
    # 合法手がないことはどう書けばいいか？
    # 1. 自分の駒を動かす
    # 2. 動かした後のposでin_checkを呼ぶ
    # 3. これを繰り返す途中で一度でもTrueが返ってきたら，その時点でreturn False
    def in_checkmate(self):
        player = self.side_to_move
        op = player.flip()
        #print(f'in_check={self.in_check(player)}')
        if not self.in_check(player):
            return False
        #print(f'plm={[m.to_uci() for m in self.plm(player)]}')
        for m in self.plm(player):
            pos1 = self.apply_move(player, m)
            #print(f'm={m.to_uci()}, pos1={pos1.fen()}')
            if not pos1.can_capture_op_king():
                return False
        return True            
    def legal_pawn_positions(self):
        # 二歩
        for x in range(5):
            if sum(self.board[y][x] == PAWN.to_piece(WHITE) for y in range(5)) > 1:
                return False
            if sum(self.board[y][x] == PAWN.to_piece(BLACK) for y in range(5)) > 1:
                return False
        # 行きどころのない歩
        for x in range(5):
            if self.board[0][x] == PAWN.to_piece(WHITE):
                return False
            if self.board[4][x] == PAWN.to_piece(BLACK):
               return False
        return True
    def can_capture_op_king(self):
        return self.in_check(self.side_to_move.flip())
    def illegal(self):
        return not self.legal_pawn_positions() or self.can_capture_op_king()
    def __str__(self):
        return f'Position{(self.side_to_move, self.board, self.hands)}'
# ## 一手前の局面をすべて作成する generate_previous_positions

def king_checkmate_pawn(pos: Position, y, x):
    assert pos.board[y][x].ptype() == PAWN
    player = pos.side_to_move.flip()
    dy, dx = PIECE_SHORT_DIRECTIONS[PAWN.to_piece(player)][0]
    ny, nx = y + dy, x + dx
    #print(f'ny, nx = {(ny, nx)}, player={player}')
    if not is_on_board(nx, ny) or pos.board[ny][nx] != KING.to_piece(player.flip()):
        return False
    return pos.in_checkmate()


def generate_previous_moves(pos: Position):
    player = pos.side_to_move
    opp = player.flip()
    moves = []
    for y in range(5):
        for x in range(5):
            piece = pos.board[y][x]
            if piece == BLANK or piece.player() != opp:
                continue
            ptype = piece.ptype()
            if not ptype.is_promoted() and ptype != KING:
                if ptype != PAWN or not king_checkmate_pawn(pos, y, x):
                    moves.append(Move.make_drop_move(piece.ptype(), (y, x)))
            for dy, dx in PIECE_LONG_DIRECTIONS[piece]:
                ny, nx = y - dy, x - dx
                while is_on_board(ny, nx) and pos.board[ny][nx] == BLANK:
                    moves.append(Move((ny, nx), (y, x), False))
                    if ptype.is_promoted() and (can_promote_y(opp, y) or can_promote_y(opp, ny)):
                        moves.append(Move((ny, nx), (y, x), True))
                    ny -= dy
                    nx -= dx
            for dy, dx in PIECE_SHORT_DIRECTIONS[piece]:
                ny, nx = y - dy, x - dx
                if not is_on_board(ny, nx) or pos.board[ny][nx] != BLANK: continue
                moves.append(Move((ny, nx), (y, x), False))
            if ptype.is_promoted():
                oldpiece = ptype.unpromote().to_piece(opp)
                for dy, dx in PIECE_SHORT_DIRECTIONS[oldpiece]:
                    ny, nx = y - dy, x - dx
                    if not is_on_board(ny, nx) or pos.board[ny][nx] != BLANK: continue
                    if can_promote_y(opp, y) or can_promote_y(opp, ny):
                        moves.append(Move((ny, nx), (y, x), True))
    return moves

def generate_previous_positions(pos: Position):
    ret = []
    moves = generate_previous_moves(pos)
    #print(f'moves={moves}')
    player = pos.side_to_move.flip()
    hands = set(pos.hands[player.value] + [Ptype.BLANK])
    for m in moves:
        if m.is_drop():
            pos1 = pos.apply_unmove(player, m, Ptype.BLANK)
            if not pos1.illegal():
                ret.append(pos1)
        else:
            for ptype in hands:
                pos1 = pos.apply_unmove(player, m, ptype.to_piece(player.flip()))
                if not pos1.illegal():
                    ret.append(pos1)
                if ptype != Ptype.BLANK and ptype.can_promote():
                    pos1 = pos.apply_unmove(player, m, ptype.promote().to_piece(player.flip()))
                    if not pos1.illegal():
                        ret.append(pos1)
                
    return ret                    
