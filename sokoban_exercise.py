"""第13回 倉庫番・演習版：完成デモを読み、別の構造へ処理を移植する。

演習の進め方
  ① TODO 1：WASDでプレイヤーを移動（範囲外に出さない）
  ② TODO 2：壁にぶつかると移動できないようにする
  ③ TODO 3：箱を押す処理を追加（壁や別の箱の手前では止まる）
"""

KEY_TO_VECTOR = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}

MAP_TEXT = [
    """#########
#       #
#  .    #
#  $    #
#  @    #
#       #
#########""",
    """##########
#        #
#  ..    #
#  $$    #
#   @    #
#        #
##########""",
    """###########
#         #
#         #
#    #    #
#    #    #
#  . # $  #
#      @  #
###########""",
]


def new_board(level_text):
    """ステージの文字列を読み、管理データを作る。引数：文字列。戻り値：辞書。"""
    rows = level_text.splitlines()
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("マップの横幅を揃えてください")
    board = {
        "size": (len(rows[0]), len(rows)),
        "solid": set(),
        "targets": set(),
        "crates": set(),
        "hero": None,
        "steps": 0,
        "past": [],
    }
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            p = (x, y)
            if ch == "#":
                board["solid"].add(p)
            if ch in ".+*":
                board["targets"].add(p)
            if ch in "$*":
                board["crates"].add(p)
            if ch in "@+":
                if board["hero"] is not None:
                    raise ValueError("プレイヤーは1人にしてください")
                board["hero"] = p
    if board["hero"] is None or not board["crates"] or len(board["crates"]) != len(board["targets"]):
        raise ValueError("プレイヤー1人、箱とゴールは同数にしてください")
    return board


def print_board(board):
    """現在の盤面を画面に表示する。引数：board。戻り値：なし。"""
    width, height = board["size"]
    print("\n" * 2 + "=== SOKOBAN : EXERCISE ===")
    print("# 壁  . ゴール  $ 箱  @ プレイヤー  * ゴール上の箱")
    for y in range(height):
        output = ""
        for x in range(width):
            p = (x, y)
            if p == board["hero"]:
                output += "+" if p in board["targets"] else "@"
            elif p in board["crates"]:
                output += "*" if p in board["targets"] else "$"
            elif p in board["solid"]:
                output += "#"
            elif p in board["targets"]:
                output += "."
            else:
                output += " "
        print(output)
    print(f"移動回数: {board['steps']} | WASD 移動 / U 戻す / R 再開 / Q 終了")


def in_field(board, point):
    """座標が盤面内か調べる。引数：board, (x,y)。戻り値：bool。"""
    x, y = point
    w, h = board["size"]
    return 0 <= x < w and 0 <= y < h


def next_position(origin, vector):
    """座標の足し算。引数：(x,y), (dx,dy)。戻り値：(x2,y2)。"""
    return (origin[0] + vector[0], origin[1] + vector[1])


def can_enter(board, destination):
    """TODO 2：壁判定。引数：board, 移動先座標。戻り値：移動可ならTrue。"""
    return in_field(board, destination) and destination not in board["solid"]


def push_crate(board, crate_position, vector):
    """TODO 3：箱を押す。引数：board, 箱座標, 移動方向。戻り値：押せたらTrue。"""
    next_crate_pos = next_position(crate_position, vector)
    if can_enter(board, next_crate_pos) and next_crate_pos not in board["crates"]:
        board["crates"].remove(crate_position)
        board["crates"].add(next_crate_pos)
        return True
    return False


def apply_move(board, direction_key):
    """TODO 1〜3：プレイヤーの移動。引数：board, WASDの1文字。戻り値：成功ならTrue。"""
    if direction_key not in KEY_TO_VECTOR:
        return False

    vector = KEY_TO_VECTOR[direction_key]
    next_hero_pos = next_position(board["hero"], vector)

    if not can_enter(board, next_hero_pos):
        return False

    prev_hero = board["hero"]
    prev_crates = board["crates"].copy()

    if next_hero_pos in board["crates"]:
        if not push_crate(board, next_hero_pos, vector):
            return False

    board["past"].append((prev_hero, prev_crates))
    board["hero"] = next_hero_pos
    board["steps"] += 1
    return True


def step_back(board):
    """Undoを実行。引数：board。戻り値：なし。"""
    if board["past"]:
        board["hero"], board["crates"] = board["past"].pop()
        board["steps"] -= 1


def completed(board):
    """すべての箱がゴール上にあるか調べる。引数：board。戻り値：bool。"""
    return board["crates"] == board["targets"]


def start():
    """キー入力・ステージ進行を管理する。戻り値：なし。"""
    index = 0
    board = new_board(MAP_TEXT[index])
    while True:
        print_board(board)
        if completed(board):
            print("ステージクリア！")
            index += 1
            if index == len(MAP_TEXT):
                print("全ステージクリア！")
                break
            input("Enterで次のステージへ...")
            board = new_board(MAP_TEXT[index])
            continue
        key = input("操作 > ").strip().lower()[:1]
        if key == "q":
            break
        if key == "r":
            board = new_board(MAP_TEXT[index])
        elif key == "u":
            step_back(board)
        else:
            apply_move(board, key)


if __name__ == "__main__":
    start()