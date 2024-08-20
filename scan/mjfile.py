# ファイル処理(主にjsonファイル)に関する関数集
import json
import os
import pandas as pd
import csv

# カレントディレクトリを移動する関数
def cdir():
    # カレントディレクトリを移動
    new_directory = '/Users/hachijinkou/Documents/Python/MLEAGUE/'  # 移動先のフォルダ
    os.chdir(new_directory)  # 移動

# jsonのファイル名を指定してjson型データを取得する
def openJson(filename):
    with open(filename, mode='rt', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

# フォルダ内のファイル全てのファイル名を取得
def get_files(folder_path):
    try:
        # フォルダ内の全ファイル名を取得
        file_names = os.listdir(folder_path)
        return sorted(file_names)
    except OSError as e:
        print(f"エラー: {e}")
        return []
    
# 二次元配列のデータをcsv保存
def writeCsv(data, o_filename, columns_index=None):
    if columns_index is None:
        columns_index = [str(i+1) for i in range(len(data[0]))]
    df = pd.DataFrame(data=data, columns=columns_index)
    df.to_csv(o_filename, index=False, encoding='utf-8')

# csvにデータを追加する
def add_data(data, o_filename):
    with open(o_filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# csvをソートする
def csv_sort(o_filename=None):
    sortid = {''}

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

# A0, B0, C0, D0 を 0,1,2,3に変換
def playerid(str_id):
    strid = {'A0': 0, 'B0': 1, 'C0': 2, 'D0': 3}
    return strid[str_id]

# kyokustartのargsから「東1局」などの文字列を求める
def kyokuName(args):
    kaze = '東' if args[4] == '1z' else '南'
    return kaze + str(playerid(args[1])+1) + '局'

def seatName(str_id, kyokuNum):
    seatNameKey = {0: '東家', 1: '南家', 2: '西家', 3: '北家'}
    seatNum = (playerid(str_id) - kyokuNum) % 4
    return seatNameKey[seatNum]

