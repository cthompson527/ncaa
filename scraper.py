from bs4 import BeautifulSoup
from threading import Thread
import urllib2

def get_team_ids():
    conferences = ['ACC', 'Big Ten', 'Big 12', 'Pac-12', 'SEC']
    tables = {}
    teams = []
    html_doc = urllib2.urlopen('http://espn.go.com/college-football/teams')
    soup = BeautifulSoup(html_doc, 'html.parser')
    fbs = soup.find('div', 'span-2')
    table_titles = fbs.find_all('h4')

    # initialize the team_ids hashmap
    for table_title in table_titles:
        if table_title.text in conferences:
            tables[table_title.text] = table_title.parent.parent

    # insert teams in team_ids hashmap
    for conference in conferences:
        lists = tables[conference].find_all('li')
        for list in lists:
            anchor = list.h5.a
            id = __get_team_id_from_a(anchor)
            name = anchor.text
            team = dict(id=id, name=name, conference=conference)
            teams.append(team)

    return teams

def get_game_ids_in_year(year):
    list_of_game_ids_in_week = []
    threads = []

    for index in xrange(15):
        week = index + 1
        t = Thread(target=__retrieve_game_data_from_espn, args=(year, week, list_of_game_ids_in_week))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()

    game_ids = [y for x in list_of_game_ids_in_week for y in x]
    return game_ids

def get_game_result_by_ids(game_ids):
    game_results = []
    threads = []
    split_game_ids = [game_ids[x:x+20] for x in xrange(0, len(game_ids), 20)]
    for ids in split_game_ids:
        for id in ids:
            t = Thread(target=__retrieve_results_data_from_espn, args=(id, game_results))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()
        print 'length: %s --- %s' % (len(game_results), game_results)
    return game_results

def __retrieve_results_data_from_espn(id, game_results):
    from urllib2 import HTTPError
    home_score = 0
    away_score = 0
    final = False
    result = dict(id=id, home_score=home_score, away_score=away_score, final=final)
    while True:
        try:
            html_doc = urllib2.urlopen('http://espn.go.com/college-football/game?gameId=%s' % id)
            break
        except HTTPError:
            continue

    soup = BeautifulSoup(html_doc, 'html.parser')
    div = soup.find('div', class_='competitors')
    away = div.find('div', class_='team away')
    home = div.find('div', class_='team home')
    away_container = away.find('div', class_='score-container')
    if away_container.div.text:
        away_score = away_container.div.text
        home_container = home.find('div', class_='score-container')
        home_score = home_container.div.text
        game_status = div.find('div', class_='game-status')
        final = 'Final' in game_status.span.text
        result['home_score'] = home_score
        result['away_score'] = away_score
        result['final'] = final
    game_results.append(result)

def __get_team_id_from_a(a_tag):
    href = a_tag['href']
    urlpath = href.split('/')
    id = urlpath[urlpath.index('id')+1]
    return id

def __get_game_id_from_a(a_tag):
    href = a_tag['href']
    querypath = href.split('=')
    id = querypath[1]
    return id

def __retrieve_game_data_from_espn(year, week, games):
    from datetime import datetime, date
    html_doc = urllib2.urlopen('http://espn.go.com/college-football/schedule/_/year/%s/week/%s' % (year, week))
    # html_doc = urllib2.urlopen('http://espn.go.com/college-football/schedule/_/year/2015/group/4/week/4')
    soup = BeautifulSoup(html_doc, 'html.parser')
    div = soup.find('div', id='sched-container')
    trs = div.find_all('tr')
    games_in_week = []
    for tr in trs:
        str_date = tr.parent.parent.parent.previous_sibling.text + ', ' + str(year)
        date = datetime.strptime(str_date, '%A, %B %d, %Y').date()
        td = tr.td
        if td == None:
            continue
        away_td = td
        away_link = away_td.find('a')
        home_td = td.next_sibling
        home_link = home_td.find('a')
        time_td = td.next_sibling.next_sibling
        game_link = time_td.find('a')
        if away_link == None or home_link == None or game_link == None:
            continue
        away_id = __get_team_id_from_a(away_link)
        home_id = __get_team_id_from_a(home_link)
        game_id = __get_game_id_from_a(game_link)
        games_in_week.append(dict(away_id=away_id, home_id=home_id, game_id=game_id, year=year, week=week, date=date))

    games.append(games_in_week)

if __name__ == '__main__':
    #print get_game_ids_in_year(2015)
    #print get_team_ids()
    print get_game_result_by_ids([400869090, 400869822, 400757045])
