import pandas as pd
from util import prob

def create_minute_data(matches:pd.DataFrame = None, shots_all:pd.DataFrame = None) -> list[pd.DataFrame]:
    '''
    Function to create minute by minute data for each match in `matches` showing on the evolving goal probabilities based on the shots in `shots_all`.
    Saves data for each match in separate CSV named after the `match_code` and returns a list of pandas DataFrames containing the data for each match
    in `matches`.

    :param matches: Pandas DataFrame containing `match_id`, `h_team`, `a_team`, `match_code`, and `min_max` at a match level. If None, data will be 
        loaded from saved CSV file. Default value: `None`
    :type matches: pd.DataFrame
    :param shots_all: Pandas DataFrame containing `match_id`, `minute`, `h_a`, `xG`, `result`, `x`, `y`, `player`, `shot_type`, and `last_action` for
        each shot taken during the matches found in `matches`. If None, data will be loaded from saved CSV file. Default value: `None`
    :type shots_all: pd.DataFrame
    :returns output: List of pandas DataFrames containing the minute by minute data for each match. Each DataFrame contains `minute`, the name of the 
        home team `h_name`, the score for the home team `h_score`, the naive xG for the home team `h_xG`, the probability of the home team having scored
        0 `h_0`, 1 `h_1`, 2 `h_2`, 3 `h_3`, and 4 or more `h_4` goals, and the most recent event for the home team `h_event_log`, with `a_name`, `a_score`,
        `a_xG`, `a_0`, `a_1`, `a_2`, `a_3`, `a_4, and `a_event_log` representing the same data for the away team.
    :rtype output: list[pd.DataFrame]
    '''
    if matches is None:
        try:
            matches = pd.read_csv('./data/matches.csv')
        except:
            raise FileNotFoundError('No matches dataframe provided and no matches.csv file found in ./data/ folder.')
    if shots_all is None:
        try:
            shots_all = pd.read_csv('./data/raw_shots.csv')
        except:
            raise FileNotFoundError('No shots_all dataframe provided and no raw_shots.csv file found in ./data/ folder.')

    output = []

    for id in matches['match_id']:
        data = {
            'minute':[],
            'h_name':[],
            'h_score':[],
            'h_xG':[],
            'h_0':[],
            'h_1':[],
            'h_2':[],
            'h_3':[],
            'h_4':[],
            'h_event_log':[],
            'a_name':[],
            'a_score':[],
            'a_xG':[],
            'a_0':[],
            'a_1':[],
            'a_2':[],
            'a_3':[],
            'a_4':[],
            'a_event_log':[],
            'code':[]
        }

        h_name = matches[matches['match_id'] == id]['h_team'].item()
        a_name = matches[matches['match_id'] == id]['a_team'].item()
        code = matches[matches['match_id'] == id]['match_code'].item()

        shots_game = shots_all[shots_all['match_id']==id]
        h_shots = []
        a_shots = []

        for m in range(matches[matches['match_id']==id]['max_min'].item() + 1):
            # Get previous minute / initial values
            if m == 0:
                h_score = 0
                h_xG = 0
                h_prob = [1,0,0,0,0]
                h_events = ''
                a_score = 0
                a_xG = 0
                a_prob = [1,0,0,0,0]
                a_events = ''
            else:
                h_score = data['h_score'][-1]
                h_xG = data['h_xG'][-1]
                h_prob = [data['h_0'][-1], data['h_1'][-1], data['h_2'][-1], data['h_3'][-1], data['h_4'][-1]]
                h_events = data['h_event_log'][-1]
                a_score = data['a_score'][-1]
                a_xG = data['a_xG'][-1]
                a_prob = [data['a_0'][-1], data['a_1'][-1], data['a_2'][-1], data['a_3'][-1], data['a_4'][-1]]
                a_events = data['a_event_log'][-1]
                
            
            shots_min = shots_game[shots_game['minute']==m].reset_index()
            if shots_min.shape[0] > 0:
                # Append first shot to the current attack
                attack = [shots_min['xG'][0]]
                attack_result = [shots_min['result'][0]]
                attack_h_a = [shots_min['h_a'][0]]
                attack_players = [shots_min['player'][0]]

                for i in range(1,shots_min.shape[0]):
                    if shots_min['last_action'][i] == 'Rebound':
                        # Append any rebounded shots to the current attack
                        attack.append(shots_min['xG'][i])
                        attack_result.append(shots_min['result'][i])
                        attack_h_a.append(shots_min['h_a'][i])
                        attack_players.append(shots_min['player'][i])
                    else:
                        # Otherwise get probability & result from the current attack and append it to h_shots/a_shots, and update the xG and score
                        attack_xG = 1 - prob(attack,0)
                        if attack_h_a[-1] == 'h':
                            h_shots.append(attack_xG)
                            h_xG += attack_xG
                            if attack_result[-1] == 'Goal':
                                h_score += 1
                                if len(attack) > 1:
                                    h_events = f'{m}\': Goal scored by {attack_players[-1]} from an attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                                else:
                                    h_events = f'{m}\': Goal scored by {attack_players[-1]} from a shot worth {round(attack_xG,2)} xG'
                            elif attack_result[-1] == 'OwnGoal':
                                a_score += 1
                                h_events = f'{m}\': Own goal scored by {attack_players[-1]}'
                            else:
                                if len(attack) > 1:
                                    h_events = f'{m}\': Attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                                else:
                                    h_events = f'{m}\': Shot by {attack_players[-1]} worth {round(attack_xG,2)} xG'
                            
                        else:
                            a_shots.append(attack_xG)
                            a_xG += attack_xG
                            if attack_result[-1] == 'Goal':
                                a_score += 1
                                if len(attack) > 1:
                                    a_events = f'{m}\': Goal scored by {attack_players[-1]} from an attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                                else:
                                    a_events = f'{m}\': Goal scored by {attack_players[-1]} from a shot worth {round(attack_xG,2)} xG'
                            elif attack_result[-1] == 'OwnGoal':
                                h_score += 1
                                a_events = f'{m}\': Own goal scored by {attack_players[-1]}'
                            else:
                                if len(attack) > 1:
                                    a_events = f'{m}\': Attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                                else:
                                    a_events = f'{m}\': Shot by {attack_players[-1]} worth {round(attack_xG,2)} xG'
                        # Reset the current attack to include only the most recent shot
                        attack = [shots_min['xG'][i]]
                        attack_result = [shots_min['result'][i]]
                        attack_h_a = [shots_min['h_a'][i]]
                        attack_players = [shots_min['player'][i]]
                
                # Deal with the contents of the final current attack of the current minute
                attack_xG = 1 - prob(attack, 0)
                if attack_h_a[-1] == 'h':
                    h_shots.append(attack_xG)
                    h_xG += attack_xG
                    if attack_result[-1] == 'Goal':
                        h_score += 1
                        if len(attack) > 1:
                            h_events = f'{m}\': Goal scored by {attack_players[-1]} from an attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                        else:
                            h_events = f'{m}\': Goal scored by {attack_players[-1]} from a shot worth {round(attack_xG,2)} xG'
                    elif attack_result[-1] == 'OwnGoal':
                        a_score += 1
                        h_events = f'{m}\': Own goal scored by {attack_players[-1]}'
                    else:
                        if len(attack) > 1:
                            h_events = f'{m}\': Attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                        else:
                            h_events = f'{m}\': Shot by {attack_players[-1]} worth {round(attack_xG,2)} xG'
                else:
                    a_shots.append(attack_xG)
                    a_xG += attack_xG
                    if attack_result[-1] == 'Goal':
                        a_score += 1
                        if len(attack) > 1:
                            a_events = f'{m}\': Goal scored by {attack_players[-1]} from an attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                        else:
                            a_events = f'{m}\': Goal scored by {attack_players[-1]} from a shot worth {round(attack_xG,2)} xG'
                    elif attack_result[-1] == 'OwnGoal':
                        h_score += 1
                        a_events = f'{m}\': Own goal scored by {attack_players[-1]}'
                    else:
                        if len(attack) > 1:
                            a_events = f'{m}\': Attack with {len(attack)} shots worth {round(attack_xG,2)} xG'
                        else:
                            a_events = f'{m}\': Shot by {attack_players[-1]} worth {round(attack_xG,2)} xG'
                
                new_h_prob = [prob(h_shots,0), prob(h_shots,1), prob(h_shots,2), prob(h_shots,3)]
                new_h_prob.append(1 - (new_h_prob[0] + new_h_prob[1] + new_h_prob[2] + new_h_prob[3]))
                new_a_prob = [prob(a_shots,0),prob(a_shots,1),prob(a_shots,2),prob(a_shots,3)]
                new_a_prob.append(1 - (new_a_prob[0] + new_a_prob[1] + new_a_prob[2] + new_a_prob[3]))
                diff_h_prob = []
                diff_a_prob = []
                for j in range(5):
                    diff_h_prob.append((new_h_prob[j] - h_prob[j])/5)
                    diff_a_prob.append((new_a_prob[j] - a_prob[j])/5)
                
                # lerping probability values for smoother transition in animation
                for f in range(4):
                    data['minute'].append(m)
                    data['h_name'].append(h_name)
                    data['h_score'].append(h_score)
                    data['h_xG'].append(h_xG)
                    data['h_0'].append(h_prob[0] + (diff_h_prob[0] * (f+1)))
                    data['h_1'].append(h_prob[1] + (diff_h_prob[1] * (f+1)))
                    data['h_2'].append(h_prob[2] + (diff_h_prob[2] * (f+1)))
                    data['h_3'].append(h_prob[3] + (diff_h_prob[3] * (f+1)))
                    data['h_4'].append(h_prob[4] + (diff_h_prob[4] * (f+1)))
                    data['h_event_log'].append(h_events)
                    data['a_name'].append(a_name)
                    data['a_score'].append(a_score)
                    data['a_xG'].append(a_xG)
                    data['a_0'].append(a_prob[0] + (diff_a_prob[0] * (f+1)))
                    data['a_1'].append(a_prob[1] + (diff_a_prob[1] * (f+1)))
                    data['a_2'].append(a_prob[2] + (diff_a_prob[2] * (f+1)))
                    data['a_3'].append(a_prob[3] + (diff_a_prob[3] * (f+1)))
                    data['a_4'].append(a_prob[4] + (diff_a_prob[4] * (f+1)))
                    data['a_event_log'].append(a_events)
                    data['code'].append(code)
                data['minute'].append(m)
                data['h_name'].append(h_name)
                data['h_score'].append(h_score)
                data['h_xG'].append(h_xG)
                data['h_0'].append(new_h_prob[0])
                data['h_1'].append(new_h_prob[1])
                data['h_2'].append(new_h_prob[2])
                data['h_3'].append(new_h_prob[3])
                data['h_4'].append(new_h_prob[4])
                data['h_event_log'].append(h_events)
                data['a_name'].append(a_name)
                data['a_score'].append(a_score)
                data['a_xG'].append(a_xG)
                data['a_0'].append(new_a_prob[0])
                data['a_1'].append(new_a_prob[1])
                data['a_2'].append(new_a_prob[2])
                data['a_3'].append(new_a_prob[3])
                data['a_4'].append(new_a_prob[4])
                data['a_event_log'].append(a_events)
                data['code'].append(code)
            else:
                for i in range(5):
                    data['minute'].append(m)
                    data['h_name'].append(h_name)
                    data['h_score'].append(h_score)
                    data['h_xG'].append(h_xG)
                    data['h_0'].append(h_prob[0])
                    data['h_1'].append(h_prob[1])
                    data['h_2'].append(h_prob[2])
                    data['h_3'].append(h_prob[3])
                    data['h_4'].append(h_prob[4])
                    data['h_event_log'].append(h_events)
                    data['a_name'].append(a_name)
                    data['a_score'].append(a_score)
                    data['a_xG'].append(a_xG)
                    data['a_0'].append(a_prob[0])
                    data['a_1'].append(a_prob[1])
                    data['a_2'].append(a_prob[2])
                    data['a_3'].append(a_prob[3])
                    data['a_4'].append(a_prob[4])
                    data['a_event_log'].append(a_events)
                    data['code'].append(code)

        # Add 20 frames holding on the final value
        h_score = data['h_score'][-1]
        h_xG = data['h_xG'][-1]
        h_prob = [data['h_0'][-1], data['h_1'][-1], data['h_2'][-1], data['h_3'][-1], data['h_4'][-1]]
        a_score = data['a_score'][-1]
        a_xG = data['a_xG'][-1]
        a_prob = [data['a_0'][-1], data['a_1'][-1], data['a_2'][-1], data['a_3'][-1], data['a_4'][-1]]
        for f in range(20):
            data['minute'].append(m)
            data['h_name'].append(h_name)
            data['h_score'].append(h_score)
            data['h_xG'].append(h_xG)
            data['h_0'].append(h_prob[0])
            data['h_1'].append(h_prob[1])
            data['h_2'].append(h_prob[2])
            data['h_3'].append(h_prob[3])
            data['h_4'].append(h_prob[4])
            data['h_event_log'].append(h_events)
            data['a_name'].append(a_name)
            data['a_score'].append(a_score)
            data['a_xG'].append(a_xG)
            data['a_0'].append(a_prob[0])
            data['a_1'].append(a_prob[1])
            data['a_2'].append(a_prob[2])
            data['a_3'].append(a_prob[3])
            data['a_4'].append(a_prob[4])
            data['a_event_log'].append(a_events)
            data['code'].append(code)
        
        # Save data to csv
        df = pd.DataFrame(data)
        df.to_csv(f'./data/{code}.csv', index=False)
        output.append(df)

    return output

if __name__=='__main__':
    create_minute_data()