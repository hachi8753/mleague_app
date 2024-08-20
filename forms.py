from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, IntegerField, PasswordField, DateField, 
    RadioField, SelectField, BooleanField, TextAreaField, 
    EmailField, SubmitField
)
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email

import json

# ==========================================================
# Formクラス
# ==========================================================


with open("json/mleague.json", mode="rt", encoding="utf-8") as f:
    mdata = json.load(f)

# ユーザー情報クラス
class InputForm(FlaskForm):
    
    # ID
    id = StringField("ID割り当て:", validators=[DataRequired('必須入力')], render_kw={"class": "input-text"})
    
    # 名前: 文字列入力
    name = StringField("氏名:", validators=[DataRequired('必須入力')], render_kw={"class": "input-text"})

    # チーム
    team = SelectField('チーム:', choices=[('', '')] + [(key, name) for key, name in mdata['teams'].items()], render_kw={"class": "select-box"}, default='')

    # 性別
    gender = RadioField('性別:', choices=[('Male', '男性'), ('Female', '女性')], render_kw={"class": "radio-button"}, default='Male')

    # 送信ボタン
    submit = SubmitField('登録', render_kw={"class": "button"})
    
class InputFormGame(FlaskForm):

    id = StringField("対局No")
    
    date = DateField("日付: ", format="%Y-%m-%d")
        
    point1 = IntegerField("持ち点: ")
    point2 = IntegerField("持ち点: ")
    point3 = IntegerField("持ち点: ")
    point4 = IntegerField("持ち点: ")
    
    player1 = SelectField('東家:')
    player2 = SelectField('南家:')
    player3 = SelectField('西家:')
    player4 = SelectField('北家:')
    
    # 送信ボタン
    submit = SubmitField('登録', render_kw={"class": "button-register"})
    
    def __init__(self, gameid, players, *args, **kwargs):
        super(InputFormGame, self).__init__(*args, **kwargs)
        self.id.data = gameid
        self.player1.choices = players
        self.player2.choices = players
        self.player3.choices = players
        self.player4.choices = players
    
    def validate(self):
        # 通常のバリデーションを実行
        if not super(InputFormGame, self).validate():
            return False
        
        # カスタムバリデーションを実行
        if self.point1.data + self.point2.data + self.point3.data + self.point4.data != 100000:
            self.point4.errors.append('合計が100000点ではありません')
            return False
        
        return True
        


class InputFormRegulation(FlaskForm):
    
    year = IntegerField("年: ", default=2018)
    regular = IntegerField("レギュラーシーズン: ")
    semi = IntegerField("セミファイナルシリーズ: ")
    final = IntegerField("ファイナルシリーズ: ")
    
    # 送信ボタン
    submit = SubmitField('登録', render_kw={"class": "button"})