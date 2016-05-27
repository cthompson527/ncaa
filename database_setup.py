from flask_sqlalchemy import SQLAlchemy
from ncaa import app

db = SQLAlchemy(app)

class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    conference = db.Column(db.String(30), nullable=False)


class Game(db.Model):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    home_team = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    home_score = db.Column(db.Integer, nullable=False)
    away_score = db.Column(db.Integer, nullable=False)
    finished = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Date, nullable=False)

db.create_all()
db.session.commit()

if __name__ == '__main__':
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm.exc import NoResultFound
    from scraper import get_team_ids, get_game_ids_in_year, get_game_result_by_ids
    from datetime import datetime

    current_date = datetime.now()
    year = current_date.year

    teams = get_team_ids()
    for team in teams:
        try:
            db_team = Team(id=team['id'], name=team['name'], conference=team['conference'])
            db.session.add(db_team)
            db.session.commit()
        except IntegrityError:
            print team['name'] + ' already exists in the database.'
            db.session.rollback()

    games = get_game_ids_in_year(year)
    print games
    print len(games)

    for game in games:
        try:
            away_team = db.session.query(Team).filter_by(id=game['away_id']).one()
            home_team = db.session.query(Team).filter_by(id=game['home_id']).one()
            if away_team.conference == home_team.conference:
                db_game = Game(id=game['game_id'], home_team=game['home_id'], away_team=game['away_id'], year=game['year'], week=game['week'], date=game['date'], home_score=0, away_score=0, finished=False)
                db.session.add(db_game)
                db.session.commit()
        except NoResultFound:
            pass
        except IntegrityError:
            db.session.rollback()

    print 'grabbing game data for all games in 2015'
    previous_games = db.session.query(Game).filter(Game.year < year).all()
    game_ids = []
    for game in previous_games:
        game_ids.append(game.id)
    game_results = get_game_result_by_ids(game_ids)
    for game_result in game_results:
        game = db.session.query(Game).get(game_result['id'])
        game.away_score = game_result['away_score']
        game.home_score = game_result['home_score']
        game.finished = game_result['final']
        db.session.add(game)
        db.session.commit()
    print len(previous_games)
