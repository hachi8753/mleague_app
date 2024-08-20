# jsonファイルからの情報抽出を主に行うモジュール
import scan.mahjong_func as mj
import re
import scan.mleague as ml

zihai_str = zihai_str = {'1z': '東', '2z': '南', '3z': '西', '4z': '北', '5z': '白', '6z': '發', '7z': '中'}

# 麻雀の卓の情報をまとめる (一局ごと)
class MTable:
    """  次のように使う
    table = MTable()
    data = json_data['log'][0]  # 局のデータ
    for log in data:
        # logを読み込む
        table.read_log(log)
        
        ## 巡目ごとの処理 ##
        
    ## 終局時の処理 ##
        
    """
    
    def __init__(self):
        
        # 使用するかどうか要検討(読み込んだログを蓄積するためのリスト)
        self.data = []
        
        # ドラ表示牌
        self.dora = []
        self.ura = []
        
        self.kawa = {'A0': [], 'B0': [], 'C0': [], 'D0': []}
        self.tehai = {'A0': [], 'B0': [], 'C0': [], 'D0': []}
        self.meld = {'A0': [], 'B0': [], 'C0': [], 'D0': []}
        # 副露の牌だけ記録 (見た目枚数などの処理をしやすくするため)
        self.meld_pai = {'A0': [], 'B0': [], 'C0': [], 'D0': []}
        # リーチしているかどうか
        self.richi_flag = {'A0': 0, 'B0': 0, 'C0': 0, 'D0': 0}
        self.meld_count = {'A0': 0, 'B0': 0, 'C0': 0, 'D0': 0}
        
        # 巡目
        self.junme = 0
        # 副露のフラグ(前回のログが副露のログかどうか)
        self.meld_flag = 0
        # 親のインデックス(A0~D0のいずれか)
        self.oya = ''
        # 席(東家~北家のいずれか)
        self.seatName = {'A0': '', 'B0': '', 'C0': '', 'D0': ''}
        self.position = {'A0': 0, 'B0': 0, 'C0': 0, 'D0': 0}
        # シャンテン数
        self.shanten = {'A0': 0, 'B0': 0, 'C0': 0, 'D0': 0}
        # 局名 (東1局, 東1局1本場など)
        self.kyoku_name = ''
        
        self.kyoku_num = 0
        self.honba = None
        self.kyotaku = None
        
        # read_logで使う変数
        self.cmd = 'kyokustart'
        self.prev_index = 'A0'
        
        self.richi_and_deal_flag = ''
    
    # ログを読み込む
    def read_log(self, log):
        """
        次のログまで保持する情報
        最後にツモった牌    ->  self.tsumoPai
        直前のログの主体者  ->  self.prev_index
        直前のログのcmd    ->  self.cmd = cmd
        """
        
        cmd = log['cmd']
        p_index = log['args'][0] if len(log['args']) > 0 else ''
        self.p_index = p_index
        
        if cmd == 'tsumo':
            self.tsumoPai = log['args'][2]  # ツモ牌
            if self.richi_and_deal_flag != '':
                self.richi_and_deal_flag = ""
        elif cmd == 'sutehai':
            self.process_sutehai(log['args'], p_index)
        elif cmd == 'haipai':
            self.process_haipai(log['args'], p_index)
        elif cmd == 'say':
            self.process_say(log['args'], p_index)
        elif cmd == 'kyokustart':
            self.process_kyokustart(log['args'])
        elif cmd == 'open':
            self.process_open(log['args'], p_index)
        elif cmd == 'dora':
            self.dora.append(log['args'][1])
        
        # 1つ前のログの主体プレイヤーを記録しておく
        self.prev_index = p_index
        self.cmd = cmd
    
    #--------------------------- read_log()で使う関数 ---------------------------------------
    # 配牌ログの処理
    def process_haipai(self, args, p_index):
        for i in range(len(args[1])//2):
            self.tehai[p_index].append(args[1][0+2*i:2+2*i])  # 配牌をリストに追加
    
    # 捨て牌ログの処理
    def process_sutehai(self, args, p_index):
        if 'tsumogiri' not in args:
            # ツモ牌を手牌に追加
            if self.getLastCommand() == 'tsumo' or 'richi' in args:
                self.tehai[p_index].append(self.tsumoPai)
            # 捨て牌を手牌から削除
            if args[1] not in self.tehai[p_index]:
                print('ERROR: 手牌に含まれていない牌を打牌しようとしています！', self.tsumoPai)
            else:
                self.tehai[p_index].remove(args[1])
        # 河に捨て牌を追加
        self.kawa[p_index].append(args[1])
        # 巡目の加算
        if p_index == self.oya:
            self.junme += 1
    
    def process_say(self, args, p_index):
        # ポン、チー、カンの処理
        if args[1] == 'pon' or args[1] == 'chi' or args[1] == 'kan':
            # 副露のフラグを立てる
            self.meld_flag = 1
            # 直前に打牌した人のインデックス(A0~D0)
            self.d_index = self.prev_index
            # 親以外が鳴いたときの巡目の加算処理 (例)　西家が北家から鳴いたときは巡目+1
            if p_index != self.oya:
                if abcdNumber(p_index) < abcdNumber(self.prev_index):
                    self.junme += 1
        # リーチのフラグを立てる
        if 'richi' in args:
            self.richi_flag[p_index] = 1
            self.richi_flag_and_deal_flag = p_index
        elif 'ron' in args:  # リーチ宣言牌での放銃の時、「リーチをしていない」扱いになる
            if self.richi_and_deal_flag != "":
                self.richi_flag[self.richi_and_deal_flag] = 0
    
    def process_kyokustart(self, args):
        self.kyoku_name = kyokuName(args) + ('' if args[2] == '0' else args[2] + '本場')
        self.oya = args[1]  # 親のインデックス
        for key in self.seatName.keys():
            self.seatName[key] = getSeatName(abcdNumber(key) - abcdNumber(self.oya))  # 東家~北家をseatNameに格納
            self.position[key] = (abcdNumber(key) - abcdNumber(self.oya)) % 4
        self.kyoku_num = (0 if args[4] == '1z' else 4) + abcdNumber(self.oya)
        self.honba = int(args[2])
        self.kyotaku = int(args[3])
    
    def process_open(self, args, p_index):
        if self.meld_flag == 1:
            if '[' in args[1]:  # 加カンの処理
                self.tehai[p_index].append(self.tsumoPai)  # 直前にツモった牌
                self.tehai[p_index].remove(args[2])
                self.meld_pai[p_index].append(args[2])
                # ポンの記録を加カンの記録に上書きする
                for i, p_meld in enumerate(self.meld[p_index]):
                    if len(p_meld) > 1:  # 暗カンはlen()=1なのでエラーが起きてしまう
                        # 赤ドラの例外があるので'or'を使って2つの条件を使っている
                        if p_meld[1] == args[2] or p_meld[0][1:3] == args[2]:
                            self.meld[p_index][i] = [args[1], args[2], self.meld[p_index][i][2]]
            else:
                if '(' in args[1]:  # 暗カンのとき
                    # 直前にツモった牌を手牌リストに加える
                    self.tehai[p_index].append(self.tsumoPai)
                else:
                    self.meld_count[p_index] += 1
                for i in range(1, len(args[1])-1, 2):
                    try:
                        # 副露面子を手牌から削除
                        self.tehai[p_index].remove(args[1][i:2+i])
                    except Exception as e:
                        print(f'手牌リストからの削除: {e}')
                    self.meld_pai[p_index].append(args[1][i:2+i])  # 副露した牌を副露牌として記録
                if '(' in args[1]:  # 暗カンのとき
                    self.meld[p_index].append([args[1]])
                else:
                    self.meld[p_index].append([args[1], args[2], self.d_index])
                    self.meld_pai[p_index].append(args[2])
            self.meld_flag = 0  # 副露の処理が終わったのでフラグを0にもどす

    #--------------------------------------------------------------------------------------
    
    # 巡目を取得する
    def getJunme(self) -> int:
        return self.junme
        
    # 手牌を取得する
    def getTehai(self, p_index=None):
        for p_tehai in self.tehai.values():
            mj.ripai(p_tehai)
        if p_index is None:
            return self.tehai
        else:
            return self.tehai[p_index]
    
    # 手牌を文字列型で返す
    def getTehaiString(self, p_index, zihai=False) -> str:
        mj.ripai(self.tehai[p_index])
        tehai_string = ''
        zihai_str = mj.get_zihai_str()
        for pai in self.tehai[p_index]:
            if 'z' in pai and zihai:
                tehai_string += zihai_str[pai]
            else:
                tehai_string += pai
        return tehai_string
    
    # シャンテン数を取得する
    def getShanten(self, p_index) -> int:
        return mj.calcShanten(self.tehai[p_index])
    
    # 河を取得する
    def getKawa(self, p_index=None):
        if p_index is None:
            return self.kawa
        else:
            return self.kawa[p_index]
    
    # 副露のリストを取得する
    def getMeld(self, p_index=None):
        if p_index is None:
            return self.meld
        else:
            return self.meld[p_index]
    
    # 副露の牌を文字列で取得する
    def getMeldString(self, p_index, zihai=False):
        # 副露全体の文字列
        meld_string = ''
        for i, meld in enumerate(self.meld[p_index]):
            if '<' in meld[0]:
                dif = (abcdNumber(p_index) - abcdNumber(meld[2])) % 4
                if dif == 1:  # 上家から鳴いたとき
                    meld_str = f'<{meld[1]}>{meld[0][1:-1]}'
                elif dif == 2:  # 対面から鳴いたとき
                    meld_str = f'{meld[0][1:3]}<{meld[1]}>{meld[0][3:-1]}'
                elif dif == 3:  # 下家から鳴いたとき
                    meld_str = f'{meld[0][1:-1]}<{meld[1]}>'
            elif '(' in meld[0]:
                meld_str = meld[0]
            elif '[' in meld[0]:
                dif = (abcdNumber(p_index) - abcdNumber(meld[2])) % 4
                if dif == 1:  # 上家から鳴いたとき
                    meld_str = f'[{meld[1]}]{meld[0][1:-1]}'
                elif dif == 2:  # 対面から鳴いたとき
                    meld_str = f'{meld[0][1:3]}[{meld[1]}]{meld[0][3:-1]}'
                elif dif == 3:  # 下家から鳴いたとき
                    meld_str = f'{meld[0][1:-1]}[{meld[1]}]'
            meld_string += meld_str
            if i+1 < len(self.meld[p_index]):
                meld_string += '  '
        if zihai:
            zihai_str = mj.get_zihai_str()
            i = 0
            while i < len(meld_string):
                if meld_string[i] == 'z':
                    meld_string = meld_string[:i-1] + zihai_str[meld_string[i-1:i+1]] + meld_string[i+1:]
                    i = 0
                i += 1
        return meld_string
    
    # 手牌と副露を文字列型で取得する
    def getTehaiAndMeldString(self, p_index, zihai=False):
        meld_string = self.getMeldString(p_index, zihai)
        if len(meld_string) > 0:
            tehai_string = self.getTehaiString(p_index, zihai) + '  ' + meld_string
        else:
            tehai_string = self.getTehaiString(p_index, zihai)
        return tehai_string
    
    # ドラを文字列型で取得する
    def getDoraString(self, zihai=False):
        zihai_str = mj.get_zihai_str()
        dora_string = ''
        for pai in self.dora:
            if zihai and 'z' in pai:
                dora_string += zihai_str[pai]
            else:
                dora_string += pai
        return dora_string
    
    # 手牌・副露に含まれるドラの枚数を数える
    def countDora(self, p_index):
        tehai_string = self.getTehaiAndMeldString(p_index, False)
        return mj.getNumDora(self.dora, tehai_string)
    
    # 直前のログのコマンドを取得する
    def getLastCommand(self):
        return self.cmd

    # {0,1,2,3}を{'A0','B0',...}に変換する補助用メソッド
    def stringIndex(self, i):
        string_index_list = ['A0', 'B0', 'C0', 'D0']
        return string_index_list[i]

    # 局名を取得する
    def getKyokuName(self):
        return self.kyoku_name

    # 席の名前を取得する
    def getSeatName(self, p_index):
        return self.seatName[p_index]
    
    def printTableInfo(self):
        print(self.kyoku_name)
        print('ドラ', self.dora)
        
        def printDict(table_dict, ripai=False):
            for key, value in table_dict.items():
                if ripai:
                    mj.ripai(value)
                print(key, value)
        
        print('Tehai')
        printDict(self.tehai, True)
        print('Meld')
        printDict(self.meld)
        print('kawa')
        printDict(self.kawa)
    

# A0, B0, C0, D0 を 0,1,2,3に変換
def abcdNumber(str_id):
    strid = {'A0': 0, 'B0': 1, 'C0': 2, 'D0': 3}
    return strid[str_id]

# kyokustartのargsから「東1局」などの文字列を求める
def kyokuName(args):
    kaze = '東' if args[4] == '1z' else '南'
    return kaze + str(abcdNumber(args[1])+1) + '局'


# 和了役を出力する
def yakuName(args):
    # "agari"ログのargsを入力する
    dora = ["ドラ", "裏ドラ", "赤"]
    if 'ron' in args[0]:
        start = 5 if 'comment' in args[1] else 4
    else:
        start = 4 if 'comment' in args[0] else 3
    yaku_str = ""
    # "agari"ログは,役,飜,役,飜のような構造になっている
    for j in range(start, len(args), 2):
        yaku_str += args[j]
        if args[j] in dora:
            yaku_str += str(args[j+1])
        if j + 2 < len(args):
            yaku_str += " "
    return yaku_str

# 飜数を求める
def yakuHan(args):
    # "agari"ログを入力する
    if 'ron' in args[0]:
        start = 6 if 'comment' in args[1] else 5
    else:
        start = 5 if 'comment' in args[0] else 4
    han = 0
    # "agari"ログは,役,飜,役,飜のような構造になっている
    for j in range(start, len(args), 2):
        han += int(args[j])
    return han

# ドラの枚数を数える
def numberOfDora(args):
    dora = [0, 0, 0]
    for i, fig in enumerate(args):
        if fig == 'ドラ':
            dora[0] = int(args[i+1])
        elif fig == '赤':
            dora[1] = int(args[i+1])
        elif fig == '裏ドラ':
            dora[2] = int(args[i+1])
    return dora

# 日付を返す
def getDate(json_data):
    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2} \(.+?\))', json_data['dateTime'])
    if match:
        return match.group(1)
    else:
        return ''

