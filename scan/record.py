import scan.mjfile as mf
import scan.mjargs as ma
import scan.mahjong_func as mj
import scan.mleague as ml

from models import Round, RoundDetail, Log, Win, Meld, Richi

class RecordTable(ma.MTable):
    
    def __init__(self):
        super().__init__()
        
        index_list = ['A0', 'B0', 'C0', 'D0']
        
        self.point = {idx: 0 for idx in index_list}
        self.balance = {idx: 0 for idx in index_list}
        self.result = {idx: 0 for idx in index_list}
        self.tenpai = {idx: 0 for idx in index_list}
        self.a_index = ''
        self.d_index = ''
        self.win_type = ''
        
        self.win = {}
        
        self.point_flag = 0
        
        self.process_flag = 0
        #self.json_data = json_data
        
        self.meld_len = {'A0': 0, 'B0': 0, 'C0': 0, 'D0': 0}
        
        self.meld_datas = []
        self.richi_datas = []
        self.richi_success_flag = False
        

    def read_log(self, log):
        # このlogで副露の処理が完了したかどうかをprocess_flagで管理する
        if self.meld_flag == 1:
            self.prev_shanten = self.getShanten(self.p_index)
            self.process_flag = 1
        
        if self.richi_success_flag:
            if log['cmd'] == 'sutehai':
                # リーチ宣言牌と、(宣言牌による放銃)をリストに追加
                # のちに、リーチが成立していたら(cmd='richi'が存在したら)、放銃をFalseに変更する
                self.richi_data += [log['args'][1]]
            else:
                p_index = log['args'][0] if len(log['args']) > 0 else None
                self.richi_data += [mj.machi(self.getTehai(p_index), options='str'), self.getTehaiAndMeldString(p_index)]
                if log['cmd'] == 'richi':
                    self.richi_data += [False]
                    self.richi_datas.append(self.richi_data)
                    self.richi_success_flag = False
                else:  # リーチ宣言牌で放銃したとき
                    self.richi_data += [True]
                    self.richi_datas.append(self.richi_data)
                    self.richi_success_flag = False
            
        try:
            super().read_log(log)
        except:
            pass
        
        p_index = log['args'][0] if len(log['args']) > 0 else None
        if log['cmd'] == 'point':
            if self.point_flag < 4:
                self.point[p_index] = log['args'][1][1:]
                self.point_flag += 1
            else:
                self.balance[p_index] = log['args'][1]
        elif log['cmd'] == 'agari':
            if 'ron' in log['args'][0]:
                self.win_type = 'ロン'
                self.agariPai = log['args'][0][4:]
                if 'comment' in log['args'][1]:
                    z = 2  # ずれ
                else:
                    z = 1
            else:
                self.win_type = 'ツモ'
                self.agariPai = self.tsumoPai
                if 'comment' in log['args'][0]:
                    z = 1
                else:
                    z = 0
            a_index = log['args'][0 + z]
            self.a_index = a_index
            
            self.win['han'] = ma.yakuHan(log['args'])
            self.win['fu'] = int(log['args'][2+z])
            self.win['yaku'] = ma.yakuName(log['args'])
            # 和了点の計算
            if log['args'][1+z] in ['満貫', '跳満', '倍満', '三倍満', '役満']:
                self.win['point'] = mj.agariScoreMangan(log['args'][1+z], (ma.abcdNumber(self.a_index)-ma.abcdNumber(self.oya))%4) 
                self.win['score_name'] = log['args'][1+z]
            else:
                self.win['point'] = mj.agariScore(self.win['han'], self.win['fu'], self.win_type, (ma.abcdNumber(self.a_index)-ma.abcdNumber(self.oya))%4)
                self.win['score_name'] = str(self.win['han']) + '飜' + str(self.win['fu']) + '符'
            self.win['dora'] = ma.numberOfDora(log['args'])
            self.win['deal-in'] = self.d_index if self.win_type == 'ロン' else None
            
                    
        elif log['cmd'] == 'sutehai':
            self.d_index = p_index
        elif log['cmd'] == 'say':
            if log['args'][1] == 'tenpai':
                self.tenpai[p_index] = True
            elif log['args'][1] == 'noten':
                self.tenpai[p_index] = False
            
        
        if log['cmd'] == 'say':
            #print(log)
            # リーチのデータ
            if log['args'][1] == 'richi':
                
                
                # player_index, 巡目, ドラ表示牌, 先にリーチしている人の人数
                # 待ち, 手牌
                self.richi_data = [p_index, self.getJunme(), self.getDoraString(), sum(self.richi_flag.values())-1]
                self.richi_success_flag = True
        

        
        if log['cmd'] == 'say':
            self.say = log['args'][1]
        
        # meld_flagが0になった瞬間 = 副露の処理が終わった瞬間
        # このタイミングで、副露のデータを追加していく
        if self.process_flag == 1 and self.meld_flag == 0:
            
            p = self.p_index
            
            # 副露のリストの要素数が変わっていないときは, 加カンが行われた時
            if len(self.meld[p]) == self.meld_len[p]:
                meld_type = '加カン'
            else:
                # 目的の副露のリスト
                e_meld = self.meld[p][-1]
                
                if self.say == 'chi':
                    meld_type = 'チー'
                elif self.say == 'pon':
                    meld_type = 'ポン'
                elif self.say == 'kan':
                    meld_type = 'カン'
                
                if len(e_meld) == 1:
                    meld_type = '暗カン'
                
                self.meld_len[p] += 1
            
            
            # このプログラムではチー、ポン、大明カンのみを抽出する
            if meld_type != '加カン' and meld_type != '暗カン':
                
                dif = (ma.abcdNumber(self.p_index) - ma.abcdNumber(e_meld[2])) % 4
                if dif == 1:  # 上家から鳴いたとき
                    meld_str = f'<{e_meld[1]}>{e_meld[0][1:-1]}'
                elif dif == 2:  # 対面から鳴いたとき
                    meld_str = f'{e_meld[0][1:3]}<{e_meld[1]}>{e_meld[0][3:-1]}'
                elif dif == 3:  # 下家から鳴いたとき
                    meld_str = f'{e_meld[0][1:-1]}<{e_meld[1]}>'
                
                
                dahai = e_meld[1]
                self.prev_tehai = self.getTehaiAndMeldString(p)
                
                self.meld_data = [p, self.getJunme(), self.getDoraString(), meld_type, dahai, meld_str, self.meld_len[p]]
                #print(self.meld_data)
                
                if meld_type == 'カン':
                    self.process_flag = 3
                    self.prev_shanten = self.getShanten(p)
                else:
                    self.process_flag = 2
            else:
                self.process_flag = 0
        
        elif self.process_flag == 2:
            if log['cmd'] == 'sutehai':
                # 打牌 シャンテン 手牌 リンシャン シャンテン数の変化 ドラの枚数
                dahai = log['args'][1]
                shanten = self.getShanten(self.p_index)
                tehai = self.getTehaiAndMeldString(self.p_index)
                self.meld_data += [dahai, tehai, None, self.prev_shanten, shanten, self.countDora(self.p_index)]
                self.meld_datas.append(self.meld_data)  # データの追加
                self.process_flag = 0
        elif self.process_flag == 3:
            if log['cmd'] == 'tsumo':
                # 打牌 シャンテン 手牌  リンシャン シャンテン数の変化 ドラの枚数
                rinshan = log['args'][2]
                self.meld_data += [None, self.prev_tehai, rinshan, self.prev_shanten, None, self.countDora(self.p_index)]
                self.meld_datas.append(self.meld_data)  # データの追加
                self.process_flag = 0


