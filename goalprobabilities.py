from understatapi import UnderstatClient
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

u = UnderstatClient()

colours = {
    'Manchester United':['red','black'],
    'Arsenal':['red','white'],
    'Fulham':['white','black'],
    'Burnley':['palevioletred','aqua'],
    'Manchester City':['skyblue','white'],
    'Brentford':['red','white'],
    'Chelsea':['blue','white']
}

team_match_data = u.team(team="Manchester_United").get_match_data(season="2025")
match_ids = []
for m in team_match_data:
    if m['isResult']:
        match_ids.append({'id':m['id'],'h':m['h']['title'],'a':m['a']['title'],'score':m['goals'],'datetime':m['datetime']})

# Probability Functions
def zero_prob(shots):
    result = 1
    for s in shots:
        result = result * (1-s)
    return result

def one_prob(shots):
    total = 0
    for i in range(len(shots)):
        sub = None
        for cursor in range(len(shots)):
            if cursor == i:
                if sub == None:
                    sub = shots[cursor]
                else:
                    sub = sub * shots[cursor]
            else:
                if sub == None:
                    sub = 1 - shots[cursor]
                else:
                    sub = sub * (1 - shots[cursor])
        total += sub
    return total

def two_prob(shots):
    total = 0
    for i in range(len(shots)-1):
        for j in range(i+1,len(shots)):
            sub = None
            for cursor in range(len(shots)):
                if cursor == i or cursor == j:
                    if sub == None:
                        sub = shots[cursor]
                    else:
                        sub = sub * shots[cursor]
                else:
                    if sub == None:
                        sub = 1 - shots[cursor]
                    else:
                        sub = sub * (1 - shots[cursor])
            total += sub
    return total

def three_prob(shots):
    total = 0
    for i in range(len(shots)-2):
        for j in range(i+1,len(shots)-1):
            for k in range(j+1,len(shots)):
                sub = None
                for cursor in range(len(shots)):
                    if cursor == i or cursor == j or cursor == k:
                        if sub == None:
                            sub = shots[cursor]
                        else:
                            sub = sub * shots[cursor]
                    else:
                        if sub == None:
                            sub = 1 - shots[cursor]
                        else:
                            sub = sub * (1 - shots[cursor])
                total += sub
    return total

