import os
import re
# Mリーグに関する関数集

'''
関数一覧
cdir(): カレントディレクトリを移動する
playerName(playerid): プレイヤーIDに対するプレイヤー名を返す
'''

# LAST YEAR (最新年)
LY = 2023

# カレントディレクトリを移動する関数
def cdir():
    # カレントディレクトリを移動
    new_directory = '/Users/hachijinkou/Documents/Python/MLEAGUE/'  # 移動先のフォルダ
    os.chdir(new_directory)  # 移動
    
playeridKey = {'10001': '園田賢', '10002': '村上淳', '10003': '鈴木たろう', '10004': '丸山奏子', '10005': '浅見真紀', '10006': '渡辺太',
                '20001': '二階堂亜樹', '20002': '滝沢和典', '20003': '勝又健志', '20004': '松ヶ瀬隆弥', '20005': '二階堂瑠美', 
                '25001': '内川幸太郎', '25002': '岡田紗佳', '25003': '沢崎誠', '25004': '堀慎吾', '25005': '渋川難波', 
                '30001': '佐々木寿人', '30002': '高宮まり', '30003': '前原雄大', '30004': '藤崎智', '30005': '伊達朱里紗', '30006': '滝沢和典', 
                '40001': '多井隆晴', '40002': '白鳥翔', '40003': '松本吉弘', '40004': '日向藍子', 
                '50001': '魚谷侑未', '50002': '近藤誠一', '50003': '茅森早香', '50004': '和久津晶', '50005': '東城りお', '50006': '醍醐大', 
                '60001': '萩原聖人', '60002': '瀬戸熊直樹', '60003': '黒沢咲', '60004': '本田朋広', 
                '65001': '猿川真寿', '65002': '菅原千瑛', '65003': '鈴木大介', '65004': '中田花奈', 
                '70001': '小林剛', '70002': '朝倉康心', '70003': '石橋伸洋', '70004': '瑞原明奈', '70005': '鈴木優', '70006': '仲林圭'
                }

# values[0] <= 参加年度 <= values[1]
entry = {'10001': (2018, LY), '10002': (2018, 2022), '10003': (2018, LY), '10004': (2019, 2022), '10005': (2023, LY), '10006': (2023, LY), 
         '20001': (2018, LY), '20002': (2018, 2020), '20003': (2018, LY), '20004': (2021, LY), '20005': (2021, LY),
         '25001': (2019, LY), '25002': (2019, LY), '25003': (2019, 2021), '25004': (2020, LY), '25005': (2022, LY),
         '30001': (2018, LY), '30002': (2018, LY), '30003': (2018, 2020), '30004': (2019, 2020), '30005': (2021, LY), '30006': (2021, LY),
         '40001': (2018, LY), '40002': (2018, LY), '40003': (2018, LY), '40004': (2019, LY), 
         '50001': (2018, LY), '50002': (2018, 2022), '50003': (2018, LY), '50004': (2019, 2020), '50005': (2021, LY), '50006': (2023, LY),
         '60001': (2018, LY), '60002': (2018, LY), '60003': (2018, LY), '60004': (2021, LY), 
         '65001': (2023, LY), '65002': (2023, LY), '65003': (2023, LY), '65004': (2023, LY), 
         '70001': (2018, LY), '70002': (2018, 2021), '70003': (2018, 2021), '70004': (2019, LY), '70005': (2022, LY), '70006': (2022, LY), 
}

# 各チームの参戦年度
t_entry = {'100': 2018, '200': 2018, '250': 2019, '300': 2018, '400': 2018, '500': 2018, '600': 2018, '650': 2023, '700': 2018}

teamidKey = {'100': '赤坂ドリブンズ', '200': 'EX風林火山', '250': 'KADOKAWAサクラナイツ', '300': 'KONAMI麻雀格闘倶楽部', '400': '渋谷ABEMAS', 
             '500': 'セガサミーフェニックス', '600': 'TEAM RAIDEN / 雷電', '650': 'BEAST Japanext', '700': 'U-NEXT Pirates'
        }

