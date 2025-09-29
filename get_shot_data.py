from understatapi import UnderstatClient
import time
from datetime import datetime
import pandas as pd

def get_league_shot_data(league:list[str], season:list[str]=None, period_start:str=None, period_end:str=None) -> tuple[pd.DataFrame]:
    '''
    Get the shot data from understat for every game in a specified league (or leagues), for a given season (or seasons), for a given time period. 
    If `period_start` and `period_end` are None, return shot data for all games in the specified season (or seasons). If `season` is None, most 
    recent season is used. Function saves the data in `/data/matches.csv` and `/data/raw_shots.csv` as well as returning the pandas DataFrames.
    
    :param league: a list of the leagues to get data for. One of {'EPL', 'La_Liga', 'Bundesliga', 'Serie_A', 'Ligue_1', 'RFPL'}
    :type league: list[str] | str
    :param season: a list of the seasons to get data for. Seasons use 'YYYY' format for starting year of the league (e.g. '2025' for the 2025/26 
        Premier League season). If None, `season` will be determined as the previous year from Jan 1 to Jul 31, and current year from Aug 1 to
        Dec 31.
    :type season: list[str] | str
    :param period_start: Starting date for return period. Must be in 'YYYY-MM-DD' format. Matches played on this date included.
    :type period_start: str
    :param period_end: Ending date for return period. Must be in 'YYYY-MM-DD' format. Matches played on this date included.
    :type period_end: str
    :returns matches_df: Pandas DataFrame containing the ID `match_id`, Home Team name `h_team`, Away Team name `a_team`, Match Code `match_code`,
        and maximum number minutes in the game `max_min`, for each match
    :rtype matches_df: pd.DataFrame
    :returns shots_df: Pandas DataFrame containing the match ID `match_id`, minute the shot was taken as an int `minute`, whether the shot was for 
        the home or away team `h_a`, xG of the shot `xG`, result of the shot (Goal, Saved Shot, etc.) `result`, x coordinate of the shot `x`, y
        coordinate of the shot `y`, player who took the shot `player`, type of shot (Right footed, Header, etc.) `shot_type`, and last action before
        the shot was taken (Rebound, Pass, etc.) `last_action`
    :rtype shots_df: pd.DataFrame
    '''
    # Set up timer
    sleep_setting = 2
    clock_start = time.monotonic()
    time_asleep = 0

    # Check for errors in function parameters
    if type(league) == str:
        league = [league]
    if league is None or len(league) == 0:
        raise ValueError('league field cannot be None or empty list')
    else:
        valid_leagues = {'EPL','La_Liga','Bundesliga','Serie_A','Ligue_1','RFPL'}
        for l in league:
            if l not in valid_leagues:
                raise ValueError(f'{l} is not a valid league. Please select from {valid_leagues}.')
    if type(season) == str:
        season = [season]
    if season is None or len(season) == 0:
        cur_month = datetime.today().month
        cur_year = datetime.today().year
        if cur_month >= 8:
            season = [str(cur_year)]
        else:
            season = [str(cur_year-1)]
    else:
        for s in season:
            if type(s) != str:
                raise TypeError(f'{s} is type {type(s)}. Season ids must be type string.')
            if int(s) <= 2013:
                raise ValueError(f'Understat has no data for {s} season. Earliest data available is for the 2014/15 season.')
    if (period_end is not None and period_start is None) or (period_start is not None and period_end is None):
        raise ValueError('period_start and period_end must both be set or both be None')
    if period_start is not None:
        if type(period_start) != str:
            raise TypeError(f'{period_start} is type {type(period_start)}. period_start must be of type string in "YYYY-MM-DD" format')
        else:
            start_year = int(period_start.split('-')[0])
            start_month = int(period_start.split('-')[1])
            start_day = int(period_start.split('-')[2])
            if start_day > 31:
                raise ValueError(f'{period_start} is not a valid date in "YYYY-MM-DD" format.')
            elif start_day == 31 and start_month in (2,4,6,9,11):
                raise ValueError(f'{period_start} is not a valid date in "YYYY-MM-DD" format.')
            elif start_day > 29 and start_month == 2:
                raise ValueError(f'{period_start} is not a valid date in "YYYY-MM-DD" format.')
            elif start_day == 29 and start_month ==2:
                if not (((start_year % 4 == 0) and (start_year % 100 != 0)) or (start_year % 400 == 0)):
                    raise ValueError(f'{period_start} is not a valid date ({start_year} is not a leap year)')
            elif start_month > 12:
                raise ValueError(f'{period_start} is not a valid date in "YYYY-MM-DD" format. Did you mean "{start_year}-{start_day}-{start_month}"?')
    if period_end is not None:
        if type(period_end) != str:
            raise TypeError(f'{period_end} is type {type(period_end)}. period_end must be of type string in "YYYY-MM-DD" format')
        else:
            end_year = int(period_end.split('-')[0])
            end_month = int(period_end.split('-')[1])
            end_day = int(period_end.split('-')[2])
            if end_day > 31:
                raise ValueError(f'{period_end} is not a valid date in "YYYY-MM-DD" format.')
            elif end_day == 31 and end_month in (2,4,6,9,11):
                raise ValueError(f'{period_end} is not a valid date in "YYYY-MM-DD" format.')
            elif end_day > 29 and end_month == 2:
                raise ValueError(f'{period_end} is not a valid date in "YYYY-MM-DD" format.')
            elif end_day == 29 and end_month ==2:
                if not (((end_year % 4 == 0) and (end_year % 100 != 0)) or (end_year % 400 == 0)):
                    raise ValueError(f'{period_end} is not a valid date ({end_year} is not a leap year)')
            elif end_month > 12:
                raise ValueError(f'{period_end} is not a valid date in "YYYY-MM-DD" format. Did you mean "{end_year}-{end_day}-{end_month}"?')
            if (end_year < start_year) or ((end_month < start_month) and (end_year <= start_year)) or ((end_day < start_day) and (end_month <= start_month)):
                raise ValueError(f'period_end ({period_end}) cannot be before period_start ({period_start})')
    
    elapsed = time.monotonic()
    print(f'Parameter checks complete. {round(elapsed - clock_start,4)} seconds elapsed...')

    # Set up dictionaries for collecting the holding the understat data
    match_data = {
        'match_id':[],
        'h_team':[],
        'a_team':[],
        'match_code':[],
        'max_min':[]
    }

    shot_data = {
        'match_id':[],
        'minute':[],
        'h_a':[],
        'xG':[],
        'result':[],
        'x':[],
        'y':[],
        'player':[],
        'shot_type':[],
        'last_action':[]
    }

    # Create understat session client
    u = UnderstatClient()
    for l in league:
        for s in season:
            time.sleep(sleep_setting)
            time_asleep += sleep_setting
            print(f'Getting match data for {s} season of {l}...')
            matches = u.league(league=l).get_match_data(season=s)
            elapsed = time.monotonic()
            print(f'{len(matches)} match results returned. {round(elapsed - clock_start,2)} seconds elapsed, of which {time_asleep} spent asleep.')
            total_results = sum([m['isResult'] for m in matches])
            loop_counter = 0
            for m in matches:
                if m['isResult']:
                    # Use all matches if period_start is None, otherwise check match date to ensure in scope
                    if period_start is None:
                        # Increment counter for status messages
                        loop_counter += 1

                        # Get team names and match code
                        h_team = m['h']['title']
                        a_team = m['a']['title']
                        code = f'{m['h']['short_title']}{m['a']['short_title']}{m['datetime'][:4]}{m['datetime'][5:7]}{m['datetime'][8:10]}'

                        # Get shot data from Understat for current match
                        print(f'Getting shot data for result {loop_counter} of {total_results}. Roughly {(total_results - (loop_counter - 1))*sleep_setting} seconds remaining...')
                        time.sleep(sleep_setting)
                        time_asleep += sleep_setting
                        shots = u.match(m['id']).get_shot_data()
                        h_shots = shots['h']
                        a_shots = shots['a']

                        # Determine last minute a shot was taken or default to 90 minute game
                        max_min = 90
                        if int(h_shots['minute'][-1]) > max_min:
                            max_min = int(h_shots['minute'][-1])
                        if int(a_shots['minute'][-1]) > max_min:
                            max_min = int(a_shots['minute'][-1])

                        # Append match-level values to match_data
                        match_data['match_id'].append(m['id'])
                        match_data['h_team'].append(h_team)
                        match_data['a_team'].append(a_team)
                        match_data['match_code'].append(code)
                        match_data['max_min'].append(max_min)

                        # Loop through shots to get minute, home/away, xG, result, x/y coords, player who took the shot, and last action
                        for s in h_shots:
                            shot_data['match_id'].append(m['id'])
                            shot_data['minute'].append(int(s['minute']))
                            shot_data['h_a'].append(s['h_a'])
                            shot_data['xG'].append(float(s['xG']))
                            shot_data['result'].append(s['result'])
                            shot_data['x'].append(float(s['X']))
                            shot_data['y'].append(float(s['Y']))
                            shot_data['player'].append(s['player'])
                            shot_data['shot_type'].append(s['shotType'])
                            shot_data['last_action'].append(s['lastAction'])
                        for s in a_shots:
                            shot_data['match_id'].append(m['id'])
                            shot_data['minute'].append(int(s['minute']))
                            shot_data['h_a'].append(s['h_a'])
                            shot_data['xG'].append(float(s['xG']))
                            shot_data['result'].append(s['result'])
                            shot_data['x'].append(float(s['X']))
                            shot_data['y'].append(float(s['Y']))
                            shot_data['player'].append(s['player'])
                            shot_data['shot_type'].append(s['shotType'])
                            shot_data['last_action'].append(s['lastAction'])
                        
                        elapsed = time.monotonic()
                        print(f'{len(h_shots) + len(a_shots)} shots returned. {round(elapsed - clock_start,2)} seconds elapsed, of which {time_asleep} spent asleep.')
                    else:
                        match_year = int(m['datetime'][:4])
                        match_month = int(m['datetime'][5:7])
                        match_day = int(m['datetime'][8:10])
                        if datetime(match_year, match_month, match_day) >= datetime(start_year, start_month, start_day) and datetime(match_year, match_month, match_day) <= datetime(end_year, end_month, end_day):
                            # Increment counter for status messages
                            loop_counter += 1

                            # Get team names and match code
                            h_team = m['h']['title']
                            a_team = m['a']['title']
                            code = f'{m['h']['short_title']}{m['a']['short_title']}{m['datetime'][:4]}{m['datetime'][5:7]}{m['datetime'][8:10]}'

                            # Get shot data from Understat for current match
                            print(f'Getting shot data for result {loop_counter} of {total_results}. Roughly {(total_results - (loop_counter - 1))*sleep_setting} seconds remaining...')
                            time.sleep(sleep_setting)
                            time_asleep += sleep_setting
                            shots = u.match(m['id']).get_shot_data()
                            h_shots = shots['h']
                            a_shots = shots['a']

                            # Determine last minute a shot was taken or default to 90 minute game
                            max_min = 90
                            if int(h_shots[-1]['minute']) > max_min:
                                max_min = int(h_shots[-1]['minute'])
                            if int(a_shots[-1]['minute']) > max_min:
                                max_min = int(a_shots[-1]['minute'])

                            # Append match-level values to match_data
                            match_data['match_id'].append(m['id'])
                            match_data['h_team'].append(h_team)
                            match_data['a_team'].append(a_team)
                            match_data['match_code'].append(code)
                            match_data['max_min'].append(max_min)

                            # Loop through shots to get minute, home/away, xG, result, x/y coords, player who took the shot, and last action
                            for s in h_shots:
                                shot_data['match_id'].append(m['id'])
                                shot_data['minute'].append(int(s['minute']))
                                shot_data['h_a'].append(s['h_a'])
                                shot_data['xG'].append(float(s['xG']))
                                shot_data['result'].append(s['result'])
                                shot_data['x'].append(float(s['X']))
                                shot_data['y'].append(float(s['Y']))
                                shot_data['player'].append(s['player'])
                                shot_data['shot_type'].append(s['shotType'])
                                shot_data['last_action'].append(s['lastAction'])
                            for s in a_shots:
                                shot_data['match_id'].append(m['id'])
                                shot_data['minute'].append(int(s['minute']))
                                shot_data['h_a'].append(s['h_a'])
                                shot_data['xG'].append(float(s['xG']))
                                shot_data['result'].append(s['result'])
                                shot_data['x'].append(float(s['X']))
                                shot_data['y'].append(float(s['Y']))
                                shot_data['player'].append(s['player'])
                                shot_data['shot_type'].append(s['shotType'])
                                shot_data['last_action'].append(s['lastAction'])
                            
                            elapsed = time.monotonic()
                            print(f'{len(h_shots) + len(a_shots)} shots returned. {round(elapsed - clock_start,2)} seconds elapsed, of which {time_asleep} spent asleep.')
                        elif datetime(match_year, match_month, match_day) > datetime(end_year, end_month, end_day):
                            print(f'Breaking loop. No further matches before {period_end}. Shot data for {loop_counter} matches returned.')
                            break
        
    matches_df = pd.DataFrame(match_data)
    shots_df = pd.DataFrame(shot_data)

    matches_df.to_csv('./data/matches.csv', index=False)
    shots_df.to_csv('./data/raw_shots.csv')

    elapsed = time.monotonic()
    print(f'Data collected and saved to CSV files in data folder.\n\nTotal Elapsed Time: {round(elapsed - clock_start, 4)} seconds.\nTime sleeping: {time_asleep} seconds')
    return matches_df, shots_df


