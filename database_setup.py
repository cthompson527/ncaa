from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.types import Boolean, Date

Base = declarative_base()

# class Restaurant(Base):
#     __tablename__ = 'restaurant'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(250), nullable=False)
#
# class MenuItem(Base):
#     __tablename__ = 'menu_item'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(80), nullable=False)
#     description = Column(String(250))
#     price = Column(String(8))
#     course = Column(String(250))
#     restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
#     restaurant = relationship(Restaurant)

class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    conference = Column(String(30), nullable=False)

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    home_team = Column(Integer, ForeignKey('team.id'), nullable=False)
    away_team = Column(Integer, ForeignKey('team.id'), nullable=False)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)
    date = Column(Date, nullable=False)


engine = create_engine('sqlite:///ncaa.db')
Base.metadata.create_all(engine)

if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm.exc import NoResultFound
    from scraper import get_team_ids, get_game_ids_in_year, get_game_result_by_ids
    from datetime import datetime

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    current_date = datetime.now()
    year = current_date.year

    # teams = get_team_ids()
    # for team in teams:
    #     try:
    #         db_team = Team(id=team['id'], name=team['name'], conference=team['conference'])
    #         session.add(db_team)
    #         session.commit()
    #     except IntegrityError:
    #         print team['name'] + ' already exists in the database.'
    #         session.rollback()
    #
    # games = get_game_ids_in_year(year)
    # print games
    # print len(games)
    # for game in games:
    #     try:
    #         away_team = session.query(Team).filter_by(id=game['away_id']).one()
    #         home_team = session.query(Team).filter_by(id=game['home_id']).one()
    #         if away_team.conference == home_team.conference:
    #             db_game = Game(id=game['game_id'], home_team=game['home_id'], away_team=game['away_id'], year=game['year'], week=game['week'], date=game['date'], home_score=0, away_score=0, finished=False)
    #             session.add(db_game)
    #             session.commit()
    #
    #     except NoResultFound:
    #         # print 'could not find team id#%s or team id#%s' % (game['home_id'], game['away_id'])
    #         # games.remove(game)
    #         pass
    #     except IntegrityError:
    #         session.rollback()

    print 'grabbing game data for all games in 2015'
    previous_games = session.query(Game).filter(Game.year < year).all()
    game_ids = []
    for game in previous_games:
        game_ids.append(game.id)
    game_results = get_game_result_by_ids(game_ids)
    for game_result in game_results:
        game = session.query(Game).get(game_result['id'])
        game.away_score = game_result['away_score']
        game.home_score = game_result['home_score']
        game.finished = game_result['final']
        session.add(game)
        session.commit()
    print len(previous_games)