# 開始時刻と終了時刻を返す
def getTime(json_data):
    # 正規表現パターン
    pattern = r'(\d{2}:\d{2})\s〜\s(\d{2}:\d{2})'
    match = re.search(pattern, json_data['dateTime'])
    if match:
        start_time = match.group(1)  # 開始時間
        end_time = match.group(2)
        return start_time, end_time
    else:
        return "-", "-"

# 0 -> 東家 といった変換を行う
def getSeatName(seatNum):
    number = seatNum % 4
    strIndex_key = {0: '東家', 1: '南家', 2: '西家', 3: '北家'}
    return strIndex_key[number]

# 対局ID, 年, ラウンド, 区分No, シーズンネーム, 日付, #, 
def getGameInfo(json_data, type='list'):
    game_dict = {}
    game_dict['対局ID'] = json_data['gameid']
    year, number = ml.yearAndNumber(json_data['No'])
    seasonNumber, seasonName = ml.seasonString(json_data['seasonName'])
    game_dict['年'] = year
    game_dict['ラウンド'] = number
    game_dict['区分No'] = seasonNumber
    game_dict['シーズンネーム'] = seasonName
    game_dict['日付'] = getDate(json_data)
    game_dict['#'] = '#' + str(ml.sharp(number, year, seasonName))
    
    if type=='list':
        return list(game_dict.values())
    elif type=='dict':
        return game_dict
    else:
        print('getGameInfo()のエラー: 戻り値はリスト型または辞書型を指定してください')
        return game_dict


def changeZihaiString(string):
    i = 0
    while i < len(string):
        if string[i] == 'z':
            string = string[:i-1] + zihai_str[string[i-1:i+1]] + string[i+1:]
            i = 0
        i += 1
    return string