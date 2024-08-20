from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

# ==================================================
# モデル
# ==================================================


# 選手
class Player(db.Model):
    # テーブル名
    __tablename__ = 'players'
    
    # 選手ID
    id = db.Column(db.String(6), primary_key=True, nullable=False)
    # 選手名
    name = db.Column(db.String(20), nullable=False)
    # チームID
    teamid = db.Column(db.String(4), db.ForeignKey('teams.id'))
    # 性別
    gender = db.Column(db.String(6))
    
    # 所属団体
    organization = db.Column(db.String(12))
    # 生誕年
    birthyear = db.Column(db.Integer)
    # 誕生日 (XX月XX日の形式)
    birthday = db.Column(db.String(6))
    # 出身地
    hometown = db.Column(db.String(8))
    
    # リレーションシップ
    team = relationship('Team', back_populates="players")
    details = relationship("GameDetail", back_populates="player")
    history = relationship("PlayerHistory", back_populates="player")
    transfer = relationship("Transfer", foreign_keys='Transfer.old_playerid', back_populates="player")
    round_detail = relationship("RoundDetail", back_populates="player")
    
    def __str__(self):
        return f'{self.id}: {self.name}'
    
# チーム
class Team(db.Model):
    # テーブル名
    __tablename__ = 'teams'
    
    # チームID
    id = db.Column(db.String(4), primary_key=True, nullable=False)
    # チーム名
    name = db.Column(db.String(30), nullable=False)
    # オーナー
    owner_name = db.Column(db.String(30))
    
    color_code = db.Column(db.String(6))
    color_code_light = db.Column(db.String(6))
    
    # リレーションシップ
    players = relationship("Player", back_populates="team")
    
    def __str__(self):
        return f'{self.id}: {self.name}'

# 対局
class Game(db.Model):
    
    __tablename__ = 'games'
    
    # 対局ID
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    year = db.Column(db.Integer)
    round_number = db.Column(db.Integer)
    seasonName = db.Column(db.String(10))
    date = db.Column(db.Date)
    match_number = db.Column(db.Integer)
    check = db.Column(db.Boolean, default=False)
    
    details = relationship("GameDetail", back_populates="game")

# 対局詳細
class GameDetail(db.Model):
    __tablename__ = 'game_detail'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    gameid = db.Column(db.Integer, db.ForeignKey('games.id'))
    playerid = db.Column(db.String, db.ForeignKey('players.id'))
    point = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    score = db.Column(db.Numeric(5, 1))
    same_point = db.Column(db.Boolean, default=False)

    game = relationship('Game', back_populates="details")
    player = relationship('Player', back_populates="details")
    penalty = relationship('Penalty', back_populates="detail")

# 選手所属履歴
class PlayerHistory(db.Model):
    __tablename__ = 'player_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerid = db.Column(db.String, db.ForeignKey('players.id'))
    entry_year = db.Column(db.Integer)
    leave_year = db.Column(db.Integer)  # NULLの場合、まだ退団していない
    
    player = relationship('Player', back_populates=('history'))
    
    def __str__(self):
        return f'{self.playerid}: {self.entry_year} 〜 {"" if self.leave_year is None else self.leave_year}'

# リーグ戦詳細
class League(db.Model):
    __tablename__ = 'league'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer)
    seasonName = db.Column(db.String(20))
    # リーグ全体の試合数
    regular = db.Column(db.Integer)
    semi = db.Column(db.Integer)
    final = db.Column(db.Integer)
    # 各チームの試合数
    regular_each = db.Column(db.Integer)
    semi_each = db.Column(db.Integer)
    final_each = db.Column(db.Integer)

# チョンボ
class Penalty(db.Model):
    __tablename__ = 'penalty'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resultid = db.Column(db.Integer, db.ForeignKey('game_detail.id'))
    detail = relationship('GameDetail', back_populates='penalty')
    content = db.Column(db.String(10))

# 移籍履歴
class Transfer(db.Model):
    __tablename__ = 'transfer'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    old_playerid = db.Column(db.String(6), db.ForeignKey('players.id'))
    new_playerid = db.Column(db.String(6), db.ForeignKey('players.id'))
    
    player = relationship('Player', foreign_keys=[old_playerid], back_populates='transfer')
    new_player = relationship('Player', foreign_keys=[new_playerid], back_populates='transfer')
    
    
    def __str__(self):
        return f'{self.old_playerid} -> {self.new_playerid}'


