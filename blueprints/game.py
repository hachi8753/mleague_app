from flask import Flask, Blueprint,  render_template, request, redirect, url_for

from forms import InputForm, InputFormGame, InputFormRegulation
from models import db, Player, Team, Game, GameDetail, PlayerHistory
from models import Round, RoundDetail, Log, Win, Meld
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy import and_, func, case

from pprint import pprint

game_bp = Blueprint('game', __name__, url_prefix='/game')


@game_bp.route('/')
def index():
    return render_template('game/index.html')


# 年別の対局一覧
@game_bp.route('/<int:year>')
def display(year):
    games = db.session.query(Game).filter_by(year=year).options(joinedload(Game.details).joinedload(GameDetail.player)).all()
    for game in games:
        game.details = sorted(game.details, key=lambda detail: detail.id)
    return render_template('game/display.html', games=games, year=year)

@game_bp.route('/detail/<int:gameid>')
def detail(gameid):
    game = db.session.query(Game).options(joinedload(Game.details).joinedload(GameDetail.player)).filter_by(id=gameid).first()
    
    rounds_data = db.session.query(
        Round.id, Round.round_name.label('round_name'),
        Round.kyoku, RoundDetail.player_index.label('player_index'),
        Team.color_code.label('color'),
        Player.name.label('name'),
        RoundDetail.balance.label('balance'),
        Win.type.label('type'),  # ロンツモ
        Win.score_name.label('score_name'), 
        Win.point.label('point'),
        Win.yaku.label('yaku'), 
        Win.tehai.label('tehai'),
        Win.win_pai.label('win_pai'), 
        Win.deal_in.label('deal_in')
    ).select_from(Round).join(
        RoundDetail, 
        (Round.id == RoundDetail.round_id)
    ).outerjoin(  # LEFT JOIN を使用して Win テーブルを結合
        Win,
        (RoundDetail.round_id == Win.round_id) & (RoundDetail.player_index == Win.player_index)
    ).join(Player).join(Team).filter(
        Round.gameid == gameid
    ).all()
    
    if len(rounds_data) == 0:
        return render_template('game/detail.html', game=game, players=[], rounds=[], check=False)
    
    # player_indexと選手名の組み合わせ
    player_index_dict = {}
    for j in range(4):
        player_index_dict[rounds_data[j].player_index] = rounds_data[j].name


    round_records = [{'result': '流局'} for i in range(len(rounds_data)//4)]
    #print(round_records, len(rounds_data))
    for i in range(len(rounds_data)//4):
        
        for j in range(4):
            
            round_record = rounds_data[i*4 + j]
            #print('N', round_record)
            if round_record.type is None:
                round_records[i]['round_name'] = round_record.round_name
                continue
            else:
                round_records[i]['round_name'] = round_record.round_name
                round_records[i]['result'] = '和了'
                round_records[i]['name'] = round_record.name
                round_records[i]['type'] = round_record.type
                round_records[i]['score_name'] = round_record.score_name
                round_records[i]['balance'] = round_record.balance
                round_records[i]['point'] = round_record.point
                round_records[i]['yaku'] = round_record.yaku
                round_records[i]['tehai'] = round_record.tehai
                round_records[i]['win_pai'] = round_record.win_pai
                round_records[i]['deal_in'] = player_index_dict[round_record.deal_in] if round_record.deal_in is not None else None
                round_records[i]['color'] = round_record.color
                break

    
    rounds = db.session.query(Round).options(joinedload(Round.round_details)).filter_by(gameid=gameid)
    
    count = {
        detail.playerid : {'richi': 0, 'win': 0, 'deal_in': 0} for detail in game.details
    }
    
    for round_data in rounds.all():
        for i, round_detail in enumerate(round_data.round_details):
            key = round_detail.playerid
            if round_detail.richi:
                count[key]['richi'] += 1
            if round_detail.result == '和了':
                count[key]['win'] += 1
            if round_detail.result == '放銃':
                count[key]['deal_in'] += 1

    players = [
        {
            'name': detail.player.name,
            'rank': detail.rank, 
            'point': detail.point, 
            'richi': count[detail.playerid]['richi'], 
            'win': count[detail.playerid]['win'], 
            'deal_in': count[detail.playerid]['deal_in'],
            'player': detail.player
        }
            for detail in game.details
    ]
    
    players.sort(key=lambda x: x['rank'])
    
    return render_template('game/detail.html', game=game, players=players, rounds=round_records, check=True)