def playerid(pl_name, year=2023, idtype='str'):
    plid_key = {'園田 賢': 10001, '村上 淳': 10002, '鈴木 たろう': 10003, '丸山 奏子': 10004, '浅見 真紀': 10005, '渡辺 太': 10006, 
                '二階堂 亜樹': 20001, '勝又 健志': 20003, '松ヶ瀬 隆弥': 20004, '二階堂 瑠美': 20005,
                '内川 幸太郎': 25001, '岡田 紗佳': 25002, '沢崎 誠': 25003, '堀 慎吾': 25004, '渋川 難波': 25005, 
                '佐々木 寿人': 30001, '高宮 まり': 30002, '前原 雄大': 30003, '藤崎 智': 30004, '伊達 朱里紗': 30005, '滝沢 和典': 30006, 
                '多井 隆晴': 40001, '白鳥 翔': 40002, '松本 吉弘': 40003, '日向 藍子': 40004,
                '魚谷 侑未': 50001, '近藤 誠一': 50002, '茅森 早香': 50003, '和久津 晶': 50004, '東城 りお': 50005, '醍醐 大': 50006, 
                '萩原 聖人': 60001, '瀬戸熊 直樹': 60002, '黒沢 咲': 60003, '本田 朋広': 60004, 
                '猿川 真寿': 65001, '菅原 千瑛': 65002, '鈴木 大介': 65003, '中田 花奈': 65004, 
                '小林 剛': 70001, '朝倉 康心': 70002, '石橋 伸洋': 70003, '瑞原 明奈': 70004, '鈴木 優': 70005, '仲林 圭': 70006
                }
    # 名前に空白が入っていないときの処理
    if ' ' not in pl_name:
        for id, name in playeridKey.items():
            if name == pl_name:
                if id == '20002':
                    if year >= 2021:
                        id = '30006'
                return id
        return ValueError
    player_no = plid_key[pl_name]
    if player_no == 30006:
        if year < 2021:
            player_no = 20002
    if idtype=='int':
        return player_no
    else:
        return str(player_no)

# 選手IDに対する選手名を返す
def playerName(playerid: str):
    return playeridKey[playerid]

def teamid(playerid: str):
    return playerid[:3]

# チームIDに対するチーム名を返す
def teamName(teamid: str):
    return teamidKey[teamid]


# 与えられた年度における選手ID一覧を返す
def getPlayeridList(year):
    
    if year == 0:
        return list(playeridKey.keys())
    
    return_list = []

    for p_id in playeridKey:
        if year >= entry[p_id][0] and year <= entry[p_id][1]:
            return_list.append(p_id)
    return return_list

def getTeamidList(year):
    
    if year == 0:
        return list(teamidKey.keys())
    
    return_list = []
    
    for t_id in teamidKey:
        if year >= t_entry[t_id]:
            return_list.append(t_id)
    return return_list


# jsonに記録されている"seasonName"から区分No, 区分名を返す
def seasonString(seasonName):
    """
    seasonName (str): json_data['seasonName']
    """
    if 'レギュラーシーズン' in seasonName:
        return 0, 'レギュラーシーズン'
    elif 'セミファイナル' in seasonName:
        return 1, 'セミファイナルシリーズ'
    else:
        return 2, 'ファイナルシリーズ'

# 5桁の数字をYearとNoに分離する
def yearAndNumber(fiveNumber):
    """
    ・args
    fiveNumber (str): json_data['No]
    ・return
    year (int): 年
    number (int): 何戦目
    """
    year = int(fiveNumber[:2]) + 2000
    number = int(fiveNumber[2:])
    return year, number

def sharp(number, year=2023, seasonName='レギュラーシーズン'):
    if year == 2018 and seasonName == 'ファイナルシリーズ':
        # (number - 140) % 3 = (number + 1) % 3
        return 3 if (number+1) % 3 == 0 else (number+1) % 3
    else:
        return 2 if number % 2 == 0 else 1

# スコア, 着順から持ち点を逆算する
def pointFunc(score, rank):
    rankScore = {0: 50, 1: 10, 2: -10, 3: -30}
    
    if 1 not in rank:  # 同点トップが2人
        rankScore[0] = 30
    elif 2 not in rank:  # 同点2着が2人
        rankScore[1] = 0
    elif 3 not in rank:  # 同点3着が2人
        rankScore[2] = -20
    
    points = [round(int((float(score[i]) - rankScore[rank[i]])*1000),-2) + 30000 for i in range(4)]
    
    return points

# csvの行について指定したseasonNameと合致するか判定
def seasonNumberFunc(seasonNumber, seasonName):
    if seasonName == 'Regular':
        return seasonNumber == 0
    elif seasonName == 'Semi':
        return seasonNumber == 1
    elif seasonName == 'Final':
        return seasonNumber == 2
    elif seasonName == 'Post':
        return seasonNumber > 0
    elif seasonName == 'All':
        return True
    else:
        return False

start_id = {'18': 0, '19': 164, '20': 380, '21': 596, '22': 812, '23': 1046}
end_id = {'18': 164, '19': 380, '20': 596, '21': 812, '22': 1046, '23': 1308}

# 5桁の数字に対して対局IDを返す
def gameID(number: str) -> int:

    year, roundNum = number[:2], number[2:]
    
    return start_id[year] + int(roundNum)

# 対局IDから5桁の数字を求める
def fiveNumber(gameid: int):
    
    gameid = int(gameid)
    
    year, number = '00', '000'  # 初期化
    for key, value in end_id.items():
        if gameid <= value:
            year = key
            number = str(gameid - start_id[year]).zfill(3)
            break
    return year + number
    
# jsonファイルのファイル名から対局IDを返す
def gameID_from_filename(filename):
    # 5桁の数字をもとに対局IDを取得
    number = re.search(r'\d+', filename).group()
    return gameID(number)