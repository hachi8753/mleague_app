# カレントディレクトリ移動
import os
from scan.record import get_record
import scan.mjfile as mf


try:
    os.chdir('C:/Users/hachi/iCloudDrive/Documents/Flask/mleague_app/')  # Windows
except:
    os.chdir('/Users/hachijinkou/Documents/Flask/mleague_app/')  # Mac

from flask import Flask, render_template
from flask_migrate import Migrate
from models import db


from blueprints.game import game_bp
from blueprints.player import player_bp
from blueprints.result import result_bp
from blueprints.register import register_bp


# ==================================================
# Flask
# ==================================================
app = Flask(__name__)
# 設定ファイル読み込み
app.config.from_object("config.Config")

# dbとFlaskとの紐づけ
db.init_app(app)
# マイグレーションとの紐づけ（Flaskとdb）
migrate = Migrate(app, db)

app.register_blueprint(game_bp)
app.register_blueprint(player_bp)
app.register_blueprint(result_bp)
app.register_blueprint(register_bp)


@app.route('/')
def index():
    return render_template('index.html')


from models import Round, RoundDetail, Log, Win, Meld, Richi

def record():
    
    with app.app_context():
        
        if False:
            db.session.query(Round).delete()
            db.session.query(RoundDetail).delete()
            db.session.query(Log).delete()
            db.session.query(Meld).delete()
            db.session.query(Win).delete()
            db.session.query(Richi).delete()
            db.session.commit()
        
        
        file_list = mf.get_files('jsons/')
        for i, file in enumerate(file_list):
            
            if i % 50 == 20:
                print(file)
                
            
            if '.json' in file:
                filename = os.path.join('jsons/', file)
                
                records = get_record(filename)
                
                """
                for round_data in records['Round']:
                    db.session.add(round_data)
                for round_detail in records['RoundDetail']:
                    db.session.add(round_detail)
                for log_data in records['Log']:
                    db.session.add(log_data)
                
                for meld_data in records['Meld']:
                    db.session.add(meld_data)
                """
                for win_data in records['Win']:
                    db.session.add(win_data)
                for richi_data in records['Richi']:
                    db.session.add(richi_data)
                

        db.session.commit()
    
    return



# ==================================================
# 実行
# ==================================================
if __name__ == "__main__":
    
    #record()
    app.run(host='0.0.0.0', port=5001)