def get_team_shot_data(team:str, season:list[str]=None, period_start:str=None, period_end:str=None):
    '''
    Get the shot data from understat for every game for a specified team (or teams) for a given season (or seasons), for a given time period. 
    If `period_start` and `period_end` are None, return shot data for all games in the specified season (or seasons). If `season` is None, most 
    recent season is used. Function saves the data in `/data/matches.csv` and `/data/raw_shots.csv` as well as returning the pandas DataFrames.

    :param team: a list of the teams to get data for. Team names should be as they appear in the `title` for each team but with whitespaces (' ')
        replaced with underscores ('_').
    :type team: list[str] | str
    :param season: a list of the seasons to get data for. Seasons use 'YYYY' format for starting year of the league (e.g. '2025' for the 2025/26 
        Premier League season). If None, `season` will be determined as the previous year from Jan 1 to Jul 31, and current year from Aug 1 to
        Dec 31.
    :type season: list[str] | str
    :param period_start: Starting date for return period. Must be in 'YYYY-MM-DD' format. Matches played on this date included.
    :type period_start: str
    :param period_end: Ending date for return period. Must be in 'YYYY-MM-DD' format. Matches played on this date included.
    :type period_end: str

    :returns matches_df: Pandas DataFrame containing the ID `match_id`, Home Team name `h_team`, Away Team name `a_team`, Match 
        Code `match_code`, and maximum number minutes in the game `max_min`, for each match
    :rtype matches_df: pd.DataFrame
    :returns shots_df: Pandas DataFrame containing the raw shot data for all matches
    :rtype shots_df: pd.DataFrame
    '''
    print('Function under construction. Come back later.')

if __name__ == '__main__':
    leagues = ['EPL']
    season = '2025'
    period_start = '2025-09-26'
    period_end = '2025-09-29'
    matches, shots = get_league_shot_data(leagues, season, period_start, period_end)
    print('\nMatches:')
    print(matches.head())
    print('...\n\nShots:')
    print(shots.head())
    print('...')