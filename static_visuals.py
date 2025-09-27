import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from util import prob
# from PIL import Image
# from cairosvg import svg2png
# from io import BytesIO

# import shot and match data
matches = pd.read_csv('./data/matches.csv')
shots_all = pd.read_csv('./data/raw_shots.csv')

team_colours = {
    'Arsenal':['red','white'],
    'Aston Villa':['maroon','lightskyblue'],
    'Bournemouth':['firebrick','black'],
    'Brentford':['red','white'],
    'Brighton':['deepskyblue','white'],
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
    'red':{'red'},
    'white':{'white'},
    'lightskyblue':{'lightskyblue'},
    'maroon':{'maroon'},
    'firebrick':{'firebrick'},
    'black':{'black'},
    'blue':{'blue'},
    'yellow':{'yellow'},
    'mediumvioletred':{'mediumvioletred'},
    'turquoise':{'turquoise'},
    'powderblue':{'powderblue'},
    'skyblue':{'skyblue'},
    'gold':{'gold'},
    'navy':{'navy'},
    'deepskyblue':{'deepskyblue'},
    'orange':{'orange'}
}

for m in matches['match_id']:
    # Get Team names from match record
    h_team = matches[matches['match_id']==m]['h_team'].item()
    a_team = matches[matches['match_id']==m]['a_team'].item()
    
    # Set colours
    h_colour = team_colours[h_team]
    if team_colours[a_team][0] in clash[h_colour[0]]:
        a_colour = [team_colours[a_team][1], team_colours[a_team][0]]
    else:
        a_colour = team_colours[a_team]
    bg_colour = 'seashell'

    # Filter shot data to just the shots for this match per team
    shots = shots_all[shots_all['match_id']==m]
    h_shots = shots[shots['h_a']=='h'].reset_index()
    a_shots = shots[shots['h_a']=='a'].reset_index()
    
    # Get the score, naive xG, probability of scoring exactly n goals, and the probability of scoring at least n goals
    h_score = h_shots[h_shots['result']=='Goal'].shape[0] + a_shots[a_shots['result']=='OwnGoal'].shape[0]
    a_score = a_shots[a_shots['result']=='Goal'].shape[0] + h_shots[h_shots['result']=='OwnGoal'].shape[0]
    h_xG = h_shots['xG'].sum()
    a_xG = a_shots['xG'].sum()
    h_prob = []
    a_prob = []
    for i in range(4):
        h_prob.append(prob(h_shots['xG'],i))
        a_prob.append(prob(a_shots['xG'],i))
    h_prob.append(1-sum(h_prob))
    a_prob.append(1-sum(a_prob))
    h_at_least = [0]
    a_at_least = [0]
    for i in range(1,5):
        h_at_least.append(sum(h_prob[i:]))
        a_at_least.append(sum(a_prob[i:]))

    # Set up mpl figure so subplots share centre axis
    fig, ax = plt.subplots(1,2)
    fig.subplots_adjust(wspace=0)

    # Add bars for exact and at least probabilities
    ax[0].barh(range(5), h_prob, color=h_colour[0], zorder=3)
    ax[1].barh(range(5), a_prob, color=a_colour[0], zorder=3)
    ax[0].barh(range(5), h_at_least, color=h_colour[1], hatch='//', edgecolor=h_colour[0], zorder=2)
    ax[1].barh(range(5), a_at_least, color=a_colour[1], hatch='//', edgecolor=a_colour[0], zorder=2)

    # Set background colour as well as shared formatting for subplots
    fig.set_facecolor(bg_colour)
    for a in ax:
        a.set_facecolor(bg_colour)
        a.set_yticks(range(5), labels=["0","1","2","3","4+"])
        a.set_ylabel('Goals Scored')
        a.invert_yaxis()
        a.spines['top'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.grid(True, color='0.85', axis='x', zorder=1)

    # Set inverted formatting for subplots
    ax[0].set_xlim(1.05,0)
    ax[0].set_xticks([1,.9,.8,.7,.6,.5,.4,.3,.2,.1,0], labels=range(100,-10,-10))
    ax[0].set_xlabel('Probability (%)')
    ax[0].spines['left'].set_visible(False)
    ax[0].spines['right'].set(zorder=4)

    ax[1].set_xlim(0,1.05)
    ax[1].set_xticks([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1], labels=range(0,105,10))
    ax[1].set_xlabel('Probability (%)')
    ax[1].yaxis.set_label_position('right')
    ax[1].yaxis.set_ticks_position('right')
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['left'].set(zorder=4)

    # Create legend
    labels = ['Scored Exactly', 'Scored At Least']
    handles = [plt.Rectangle((0,0),1,1,color='black'), plt.Rectangle((0,0),1,1,facecolor='white',hatch='//',edgecolor='black')]
    ax[1].legend(labels=labels, handles=handles, loc='lower right', fancybox=False, framealpha=0.5)

    # Add Header Text
    ax[0].text(0.5, -1.25, h_team, size='large', ha='center', weight='bold')
    ax[0].text(0.5, -1, h_score, size='medium', ha='center', weight='bold')
    ax[0].text(0.5, -0.75, f'({round(h_xG,2)})', size='medium', ha='center', weight='normal')
    ax[1].text(0.5, -1.25, a_team, size='large', ha='center', weight='bold')
    ax[1].text(0.5, -1, a_score, size='medium', ha='center', weight='bold')
    ax[1].text(0.5, -0.75, f'({round(a_xG,2)})', size='medium', ha='center', weight='normal')

    fig.savefig(f'./output/static/{matches[matches['match_id']==m]['match_code'].item()}.png', bbox_inches='tight')
    plt.close(fig)
    print(f'{matches[matches['match_id']==m]['match_code'].item()} graph saved')