# 局
class Round(db.Model):
    __tablename__ = 'rounds'
    
    id = db.Column(db.String(8), primary_key=True)
    gameid = db.Column(db.Integer, db.ForeignKey('games.id'))
    round_name = db.Column(db.String(7))
    kyoku = db.Column(db.Integer)
    honba = db.Column(db.Integer)
    kyotaku = db.Column(db.Integer)
    dora = db.Column(db.Text)
    
    round_details = relationship('RoundDetail', back_populates='round')
    logs = relationship('Log', back_populates='round')


# 局詳細
class RoundDetail(db.Model):
    __tablename__ = 'round_detail'
    
    round_id = db.Column(db.String(8), db.ForeignKey('rounds.id'), primary_key=True)
    player_index = db.Column(db.String(2), primary_key=True)
    position = db.Column(db.Integer)
    playerid = db.Column(db.String(6), db.ForeignKey('players.id'))
    point = db.Column(db.Integer)
    result = db.Column(db.Text)
    richi = db.Column(db.Boolean)
    meld_num = db.Column(db.Integer)
    tenpai = db.Column(db.Boolean)
    balance = db.Column(db.Integer)
    
    round = relationship('Round', back_populates='round_details')
    player = relationship('Player', back_populates='round_detail')
    win = relationship('Win', back_populates='round_detail')
    meld = relationship('Meld', back_populates='round_detail')

# ログ
class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    round_id = db.Column(db.String(8), db.ForeignKey('rounds.id'))
    log_id = db.Column(db.Integer)
    cmd = db.Column(db.Text)
    args = db.Column(db.Text)

    round = relationship('Round', back_populates='logs')


# 和了
class Win(db.Model):
    __tablename__ = 'wins'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    round_id = db.Column(db.String(8), db.ForeignKey('rounds.id'))
    player_index = db.Column(db.String(2), db.ForeignKey('round_detail.player_index'))
    
    type = db.Column(db.String(2))
    tenpai_type = db.Column(db.String(4))
    point = db.Column(db.Integer)
    score_name = db.Column(db.String(5))
    han = db.Column(db.Integer)
    fu = db.Column(db.Integer)
    yaku = db.Column(db.Text)
    dora = db.Column(db.Integer)
    aka = db.Column(db.Integer)
    ura = db.Column(db.Integer)
    tehai = db.Column(db.Text)
    win_pai = db.Column(db.String(2))
    deal_in = db.Column(db.String(6))
    
    round_detail = relationship('RoundDetail', back_populates='win')


# 副露
class Meld(db.Model):
    __tablename__ = 'melds'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    round_id = db.Column(db.String(8), db.ForeignKey('rounds.id'))
    player_index = db.Column(db.String(2), db.ForeignKey('round_detail.player_index'))
    
    turn = db.Column(db.Integer)
    dora_pai = db.Column(db.Text)
    type = db.Column(db.String(2))
    meld_pai = db.Column(db.String(2))
    meld_element = db.Column(db.Text)
    meld_num = db.Column(db.Integer)
    dahai = db.Column(db.String(2))
    tehai = db.Column(db.Text)  # 打牌後の手牌
    rinshan = db.Column(db.String(2))
    shanten_before = db.Column(db.Integer)
    shanten_after = db.Column(db.Integer)
    dora_num = db.Column(db.Integer)
    
    round_detail = relationship('RoundDetail', back_populates='meld')

# リーチ
class Richi(db.Model):
    __tablename__ = 'richis'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    round_id = db.Column(db.String(8), db.ForeignKey('rounds.id'))
    player_index = db.Column(db.String(2), db.ForeignKey('round_detail.player_index'))
    
    turn = db.Column(db.Integer)
    dora_pai = db.Column(db.Text)
    richi_pai = db.Column(db.String)
    sensei = db.Column(db.Integer)
    machi = db.Column(db.Text)
    tehai = db.Column(db.Text)
    deal_in = db.Column(db.Boolean)
    

# 画像
class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String)  # 'player', 'team', etc.
    year = db.Column(db.Integer)
    path = db.Column(db.String)
    foreign_id = db.Column(db.String)
    format = db.Column(db.String)  # 形式