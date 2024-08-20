from flask import Flask, Blueprint,  render_template, request, redirect, url_for

from forms import InputForm, InputFormGame, InputFormRegulation
from models import db, Player, Team, Game, GameDetail, PlayerHistory
from sqlalchemy.orm import joinedload, relationship


register_bp = Blueprint('register', __name__, url_prefix='/register')


# 登録：目次
@register_bp.route('/')
def index():
    return render_template('register/index.html')


# 選手登録
@register_bp.route('/player', methods=['GET', 'POST'])
def player():
    
    form = InputForm()
    # POST
    if request.method == "POST":
        # 入力値取得
        if form.validate_on_submit():
            id = 'P' + form.id.data
            name = form.name.data
            teamid = form.team.data
            gender = form.gender.data
            # インスタンス生成
            player = Player(id=id, name=name, teamid=teamid, gender=gender)
            print(player)
            # 登録
            try:
                db.session.add(player)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
            # 一覧へ
            return redirect(url_for('register.index'))
    # GET
    return render_template('register/player.html', form=form)

# 対局の記録フォーム
@register_bp.route('/game/<int:year>/<int:gameid>', methods=['GET', 'POST'])
def game(gameid, year):
    
    players_db = db.session.query(Player).options(joinedload(Player.history)).filter(
        Player.history.any(
            (PlayerHistory.entry_year <= year) &
            (PlayerHistory.leave_year.is_(None) | (PlayerHistory.leave_year >= year))
        )
    ).order_by(Player.id).all()
    
    players = [('', '')] + [(player.id, player.name) for player in players_db]
    
    form = InputFormGame(gameid=gameid ,players=players)
    # POST
    if request.method == "POST":
        # 入力値取得
        if form.validate():
            id = int(form.id.data)
            player_list = [
                form.player1.data, 
                form.player2.data, 
                form.player3.data, 
                form.player4.data
            ]
            point_list = [
                form.point1.data, 
                form.point2.data, 
                form.point3.data, 
                form.point4.data
            ]
            
            rank_list, score_list, same_list = get_result(point_list)
            
            # 対局テーブルを更新
            game_record = db.session.get(Game, id)
            if game_record:
                game_record.date = form.date.data
                game_record.check = True
            # 対局詳細テーブルを更新
            for i in range(4):
                result_record = db.session.get(GameDetail, (id-1)*4+(i+1))
                result_record.playerid = player_list[i]
                result_record.point = point_list[i]
                result_record.rank = rank_list[i]
                result_record.score = score_list[i]
                result_record.same_point = same_list[i]
            # 登録
            if form.submit.data:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error: {e}")
                return redirect(url_for('game.display', year=game_record.year))
            else:
                return render_template('register/game.html', form=form, gameid=id, year=game_record.year)
            # 一覧へ
            # 
            
    # GET
    return render_template('register/game.html', form=form, gameid=gameid, year=year)


@register_bp.route('/regulation', methods=['GET', 'POST'])
def regulation():
    
    form = InputFormRegulation()
    # POST
    if request.method == "POST":
        # 入力値取得
        if form.validate_on_submit():
            year = form.year.data
            regular = form.regular.data
            semi = form.semi.data
            final = form.final.data
            
            print('試合数登録: ', regular, semi, final)
            # データを登録する
            
            matches = {'Regular': regular, 'Semi': semi, 'Final': final}
            
            gameid = db.session.query(GameDetail).count() // 4
            round_number = 0
            for seasonName in ['Regular', 'Semi', 'Final']:
                for _ in range(matches[seasonName]):
                    gameid += 1
                    round_number += 1
                    if year == 2018 and seasonName == 'Final':
                        match_number = 3 if (round_number-140) % 3 == 0 else (round_number-140) % 3
                    else:
                        match_number = 2 if round_number % 2 == 0 else 1
                    
                    game = Game(id=gameid, year=year, round_number=round_number, seasonName=seasonName, match_number=match_number)
                    db.session.add(game)
                    for i in range(4):
                        game_detail = GameDetail(id=(gameid-1)*4+(i+1), gameid=gameid, position=i)
                        db.session.add(game_detail)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
            
            # 一覧へ
            return redirect(url_for('register.index'))
    # GET
    return render_template('register/regulation.html', form=form)


def get_result(point):
    rank_list = [1, 1, 1, 1]
    score_list = [0.0, 0.0, 0.0, 0.0]
    same_list = [0, 0, 0, 0]
    
    for i, p in enumerate(point):
        for j, q in enumerate(point):
            if i != j:
                if p < q:
                    rank_list[i] += 1
                elif p == q:
                    same_list[i] += 1
    
    for i, rank in enumerate(rank_list):
        rank_point = [50, 10, -10, -30]
        same_point = [30, 0, -20, 0]
        
        r_point = rank_point[rank-1] if same_list[i] == 0 else same_point[rank-1]
        score_list[i] = r_point + round((point[i]-30000)/1000 , 1)
    
    return rank_list, score_list, same_list