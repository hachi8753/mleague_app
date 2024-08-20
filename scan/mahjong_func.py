# 麻雀に関する関数集

from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter

class JudgeTehai:
    
    def __init__(self, tehai: list):
        self.tehai = tehai
    
    def calcShanten(self):
        pai_str = ['', '', '', '']
    
        for pai in self.tehai:
            if 'm' in pai or 'M' in pai:
                pai_str[0] += pai[0]
            elif 'p' in pai or 'P' in pai:
                pai_str[1] += pai[0]
            elif 's' in pai or 'S' in pai:
                pai_str[2] += pai[0]
            else:
                pai_str[3] += pai[0]
        
        shanten = Shanten()
        tiles = TilesConverter.string_to_34_array(man=pai_str[0], pin=pai_str[1], sou=pai_str[2], honors=pai_str[3])
        result = shanten.calculate_shanten(tiles)
        
        return result


# シャンテン数を計算
def calcShanten(tehai) -> int:
    pai_str = ['', '', '', '']
    
    for pai in tehai:
        if len(pai) == 0:
            continue
        if 'm' in pai or 'M' in pai:
            pai_str[0] += pai[0]
        elif 'p' in pai or 'P' in pai:
            pai_str[1] += pai[0]
        elif 's' in pai or 'S' in pai:
            pai_str[2] += pai[0]
        else:
            pai_str[3] += pai[0]
    
    shanten = Shanten()
    tiles = TilesConverter.string_to_34_array(man=pai_str[0], pin=pai_str[1], sou=pai_str[2], honors=pai_str[3])
    result = shanten.calculate_shanten(tiles)
    
    return result

def machi(tehai, options='list'):
    pai_list = paiList(1)[:-3]
    if options=='str':
        machi_list = ""
    else:
        machi_list = []
    if calcShanten(tehai) > 0 or len(tehai)%3 != 1:
        return [] if options=='list' else ""
    for pai in pai_list:
        if calcShanten(tehai+[pai]) < 0:
            if options=='str':
                machi_list += pai
            else:
                machi_list.append(pai)
    return machi_list

# 満貫以上の和了点を返す
def agariScoreMangan(mangan, seatNumber):
    # mangan は'満貫', '役満'のような文字列
    
    # 和了点の辞書
    score_dict = {'満貫': (12000, 8000), '跳満': (18000, 12000), '倍満': (24000, 16000), 
                  '三倍満': (36000, 24000), '役満': (48000, 32000)}
    
    # 親ならば0, 子は1
    seatkey = 0 if seatNumber == 0 else 1
    
    return score_dict[mangan][seatkey]

# 4飜以下の和了点を返す
def agariScore(han, fu, tsumo: str, seatNumber):
    
    # 例外処理
    if han > 4:
        print('ERROR: 5飜以上の入力は禁止')
        return 0
    
    #               25    30   40    50    60    70    80    90    100   110
    score_list = [[[0,    1500, 2000, 2400, 2900, 3400, 3900, 4400, 4800, 5300], 
                    [2400, 2900, 3900, 4800, 5800, 6800, 7700, 8700, 9600, 10600], 
                    [4800, 5800, 7700, 9600], 
                    [9600]  # 親_ロン
                    ], 
                    [[0,    1000, 1300, 1600, 2000, 2300, 2600, 2900, 3200, 3600], 
                    [1600, 2000, 2600, 3200, 3900, 4500, 5200, 5800, 6400, 7100], 
                    [3200, 3900, 5200, 6400], 
                    [6400]], # 子_ロン
    #                20      25    30    40    50    60    70    80    90    100   110
                    [[0,    0,    1500, 2100, 2400, 3000, 3600, 3900, 4500, 4800, 5400], 
                    [2100, 0,    3000, 3900, 4800, 6000, 6900, 7800, 8700, 9600, 10800], 
                    [3900, 4800, 6000, 7800, 9600], 
                    [7800, 9600]  # 親_ツモ
                    ],
                    [[0,    0,    1100, 1500, 1600, 2000, 2400, 2700, 3100, 3200, 3600], 
                    [1500, 0,    2000, 2700, 3200, 4000, 4700, 5200, 5900, 6400, 7200], 
                    [2700, 3200, 4000, 5200, 6400], 
                    [5200, 6400]  # 子_ツモ
                    ]]
        
    seatKey = 0 if seatNumber == 0 else 1
    
    # ロンツモと符によるindex
    if tsumo == 'ロン':
        list_index = seatKey
        fu_index = 0 if fu == 25 else fu//10 - 2
    else:
        list_index = seatKey + 2
        fu_index = int(fu==25) if fu < 30 else fu//10 - 1
    

    if len(score_list[list_index][han-1]) <= fu_index:  # リストに点数がないときは満貫
        return 12000 if seatKey == 0 else 8000
    else:
        return score_list[list_index][han-1][fu_index]

