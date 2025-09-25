from understatapi import UnderstatClient
import time
import pandas as pd


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
    'shot_type':[]
}

u = UnderstatClient()
matches = u.league(league='EPL').get_match_data(season='2025')
for m in matches:
    if m['isResult']:
        h_team = m['h']['title']
        a_team = m['a']['title']
        code = f'{m['h']['short_title']}{m['a']['short_title']}{m['datetime'][:4]}{m['datetime'][5:7]}{m['datetime'][8:10]}'
        
        time.sleep(3) # 3 seconds appears to be working to not cause issues but delay can definitely be upped if needed
        shots = u.match(m['id']).get_shot_data()
        h_shots = shots['h']
        a_shots = shots['a']

        max_min = 90
        if int(h_shots[-1]['minute']) > max_min:
            max_min = int(h_shots[-1]['minute'])
        if int(a_shots[-1]['minute']) > max_min:
            max_min = int(a_shots[-1]['minute'])
        
        match_data['match_id'].append(m['id'])
        match_data['h_team'].append(h_team)
        match_data['a_team'].append(a_team)
        match_data['match_code'].append(code)
        match_data['max_min'].append(max_min)

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

match_df = pd.DataFrame(match_data)
shots_df = pd.DataFrame(shot_data)

match_df.to_csv('./data/matches.csv',index=False)
shots_df.to_csv('./data/raw_shots.csv')