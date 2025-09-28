import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from util import prob
from PIL import Image

import os
folder_path = os.path.abspath('./venv/Lib/site-packages/cairo/bin/')
path_env = os.environ['PATH']
if folder_path not in path_env:
    os.environ['PATH'] = folder_path + os.pathsep + path_env

from cairosvg import svg2png
from io import BytesIO

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

    # Get team crests and convert to png BytesIO buffers
    h_crest_bytes = BytesIO(svg2png(url=f'./icons/{h_team}.svg'))
    a_crest_bytes = BytesIO(svg2png(url=f'./icons/{a_team}.svg'))
    h_crest = Image.open(h_crest_bytes)
    h_width_to_height = h_crest.size[0]/h_crest.size[1]
    a_crest = Image.open(a_crest_bytes)
    a_width_to_height = a_crest.size[0]/a_crest.size[1]
    
    # Set colours
    h_colour = team_colours[h_team]
    if team_colours[a_team][0] in clash[h_colour[0]]:
        a_colour = [team_colours[a_team][1], team_colours[a_team][0]]
    else:
        a_colour = team_colours[a_team]
    bg_colour = "seashell"
    text_colour = "black"

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
    h_at_least = [h_prob[0]]
    a_at_least = [a_prob[0]]
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

    # Add outline bar if block colour is white
    if h_colour[0] == 'white':
        ax[0].barh(range(5), h_at_least, fill=False, edgecolor=h_colour[1], zorder=3)
    if a_colour[0] == 'white':
        ax[1].barh(range(5), a_at_least, fill=False, edgecolor=a_colour[1], zorder=3)

    # Set background colour as well as shared formatting for subplots
    fig.set_facecolor(bg_colour)
    for a in ax:
        a.set_facecolor(bg_colour)
        a.set_yticks(range(5), labels=["0","1","2","3","4+"], color=text_colour)
        a.tick_params(axis='y',length=0)
        a.set_ylabel('Goals Scored', color=text_colour)
        a.invert_yaxis()
        a.spines['top'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.grid(True, color='0.85', axis='x', zorder=1)

    # Set inverted formatting for subplots
    ax[0].set_xlim(1.05,0)
    ax[0].set_xticks([1,.9,.8,.7,.6,.5,.4,.3,.2,.1,0], labels=range(100,-10,-10), color=text_colour)
    ax[0].set_xlabel('Probability (%)', color=text_colour)
    ax[0].spines['left'].set_visible(False)
    ax[0].spines['right'].set(zorder=4)

    ax[1].set_xlim(0,1.05)
    ax[1].set_xticks([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1], labels=range(0,105,10), color=text_colour)
    ax[1].set_xlabel('Probability (%)', color=text_colour)
    ax[1].yaxis.set_label_position('right')
    ax[1].yaxis.set_ticks_position('right')
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['left'].set(zorder=4)

    # Create legend
    labels = ['Scored Exactly', 'Scored At Least']
    handles = [plt.Rectangle((0,0),1,1,color='black'), plt.Rectangle((0,0),1,1,facecolor='white',hatch='//',edgecolor='black')]
    ax[1].legend(labels=labels, handles=handles, loc='lower right', fancybox=False, framealpha=0.5)

    # Add Header Text
    match h_team:
        case 'Wolverhampton Wanderers':
            ax[0].text(0.75, -1.25, 'Wolves', size='large', ha='left', weight='bold', color=text_colour)
        case 'Tottenham':
            ax[0].text(0.75, -1.25, 'Spurs', size='large', ha='left', weight='bold', color=text_colour)
        case _:
            ax[0].text(0.75, -1.25, h_team, size='large', ha='left', weight='bold', color=text_colour)
    ax[0].text(0.75, -1, h_score, size='medium', ha='left', weight='bold', color=text_colour)
    ax[0].text(0.75, -0.75, f'({round(h_xG,2)})', size='medium', ha='left', weight='normal', color=text_colour)
    match a_team:
        case 'Wolverhampton Wanderers':
            ax[1].text(0.75, -1.25, 'Wolves', size='large', ha='right', weight='bold', color=text_colour)
        case 'Tottenham':
            ax[1].text(0.75, -1.25, 'Spurs', size='large', ha='right', weight='bold', color=text_colour)
        case _:
            ax[1].text(0.75, -1.25, a_team, size='large', ha='right', weight='bold', color=text_colour)
    ax[1].text(0.75, -1, a_score, size='medium', ha='right', weight='bold', color=text_colour)
    ax[1].text(0.75, -0.75, f'({round(a_xG,2)})', size='medium', ha='right', weight='normal', color=text_colour)

    # Add Team Crests to Header
    print(f'{h_team}: {h_width_to_height}')
    if h_width_to_height >= 1:
        ax_h_crest = plt.axes([0.1,0.9,0.1,0.1])
    else:
        offset = (1-h_width_to_height)/20
        ax_h_crest = plt.axes([0.1+offset,0.9,0.1-offset,0.1])
    ax_h_crest.imshow(h_crest)
    ax_h_crest.set_zorder(5)
    ax_h_crest.axis('off')
    ax_a_crest = plt.axes([0.8,0.9,0.1,0.1])
    ax_a_crest.imshow(a_crest)
    ax_a_crest.set_zorder(5)
    ax_a_crest.axis('off')

    fig.savefig(f'./output/static/{matches[matches['match_id']==m]['match_code'].item()}.png', bbox_inches='tight')
    plt.close(fig)
    print(f'{matches[matches['match_id']==m]['match_code'].item()} graph saved')