# 理牌 (萬子, 筒子, 索子, 字牌の順)
def ripai(tehai: list):
    tehai.sort(key=paiNum)

# 理牌用の関数
def paiNum(pai):
    pai_key = {'m': 0, 'p': 100, 's': 200, 'z': 300}
    if 'M' in pai:
        num = 55
    elif 'P' in pai:
        num = 155
    elif 'S' in pai:
        num = 255
    else:
        if len(pai) < 2:
            print('ERROR: 牌が記録されていません')
            return 0
        num = int(pai[0])*10 + pai_key[pai[1]]
        
    return num

def seatName(seatNumber):
    seatNameDict = {0: '東家', 1: '南家', 2: '西家', 3: '北家'}
    return seatNameDict[seatNumber]

def paiList(str_option=1):
    pai_list = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', 
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', 
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 
                '東', '南', '西', '北', '白', '發', '中', 
                '5M', '5P', '5S']
    pai_list_json = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', 
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', 
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 
                '1z', '2z', '3z', '4z', '5z', '6z', '7z', 
                '5M', '5P', '5S']
    if str_option == 1:
        return pai_list_json
    else:    
        return pai_list


yaku_list = ['門前自摸','リーチ', 'タンヤオ', '一盃口', '平和', '東', '南', '西', '北', '白', '発', '中',
             '一発', '槍槓', '嶺上開花', '海底摸月', '河底撈魚', 'チャンタ', '一気通貫', '三色同順', 'ダブルリーチ', 
             '七対子', '対々和', '三暗刻', '三色同刻', '三槓子', '小三元', '混老頭', '純チャン', '混一色', '二盃口', 
             '清一色', '天和', '地和', '大三元', '四暗刻', '字一色', '緑一色', '清老頭', '国士無双', '小四喜', '四槓子', '九蓮宝燈']


def getYakuList():
    return yaku_list


def doraPai(pai):
    if len(pai) != 2:
        return 'DORA_ERROR'
    if 'z' in pai:
        return str((int(pai[0]))%7+1) + 'z'
    else:
        return str((int(pai[0]))%9+1) + pai[1]

# ドラ表示牌のリストと牌の文字列(例:"1m1m1m <6z>6z6z")からドラの枚数
def getNumDora(dora_list: list, string) -> int:
    
    dora = [doraPai(pai) for pai in dora_list]
    
    if '5m' in dora:
        dora.append('5S')
    elif '5p' in dora:
        dora.append('5P')
    elif '5s' in dora:
        dora.append('5S')
        
    num_dora = 0
    
    # ドラのカウント
    for pai in dora:
        num_dora += string.count(pai)
    # 赤ドラのカウント
    for s in ['M', 'P', 'S']:
        if s in string:
            num_dora += 1
    
    return num_dora

def calculate_condition():
    return

def get_zihai_str():
    return {'1z': '東', '2z': '南', '3z': '西', '4z': '北', '5z': '白', '6z': '發', '7z': '中'}