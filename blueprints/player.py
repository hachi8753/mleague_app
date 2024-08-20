from flask import Blueprint, render_template
from models import db, Player, Team, Game, GameDetail, Image, PlayerHistory, Transfer
from models import Round, RoundDetail, Win, Meld, Log

from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func, case
from pprint import pprint
from decimal import Decimal

player_bp = Blueprint('player', __name__, url_prefix='/player')

# 選手一覧
@player_bp.route('/')
def display():
    players = Player.query.join(Team, Player.teamid == Team.id).order_by(Player.id).all()
    
    
    now_players = Player.query.join(Team).join(
        PlayerHistory
    ).filter(PlayerHistory.leave_year == None).order_by(Player.id).all()
    
    now_players_dict = {}
    """
    now_players_dict = {'P10001': {'player': <Player P10001>, 'path': 'players/image23_10001.png'}, ...}
    """
    
    for player in now_players:
        image = Image.query.filter_by(type='player', foreign_id=player.id).order_by(Image.year.desc()).first()
        now_players_dict[player.id] = {}
        now_players_dict[player.id]['player'] = player
        if image is None:
            now_players_dict[player.id]['path'] = None
        else:
            now_players_dict[player.id]['path'] = image.path
    
    leave_players = (
        db.session.query(Player)
        .join(Player.history)
        .outerjoin(Player.transfer)  # Transfer モデルの `old_player` リレーションシップを join
        .options(joinedload(Player.transfer))
        .filter(
            and_(
                PlayerHistory.leave_year != None,
                Player.transfer == None
            )
        ).all()
    )
    
    leave_players_dict = {}
    for player in leave_players:
        image = Image.query.filter_by(type='player', foreign_id=player.id).order_by(Image.year.desc()).first()
        leave_players_dict[player.id] = {}
        leave_players_dict[player.id]['player'] = player
        if image is None:
            leave_players_dict[player.id]['path'] = None
        else:
            leave_players_dict[player.id]['path'] = image.path
    
    return render_template('player/display.html', players=players, players_dict=now_players_dict.values(),
                           leave_players_dict=leave_players_dict.values())