def get_record(filename):
    
    
    r_data = {
        'Round': [], 
        'RoundDetail': [], 
        'Log': [], 
        'Win': [], 
        'Meld': [], 
        'Richi': []
    }
    
    json_data = mf.openJson(filename)
    
    data = json_data['log']          
    gameid = ml.gameID(json_data['No'])
    index_list = ['A0', 'B0', 'C0', 'D0']
    playerid_list = {p_index: 'P' + ml.playerid(json_data['player'][p_index], year=2000+int(json_data['No'][:2])) for p_index in index_list}
    
    for i in range(len(data)):
        
        table = RecordTable()
        round_id = 'R' + str(gameid).zfill(5) + str(i).zfill(2)
        
        for j, log in enumerate(data[i]):
            try:
                table.read_log(log)
            except Exception as e:
                print(e)
            
            log_data = Log(
                round_id = round_id, 
                log_id = j, 
                cmd = log['cmd'],
                args = str(log['args'])
            )
            r_data['Log'].append(log_data)
        
        for p_index in index_list:
            if table.win_type == 'ツモ':
                if table.a_index == p_index:
                    table.result[p_index] = '和了'
                else:
                    table.result[p_index] = '被ツモ'
            elif table.win_type == 'ロン':
                if table.a_index == p_index:
                    table.result[p_index] = '和了'
                elif table.d_index == p_index:
                    table.result[p_index] = '放銃'
                else:
                    table.result[p_index] = '横移動'
            else:
                table.result[p_index] = '流局'
        
        round_data = Round(
            id = round_id, 
            gameid = gameid, 
            round_name = table.kyoku_name, 
            kyoku = table.kyoku_num, 
            honba = table.honba,
            kyotaku = table.kyotaku,
            dora = ''.join(table.dora)
        )
        r_data['Round'].append(round_data)
        
        for j, p_index in enumerate(index_list):
            round_detail = RoundDetail(
                round_id = round_id,
                player_index = p_index,
                position = table.position[p_index], 
                playerid = playerid_list[p_index], 
                point = table.point[p_index], 
                result = table.result[p_index], 
                richi = bool(table.richi_flag[p_index]), 
                meld_num = table.meld_count[p_index], 
                tenpai = bool(table.tenpai[p_index]), 
                balance = table.balance[p_index]
            )
            r_data['RoundDetail'].append(round_detail)
        
        if table.result['A0'] != '流局':
            win_data = Win(
                round_id = round_id, 
                player_index = table.a_index, 
                type = table.win_type, 
                tenpai_type = 'リーチ' if 'リーチ' in table.win['yaku'] else ('副露' if table.meld_count[table.a_index] > 0 else 'ヤミテン'), 
                point = table.win['point'], 
                score_name = table.win['score_name'], 
                han = table.win['han'], 
                fu = table.win['fu'], 
                yaku = table.win['yaku'], 
                dora = table.win['dora'][0], 
                aka = table.win['dora'][1], 
                ura = table.win['dora'][2], 
                tehai = table.getTehaiAndMeldString(table.a_index), 
                win_pai = table.agariPai, 
                deal_in = table.win['deal-in']
            )
            r_data['Win'].append(win_data)
        
        for me in table.meld_datas:
            meld = Meld(
                round_id = round_id, 
                player_index = me[0], 
                turn = me[1], 
                dora_pai = me[2], 
                type = me[3], 
                meld_pai = me[4], 
                meld_element = me[5], 
                meld_num = me[6], 
                dahai = me[7], 
                tehai = me[8], 
                rinshan = me[9], 
                shanten_before = me[10], 
                shanten_after = me[11],
                dora_num = me[12]
            )
            r_data['Meld'].append(meld)
        for ri in table.richi_datas:
            richi = Richi(
                round_id = round_id, 
                player_index = ri[0], 
                turn = ri[1], 
                dora_pai = ri[2], 
                richi_pai = ri[4], 
                sensei = ri[3], 
                machi = ri[5], 
                tehai = ri[6], 
                deal_in = bool(ri[7])
            )
            r_data['Richi'].append(richi)
    return r_data
