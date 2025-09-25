import pandas as pd

# Formula for getting the probability of n goals being scored given the list of xGs
def prob(shots, n):
    result = 0
    match n:
        case 0:
            sub = 1
            for s in shots:
                sub = sub * (1-s)
            result += sub
        case 1:
            for i in range(len(shots)):
                sub = 1
                for c in range(len(shots)):
                    if c == i:
                        sub = sub * shots[c]
                    else:
                        sub = sub * (1 - shots[c])
                result += sub
        case 2:
            if len(shots) < 2:
                return 0
            for i in range(len(shots)-1):
                for j in range(i+1,len(shots)):
                    sub = 1
                    for c in range(len(shots)):
                        if c == i or c == j:
                            sub = sub * shots[c]
                        else:
                            sub = sub * (1 - shots[c])
                    result += sub
        case 3:
            if len(shots) < 3:
                return 0
            for i in range(len(shots)-2):
                for j in range(i+1,len(shots)-1):
                    for k in range(j+1,len(shots)):
                        sub = 1
                        for c in range(len(shots)):
                            if c == i or c == j or c == k:
                                sub = sub * shots[c]
                            else:
                                sub = sub * (1 - shots[c])
                        result += sub
        case _:
            raise ValueError('3 is the largest number forget about it')
    return result


matches = pd.read_csv('./data/matches.csv')
shots_all = pd.read_csv('./data/raw_shots.csv')

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
        'a_name':[],
        'a_score':[],
        'a_xG':[],
        'a_0':[],
        'a_1':[],
        'a_2':[],
        'a_3':[],
        'a_4':[],
        'code':[]
    }

    h_name = list(matches[matches['match_id'] == id]['h_team'])[0]
    a_name = list(matches[matches['match_id'] == id]['a_team'])[0]
    code = list(matches[matches['match_id'] == id]['match_code'])[0]

    shots_game = shots_all[shots_all['match_id']==id]
    h_shots = []
    a_shots = []

    for m in range(list(matches[matches['match_id']==id]['max_min'])[0] + 1):
        # Get previous minute / initial values
        if m == 0:
            h_score = 0
            h_xG = 0
            h_prob = [1,0,0,0,0]
            a_score = 0
            a_xG = 0
            a_prob = [1,0,0,0,0]
        else:
            h_score = data['h_score'][-1]
            h_xG = data['h_xG'][-1]
            h_prob = [data['h_0'][-1], data['h_1'][-1], data['h_2'][-1], data['h_3'][-1], data['h_4'][-1]]
            a_score = data['a_score'][-1]
            a_xG = data['a_xG'][-1]
            a_prob = [data['a_0'][-1], data['a_1'][-1], data['a_2'][-1], data['a_3'][-1], data['a_4'][-1]]
        
        shots_min = shots_game[shots_game['minute']==m]
        if shots_min.shape[0] > 0:
            for i in range(shots_min.shape[0]):
                if list(shots_min['h_a'])[i] == 'h':
                    h_shots.append(list(shots_min['xG'])[i])
                    h_xG += list(shots_min['xG'])[i]
                    if list(shots_min['result'])[i] == 'Goal':
                        h_score += 1
                else:
                    a_shots.append(list(shots_min['xG'])[i])
                    a_xG += list(shots_min['xG'])[i]
                    if list(shots_min['result'])[i] == 'Goal':
                        a_score += 1    
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
                data['a_name'].append(a_name)
                data['a_score'].append(a_score)
                data['a_xG'].append(a_xG)
                data['a_0'].append(a_prob[0] + (diff_a_prob[0] * (f+1)))
                data['a_1'].append(a_prob[1] + (diff_a_prob[1] * (f+1)))
                data['a_2'].append(a_prob[2] + (diff_a_prob[2] * (f+1)))
                data['a_3'].append(a_prob[3] + (diff_a_prob[3] * (f+1)))
                data['a_4'].append(a_prob[4] + (diff_a_prob[4] * (f+1)))
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
            data['a_name'].append(a_name)
            data['a_score'].append(a_score)
            data['a_xG'].append(a_xG)
            data['a_0'].append(new_a_prob[0])
            data['a_1'].append(new_a_prob[1])
            data['a_2'].append(new_a_prob[2])
            data['a_3'].append(new_a_prob[3])
            data['a_4'].append(new_a_prob[4])
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
                data['a_name'].append(a_name)
                data['a_score'].append(a_score)
                data['a_xG'].append(a_xG)
                data['a_0'].append(a_prob[0])
                data['a_1'].append(a_prob[1])
                data['a_2'].append(a_prob[2])
                data['a_3'].append(a_prob[3])
                data['a_4'].append(a_prob[4])
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
        data['a_name'].append(a_name)
        data['a_score'].append(a_score)
        data['a_xG'].append(a_xG)
        data['a_0'].append(a_prob[0])
        data['a_1'].append(a_prob[1])
        data['a_2'].append(a_prob[2])
        data['a_3'].append(a_prob[3])
        data['a_4'].append(a_prob[4])
        data['code'].append(code)
    
    # Save data to csv
    df = pd.DataFrame(data)
    df.to_csv(f'./data/{code}.csv', index=False)