for id in match_ids:
    time.sleep(3)
    shot_data = u.match(id['id']).get_shot_data()
    max_min = 90
    if int(shot_data['h'][-1]['minute']) > max_min:
        max_min = int(shot_data['h'][-1]['minute'])
    if int(shot_data['a'][-1]['minute']) > max_min:
        max_min = int(shot_data['a'][-1]['minute'])

    h_name = id['h']
    a_name = id['a']

    h_score = [0]
    a_score = [0]
    h_xG = [0]
    a_xG = [0]
    h_shots = []
    a_shots = []
    h_prob = [1,0,0,0,0]
    a_prob = [1,0,0,0,0]

    fig, ax = plt.subplots(1,2)
    h_bar = ax[0].barh(range(len(h_prob)),h_prob, color=colours[h_name][0], edgecolor=colours[h_name][1])
    a_bar = ax[1].barh(range(len(a_prob)),a_prob, color=colours[a_name][1], edgecolor=colours[a_name][0])
    fig.set_facecolor('0.6')
    fig.suptitle(f'0\': {h_score[0]} ({round(h_xG[0],2)}) - ({round(a_xG[0],2)}) {a_score[0]} ')
    ax[0].set_facecolor('0.9')
    ax[0].set_xlim(1,0)
    ax[0].set_yticks(range(5), labels=["0","1","2","3","4+"])
    ax[0].set_ylabel('# Goals')
    ax[0].set_xlabel('Probability')
    ax[0].invert_yaxis()
    ax[0].set_title(h_name)
    ax[1].set_facecolor('0.9')
    ax[1].set_xlim(0,1)
    ax[1].set_yticks(range(5), labels=["0","1","2","3","4+"])
    ax[1].set_ylabel('# Goals')
    ax[1].set_xlabel('Probability')
    ax[1].yaxis.set_label_position('right')
    ax[1].yaxis.set_ticks_position('right')
    ax[1].invert_yaxis()
    ax[1].set_title(a_name)

    def update(m):
        for s in shot_data['h']:
            if int(s['minute']) == m+1:
                h_shots.append(float(s['xG']))
                h_xG.append(h_xG[-1] + float(s['xG']))
                if s['result'] == 'Goal':
                    h_score.append(h_score[-1] + 1)
        
        for s in shot_data['a']:
            if int(s['minute']) == m+1:
                a_shots.append(float(s['xG']))
                a_xG.append(a_xG[-1] + float(s['xG']))
                if s['result'] == 'Goal':
                    a_score.append(a_score[-1] + 1)

        match len(h_shots):
            case 0:
                h_prob = [1,0,0,0,0]
            case 1:
                h_prob = [1 - h_shots[0], h_shots[0], 0, 0, 0]
            case 2:
                h_prob = [zero_prob(h_shots), one_prob(h_shots), two_prob(h_shots), 0, 0]
            case _:
                h_prob = [zero_prob(h_shots), one_prob(h_shots), two_prob(h_shots), three_prob(h_shots), 0]
                h_prob[4] = 1 - (h_prob[0] + h_prob[1] + h_prob[2] + h_prob[3])
        
        match len(a_shots):
            case 0:
                a_prob = [1,0,0,0,0]
            case 1:
                a_prob = [1 - a_shots[0], a_shots[0], 0, 0, 0]
            case 2:
                a_prob = [zero_prob(a_shots), one_prob(a_shots), two_prob(a_shots), 0, 0]
            case _:
                a_prob = [zero_prob(a_shots), one_prob(a_shots), two_prob(a_shots), three_prob(a_shots), 0]
                a_prob[4] = 1 - (a_prob[0] + a_prob[1] + a_prob[2] + a_prob[3])

        for r in range(len(ax[0].patches)):
            ax[0].patches[r].set_width(h_prob[r])
            ax[1].patches[r].set_width(a_prob[r])
        fig.suptitle(f'{m+1}\': {h_score[-1]} ({round(h_xG[-1],2)}) - ({round(a_xG[-1],2)}) {a_score[-1]}')


    ani = FuncAnimation(fig, update, frames=max_min, interval=100, repeat=False)
    ani.save(f'./output/{h_name} v {a_name}.gif','pillow', fps=10)


# print(f'{m}\' Minute:')
# print(f'Teams:\t\t| {match_ids[0]['h'].ljust(20)}|{match_ids[0]['a'].rjust(20)} |')
# print(f'Score:\t\t| {str(h_score).ljust(20)}|{str(a_score).rjust(20)} |')
# print(f'xG:\t\t| {str(round(h_xG,4)).ljust(20)}|{str(round(a_xG,4)).rjust(20)} |')
# print(f'P(0 Goals):\t| {str(round(h_0_prob * 100,2)).ljust(18)}% | %{str(round(a_0_prob * 100,2)).rjust(18)} |')
# print(f'P(1 Goals):\t| {str(round(h_1_prob * 100,2)).ljust(18)}% | %{str(round(a_1_prob * 100,2)).rjust(18)} |')
# print(f'P(2 Goals):\t| {str(round(h_2_prob * 100,2)).ljust(18)}% | %{str(round(a_2_prob * 100,2)).rjust(18)} |')
# print(f'P(3 Goals):\t| {str(round(h_3_prob * 100,2)).ljust(18)}% | %{str(round(a_3_prob * 100,2)).rjust(18)} |')
# print(f'P(4+ Goals):\t| {str(round(h_4_plus_prob * 100,2)).ljust(18)}% | %{str(round(a_4_plus_prob * 100,2)).rjust(18)} |')
# print('\n')
    

# print(f"{match_ids[0]['h']} - {match_ids[0]['a']} ({match_ids[0]['score']['h']} - {match_ids[0]['score']['a']}):")
# print(shot_data)