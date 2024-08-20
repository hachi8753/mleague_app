from flask import Flask, Blueprint,  render_template, request, redirect, url_for

from forms import InputForm, InputFormGame, InputFormRegulation
from models import db, Player, Team, Game, GameDetail, PlayerHistory, Image
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy import and_, or_, func, case

from pprint import pprint

result_bp = Blueprint('result', __name__, url_prefix='/result')

@result_bp.route('/')
def index():
    return render_template('result/index.html')



@result_bp.route('/<int:year>')
def display(year):
    
    results = db.session.query(
            GameDetail.playerid,
            Player.name.label('player_name'),
            Team.name.label('team_name'), 
            func.sum(GameDetail.score).label('total_score'), 
            func.max(GameDetail.point).label('max_point'), 
            func.count(GameDetail.id).label('count'), 
            func.sum(case((GameDetail.rank == 1, 1), else_=0)).label('rank1'),
            func.sum(case((GameDetail.rank == 2, 1), else_=0)).label('rank2'),
            func.sum(case((GameDetail.rank == 3, 1), else_=0)).label('rank3'),
            func.sum(case((GameDetail.rank == 4, 1), else_=0)).label('rank4')
        ).join(Game).join(Player).join(Team).filter(
        and_(
            Game.year == year,
            Game.seasonName == 'Regular'
        )
    ).group_by(GameDetail.playerid).all()
    
    # スコアリストを取得する
    score_list = [result.total_score for result in results]

    # スコアとそのインデックスのリストを作成する
    indexed_scores = list(enumerate(score_list))

    # スコアで降順にソートする
    sorted_scores = sorted(indexed_scores, key=lambda x: x[1], reverse=True)

    # 順位を計算する
    rank_map = {}
    current_rank = 1
    for i, (index, score) in enumerate(sorted_scores):
        if i > 0 and score < sorted_scores[i - 1][1]:
            current_rank = i + 1
        rank_map[index] = current_rank

    # 元のスコアリストに基づいて順位リストを作成する
    rank_and_result = [(rank_map[i], result) for i, result in enumerate(results)]

    return render_template('result/display.html', results=rank_and_result)


@result_bp.route('/champion')
def champion():
    
    results = db.session.query(
            Game.year, 
            Team.id, 
            func.sum(GameDetail.score).label('point')
        ).select_from(GameDetail).join(Game).join(Player).join(Team).filter(
            Game.seasonName == 'Regular'    
        ).group_by(Game.year, Team.id).all()

    
    win_teams, result_regular = get_ranking_regular(results, 'Regular')
    
    results = db.session.query(
            Game.year, 
            Team.id, 
            func.sum(GameDetail.score).label('point')
        ).select_from(GameDetail).join(Game).join(Player).join(Team).filter(
            Game.seasonName == 'Semi'
        ).group_by(Game.year, Team.id).all()
    
    #pprint(results)
    
    win_teams, result_semi = get_ranking_regular(results, 'Semi', win_teams)
    
    results = db.session.query(
            Game.year, 
            Team.id, 
            func.sum(GameDetail.score).label('point')
        ).select_from(GameDetail).join(Game).join(Player).join(Team).filter(
            Game.seasonName == 'Final'
        ).group_by(Game.year, Team.id).all()
    
    win_teams, result_final = get_ranking_regular(results, 'Final', win_teams)
    
    
    
    champions = []
    for year in win_teams.keys():
        teamid = list(win_teams[year].keys())[0]
        players = db.session.query(
            Player
        ).select_from(Player).join(PlayerHistory).filter(
            and_(
                Player.teamid == teamid,
                PlayerHistory.entry_year <= year, 
                or_(PlayerHistory.leave_year >= year, PlayerHistory.leave_year.is_(None))
            )
        ).all()
        
        images = [Image.query.filter_by(type='player', foreign_id=player.id, year=year).first().path for player in players]
        
        logo = Image.query.filter_by(type='team', foreign_id=teamid, format='logo').first().path
        
        champion = (year, {
            'team': players[0].team.name, 
            'point': "{:.1f}".format(win_teams[year][teamid]), 
            'logo': logo,
            'path': images,
            'color': players[0].team.color_code_light
        })
        champions.append(champion)
    
    champions.sort(key=lambda x: x[0], reverse=True)
    
    return render_template('result/champion.html', champions=champions)

"""


    images = Image.query.filter_by(type='player', foreign_id=playerid).order_by(Image.year.desc()).all()
    
    player = db.session.get(Player, playerid)
"""


# レギュラーを通過したチームのリストと、チームポイント半分を返す
def get_ranking_regular(results, season, win_teams=None):
    
    result_list = {}    

    for result in results:
        year = result.year            
        if year not in result_list.keys():
            result_list[year] = []
        if win_teams is None:
            result_list[result.year].append(result)
        else:
            if result[1] in win_teams[year].keys():
                result_list[year].append((result[0], result[1], result[2]+win_teams[year][result[1]]))
    
    # 2018, Semiは対局データがないので、初期化の時に格納しておく
    if win_teams is not None and season == 'Semi':
        win_teams = {2018: win_teams[2018]}
    else:
        win_teams = {}
    
    
    for year in result_list.keys():
        result_list[year].sort(key=lambda x: x[2], reverse=True)

        win_teams[year] = []

        if season != 'Final':
            num = 6 if season == 'Regular' and year > 2018 else 4
            #FIXME 切り上げ、切り下げを修正する必要がある
            win_teams[year] = {result_list[year][i][1]: result_list[year][i][2]/2 for i in range(num)}
        else:
            win_teams[year] = {result_list[year][0][1]: result_list[year][0][2]}

        #FIXME データが揃ったら削除する
        if year == 2019:
            if season == 'Semi':
                win_teams[2019]['T700'] = win_teams[2019].pop('T600')
            elif season == 'Final':
                win_teams[2019]['T700'] = win_teams[2019].pop('T500')
                
                
        
    
    return win_teams, result_list
