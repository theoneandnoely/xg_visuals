import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

team_colours = {
    'Arsenal':['red','white'],
    'Aston Villa':['lightskyblue','maroon'],
    'Bournemouth':['firebrick','black'],
    'Brentford':['red','white'],
    'Brighton':['blue','yellow'],
    'Burnley':['mediumvioletred','turquoise'],
    'Chelsea':['blue','powderblue'],
    'Crystal Palace':['blue','red'],
    'Everton':['blue','white'],
    'Fulham':['white','black'],
    'Leeds':['yellow','blue'],
    'Liverpool':['red','yellow'],
    'Manchester City':['skyblue','white'],
    'Manchester United':['red','black'],
    'Newcastle United':['black','white'],
    'Nottingham Forest':['red','white'],
    'Sunderland':['red','gold'],
    'Tottenham':['white','navy'],
    'West Ham':['maroon','deepskyblue'],
    'Wolverhampton Wanderers':['orange','black']
}
clash = {
    'red':{'red','firebrick','orange','mediumvioletred','maroon'},
    'white':{'white'},
    'lightskyblue':{'lightskyblue','turquoise','powderblue','skyblue','deepskyblue'},
    'maroon':{'maroon','red','firebrick','mediumvioletred','orange'},
    'firebrick':{'firebrick','red','maroon','mediumvioletred','orange'},
    'black':{'black','navy'},
    'blue':{'blue','deepskyblue','navy'},
    'yellow':{'yellow','gold','orange'},
    'mediumvioletred':{'mediumvioletred','red','maroon','firebrick','orange'},
    'turquoise':{'turquoise','lightskyblue','powderblue','skyblue','deepskyblue'},
    'powderblue':{'powderblue','lightskyblue','turquoise','skyblue','deepskyblue'},
    'skyblue':{'skyblue','lightskyblue','turquoise','powderblue','deepskyblue'},
    'gold':{'gold','yellow'},
    'navy':{'navy','blue','black'},
    'deepskyblue':{'deepskyblue','lightskyblue','blue','turquoise','powderblue','skyblue'},
    'orange':{'orange','red','maroon','firebrick','mediumvioletred'}
}

matches = pd.read_csv('./data/matches.csv')
for m in list(matches['match_code']):
    data = pd.read_csv(f'./data/{m}.csv')

    h_name = list(data['h_name'])[0]
    h_colours = team_colours[h_name]

    a_name = list(data['a_name'])[0]
    if team_colours[a_name][0] in clash[h_colours[0]]:
        a_colours = [team_colours[a_name][1], team_colours[a_name][0]]
    else:
        a_colours = team_colours[a_name]
    
    h_score = [list(data['h_score'])[0]]
    a_score = [list(data['a_score'])[0]]
    h_xG = [list(data['h_xG'])[0]]
    a_xG = [list(data['a_xG'])[0]]
    h_prob = [list(data['h_0'])[0], list(data['h_1'])[0], list(data['h_2'])[0], list(data['h_3'])[0], list(data['h_4'])[0]]
    a_prob = [list(data['a_0'])[0], list(data['a_1'])[0], list(data['a_2'])[0], list(data['a_3'])[0], list(data['a_4'])[0]]

    fig, ax = plt.subplots(1,2)

    fig.set_facecolor('navajowhite')
    fig.suptitle(f'0\': {h_score[0]} ({round(h_xG[0],2)}) - ({round(a_xG[0],2)}) {a_score[0]}')
    
    ax[0].barh(range(len(h_prob)), h_prob, color=h_colours[0], edgecolor=h_colours[1])
    ax[1].barh(range(len(a_prob)), a_prob, color=a_colours[0], edgecolor=a_colours[1])
    ax[0].set_facecolor('papayawhip')
    ax[0].set_xlim(1,0)
    ax[0].set_yticks(range(5), labels=["0","1","2","3","4+"])
    ax[0].set_ylabel('# Goals')
    ax[0].set_xticks([1,0.8,0.6,0.4,0.2,0], labels=["100", "80", "60", "40", "20", "0"])
    ax[0].set_xlabel('Probability (%)')
    ax[0].invert_yaxis()
    ax[0].set_title(h_name)
    ax[0].spines['left'].set_visible(False)
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].set_axisbelow(True)
    ax[0].grid(True, color='wheat', axis='x', zorder=0)

    ax[1].set_facecolor('papayawhip')
    ax[1].set_xlim(0,1)
    ax[1].set_yticks(range(5), labels=["0","1","2","3","4+"])
    ax[1].set_ylabel('# Goals')
    ax[1].set_xticks([0,0.2,0.4,0.6,0.8,1], labels=["0","20","40","60","80","100"])
    ax[1].set_xlabel('Probability (%)')
    ax[1].yaxis.set_label_position('right')
    ax[1].yaxis.set_ticks_position('right')
    ax[1].invert_yaxis()
    ax[1].set_title(a_name)
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['top'].set_visible(False)
    ax[1].spines['bottom'].set_visible(False)
    ax[1].set_axisbelow(True)
    ax[1].grid(True, color='wheat', axis='x', zorder=0)

    def update(f):
        h_prob = [list(data['h_0'])[f], list(data['h_1'])[f], list(data['h_2'])[f], list(data['h_3'])[f], list(data['h_4'])[f]]
        a_prob = [list(data['a_0'])[f], list(data['a_1'])[f], list(data['a_2'])[f], list(data['a_3'])[f], list(data['a_4'])[f]]
        for r in range(len(ax[0].patches)):
            ax[0].patches[r].set_width(h_prob[r])
            ax[1].patches[r].set_width(a_prob[r])
        fig.suptitle(f'{list(data['minute'])[f]}\': {list(data['h_score'])[f]} ({round(list(data['h_xG'])[f],2)}) - ({round(list(data['a_xG'])[f],2)}) {list(data['a_score'])[f]}')
    
    ani = FuncAnimation(fig, update, frames=range(data.shape[0]), interval=25, repeat=False)
    ani.save(f'./output/{m}.gif','pillow',fps=30)
    plt.close(fig)