@player_bp.route('/<playerid>')
def detail(playerid):
    
    results_data = db.session.query(
            Game.year,
            Game.seasonName,
            func.sum(GameDetail.score).label('total_score'), 
            func.max(GameDetail.point).label('max_point'), 
            func.count(GameDetail.id).label('count'),
            func.sum(case((GameDetail.rank == 1, 1), else_=0)).label('rank1'),
            func.sum(case((GameDetail.rank == 2, 1), else_=0)).label('rank2'),
            func.sum(case((GameDetail.rank == 3, 1), else_=0)).label('rank3'),
            func.sum(case((GameDetail.rank == 4, 1), else_=0)).label('rank4')
        ).join(Game).join(Player).join(Team).filter(
        and_(
            GameDetail.playerid == playerid
        )
    ).group_by(Game.year, Game.seasonName).all()
        
    results = {}
    
    season_list = ['Regular', 'Semi', 'Final', 'All']
    
    for result_data in results_data:
        year = result_data.year
        if year not in results.keys():
            results[year] = {
                seasonName: {
                    'score': Decimal(0.0), 'max_point': 0, 'count': 0, 'rank1': 0, 'rank2': 0, 'rank3': 0, 'rank4': 0
                } for seasonName in (season_list if year>2018 else ['Regular', 'Final', 'All'])
            }
        season = result_data.seasonName
        results[year][season]['score'] = result_data.total_score
        results[year][season]['max_point'] = result_data.max_point
        results[year][season]['count'] = result_data.count
        results[year][season]['rank1'] = result_data.rank1
        results[year][season]['rank2'] = result_data.rank2
        results[year][season]['rank3'] = result_data.rank3
        results[year][season]['rank4'] = result_data.rank4
        # 計算
        results[year][season]['avoid4'] = "{:.3f}".format(1 - result_data.rank4 / result_data.count)  # 4着回避率
        results[year][season]['top_rate'] = "{:.3f}".format(result_data.rank1 / result_data.count)  # トップ率
        results[year][season]['rentai'] = "{:.3f}".format((result_data.rank1 + result_data.rank2) / result_data.count)  # 連対率
        results[year][season]['average_rank'] = "{:.3f}".format(
            (result_data.rank1 + result_data.rank2*2 + result_data.rank3*3 + result_data.rank4*4) / result_data.count
        )
    # 集計 (All)
    for year in results.keys():
        for key in results[year]['Regular'].keys():
            results[year]['All'][key] = get_all_season_data(results, year, key)
    
    images = Image.query.filter_by(type='player', foreign_id=playerid).order_by(Image.year.desc()).all()
    
    player = db.session.get(Player, playerid)
    
    
    
    # 成績未登録で、写真だけ登録されている場合
    keys = ['score', 'max_point', 'count', 'rank1', 'rank2', 'rank3', 'rank4',
            'avoid4', 'top_rate', 'rentai', 'average_rank']
    if len(images)>0 and images[0].year not in results.keys():
        results[images[0].year] = {seasonName: {key: None for key in [
            'score', 'max_point', 'count', 'rank1', 'rank2', 'rank3', 'rank4','avoid4', 'top_rate', 'rentai', 'average_rank'
            ]} for seasonName in season_list}
    
    # 成績のリスト
    detail_boxes = [(year, images[i], [(seasonName, results[year][seasonName]) for seasonName in 
                                       (season_list if year > 2018 else ['Regular', 'Final', 'All'])])
                    for i, year in enumerate(sorted(results.keys(), reverse=True))]
    
    # 通算成績
    results_all = [(seasonName, {key: get_all_year_data(results, seasonName, key) for key in keys}) for seasonName in season_list]
    # チームロゴ画像
    team_logo = Image.query.filter_by(type='team', foreign_id=player.teamid, format='logo').first()
    
    
    
    # 和了データ
    win_count = func.count(Win.id)
    richi_win_count = func.sum(case((Win.tenpai_type == 'リーチ', 1), else_=0))
    win_data = db.session.query(
            Game.year.label('year'),
            win_count.label('win_count'), # 和了回数
            richi_win_count.label('richi_win_count'), 
            (func.sum(Win.point) / func.count(Win.point)).label('average_win_point'),  # 平均打点
            func.max(Win.point).label('max_win_point'),  # 最大和了点
            (func.sum(Win.dora) / win_count).label('dora_average'),  # 平均ドラ枚数
            (func.sum(Win.aka) / win_count).label('aka_average'),  # 平均赤ドラ枚数
            (func.sum(Win.ura) / win_count).label('ura_average'),  # 平均裏ドラ枚数
            (func.sum(case((Win.type == 'ツモ', 1), else_=0)) / win_count).label('tsumo_rate'), 
            (func.sum(case((Win.ura > 0, 1), else_=0)) / richi_win_count).label('ura_in_rate'),  # 裏ドラ含有率
            (richi_win_count / win_count).label('richi_of_win'), # 和了内訳 (リーチ)
            (func.sum(case((Win.tenpai_type == '副露', 1), else_=0)) / win_count).label('meld_of_win'), # 和了内訳 (リーチ)
            (func.sum(case((Win.tenpai_type == 'ヤミテン', 1), else_=0)) / win_count).label('dama_of_win'), # 和了内訳 (リーチ)
            (func.sum(case((Win.yaku.contains('一発'), 1), else_=0))).label('soku_count')  # 一発和了回数
        ).outerjoin(
            RoundDetail, 
            and_(
                Win.round_id == RoundDetail.round_id,
                Win.player_index == RoundDetail.player_index
            )
        ).join(Round).join(Game).filter(
        and_(
            RoundDetail.playerid == playerid, 
            Game.seasonName == 'Regular'
        )
    ).group_by(Game.year).all()
        
    round_count = func.count(RoundDetail.round_id)
    
    round_data = db.session.query(
            Game.year.label('year'), 
            round_count.label('round_count'),
            (func.sum(case((RoundDetail.result == "和了", 1), else_=0)) / round_count).label('win_rate'), 
            (func.sum(case((RoundDetail.result == "放銃", 1), else_=0)) / round_count).label('deal_in_rate'), 
            (func.sum(case((RoundDetail.result == "流局", 1), else_=0)) / round_count).label('draw_rate'), 
            (func.sum(case((RoundDetail.richi, 1), else_=0)) / round_count).label('richi_rate'), 
            (func.sum(case((RoundDetail.meld_num > 0, 1), else_=0)) / round_count).label('meld_rate'), 
            (func.sum(case((RoundDetail.tenpai, 1), else_=0)) / func.sum(case((RoundDetail.result == "流局", 1), else_=0))).label('tenpai_rate'), 
        ).select_from(RoundDetail).join(Round).join(Game).filter(
        and_(
            RoundDetail.playerid == playerid, 
            Game.seasonName == 'Regular'
        )
    ).group_by(Game.year).all()
    
    #pprint(round_data)
    
    detail_result = get_detail_result(round_data, win_data)
    
    return render_template('player/detail.html', player=player, boxes=detail_boxes, team_logo=team_logo.path,
                           results_all=results_all, detail_result=detail_result)

# カスタムフィルター
@player_bp.app_template_filter('judge_transfer')
def judge_transfer(transfer):
    if len(transfer) > 0:
        return True
    else:
        return False


def get_all_season_data(results, year, key):
    seasons = ['Regular', 'Semi', 'Final'] if year > 2018 else ['Regular', 'Final']
    
    if key == 'max_point':
        return max(results[year][season][key] for season in seasons)
    elif key == 'avoid4':
        return "{:.3f}".format(
            1 - get_all_season_data(results, year, 'rank4') / get_all_season_data(results, year, 'count')
        )
    elif key == 'top_rate':
        return "{:.3f}".format(
            get_all_season_data(results, year, 'rank1') / get_all_season_data(results, year, 'count')
        )
    elif key == 'rentai':
        return "{:.3f}".format(
            (
                get_all_season_data(results, year, 'rank1') + get_all_season_data(results, year, 'rank2')
            ) / get_all_season_data(results, year, 'count')
        )
    elif key == 'average_rank':
        return "{:.3f}".format(
            (
                get_all_season_data(results, year, 'rank1') + get_all_season_data(results, year, 'rank2')*2 +
                get_all_season_data(results, year, 'rank3')*3 + get_all_season_data(results, year, 'rank4')*4
            ) / get_all_season_data(results, year, 'count')
        )
    else:
        return sum(results[year][season][key] for season in seasons)

# Allを埋めた後での実行を推奨
def get_all_year_data(results, season, key):
    if key != 'count' and get_all_year_data(results, season, 'count') == 0:
        if key in ['count', 'rank1', 'rank2', 'rank3', 'rank4']:
            return 0
        elif key == 'score':
            return '0.0'
        else:
            return '-'
    if key == 'max_point':
        return max(results[year][season][key] for year in results.keys() if season in results[year].keys())
    elif key == 'avoid4':
        return "{:.3f}".format(
            1 - get_all_year_data(results, season, 'rank4') / get_all_year_data(results, season, 'count')
        )
    elif key == 'top_rate':
        return "{:.3f}".format(
            get_all_year_data(results, season, 'rank1') / get_all_year_data(results, season, 'count')
        )
    elif key == 'rentai':
        return "{:.3f}".format(
            (
                get_all_year_data(results, season, 'rank1') + get_all_year_data(results, season, 'rank2')
            ) / get_all_year_data(results, season, 'count')
        )
    elif key == 'average_rank':
        return "{:.3f}".format(
            (
                get_all_year_data(results, season, 'rank1') + get_all_year_data(results, season, 'rank2')*2 
                + get_all_year_data(results, season, 'rank3')*3 + get_all_year_data(results, season, 'rank4')*4
            ) / get_all_year_data(results, season, 'count')
        )
    else:
        return sum(results[year][season][key] for year in results.keys() if season in results[year].keys())

# 成績詳細を取得
def get_detail_result(round_datas, win_datas):
    
    detail_result = {}

    for round_data in round_datas:
        year = round_data.year
        if year not in detail_result.keys():
            detail_result[year] = {}
        detail_result[year]['win_rate'] = "{:.2f}".format(round_data.win_rate*100)
        
        detail_result[year]['round_count'] = round_data.round_count
        
        detail_result[year]['deal_in_rate'] = "{:.2f}".format(round_data.deal_in_rate*100)
        detail_result[year]['meld_rate'] = "{:.2f}".format(round_data.meld_rate*100)
        detail_result[year]['draw_rate'] = "{:.2f}".format(round_data.draw_rate*100)
        detail_result[year]['richi_rate'] = "{:.2f}".format(round_data.richi_rate*100)
        detail_result[year]['tenpai_rate'] = "{:.2f}".format(round_data.tenpai_rate*100)



    for win_data in win_datas:
        year = win_data.year
        if year not in detail_result.keys():
            detail_result[year] = {}
        detail_result[year]['win_count'] = win_data.win_count
        
        detail_result[year]['tsumo_rate'] = "{:.2f}".format(win_data.tsumo_rate*100)
        
        detail_result[year]['average_win_point'] = "{:.0f}".format(win_data.average_win_point)
        detail_result[year]['max_win_point'] = win_data.max_win_point
        detail_result[year]['all_dora_average'] = "{:.2f}".format(win_data.dora_average + win_data.aka_average + win_data.ura_average)
        detail_result[year]['dora_average'] = "{:.2f}".format(win_data.dora_average)
        detail_result[year]['aka_average'] = "{:.2f}".format(win_data.aka_average)
        detail_result[year]['ura_average'] = "{:.2f}".format(win_data.ura_average)
        detail_result[year]['ura_in_rate'] = "{:.2f}".format(win_data.ura_in_rate*100)
        detail_result[year]['richi_of_win'] = "{:.2f}".format(win_data.richi_of_win*100)
        detail_result[year]['dama_of_win'] = "{:.2f}".format(win_data.dama_of_win*100)
        detail_result[year]['meld_of_win'] = "{:.2f}".format(win_data.meld_of_win*100)
        detail_result[year]['soku_rate'] = "{:.2f}".format(win_data.soku_count / win_data.richi_win_count*100)
    
    new_detail_result = [(year, detail_result[year]) for year in sorted(detail_result.keys(), reverse=True)]

    return new_detail_result
