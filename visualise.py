import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import time
from PIL import Image

import os
folder_path = os.path.abspath('./venv/Lib/site-packages/cairo/bin/')
path_env = os.environ['PATH']
if folder_path not in path_env:
    os.environ['PATH'] = folder_path + os.pathsep + path_env

from cairosvg import svg2png
from io import BytesIO

start_start = time.monotonic()

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
start = time.monotonic()
matches = pd.read_csv('./data/matches.csv')
end = time.monotonic()
print(f'Matches DataFrame loaded in {round(end - start,4)} seconds.')

counter = 0
for m in matches['match_code']:
    counter += 1
    print(f'-----------------\nMatch {counter} of {matches.shape[0]}: {m}')

    # Get per frame data
    start = time.monotonic()
    data = pd.read_csv(f'./data/{m}.csv')
    end = time.monotonic()
    print(f'Data for {m} loaded in {round(end - start,4)} seconds.')

    start = time.monotonic()
    # Get team names and colours
    h_name = data['h_name'][0]
    h_colours = team_colours[h_name]
    a_name = data['a_name'][0]
    if team_colours[a_name][0] in clash[h_colours[0]]:
        a_colours = [team_colours[a_name][1], team_colours[a_name][0]]
    else:
        a_colours = team_colours[a_name]
    bg_colour = 'seashell'
    text_colour = 'black'

    # Get team crests and convert to png BytesIO buffers
    h_crest_bytes = BytesIO(svg2png(url=f'./icons/{h_name}.svg'))
    a_crest_bytes = BytesIO(svg2png(url=f'./icons/{a_name}.svg'))
    h_crest = Image.open(h_crest_bytes)
    h_width_to_height = h_crest.size[0]/h_crest.size[1]
    a_crest = Image.open(a_crest_bytes)
    a_width_to_height = a_crest.size[0]/a_crest.size[1]

    # Initialise variable data
    h_score = data['h_score'][0]
    a_score = data['a_score'][0]
    h_xG = data['h_xG'][0]
    a_xG = data['a_xG'][0]
    h_prob = [data['h_0'][0], data['h_1'][0], data['h_2'][0], data['h_3'][0], data['h_4'][0]]
    a_prob = [data['a_0'][0], data['a_1'][0], data['a_2'][0], data['a_3'][0], data['a_4'][0]]
    h_at_least = [h_prob[0],0,0,0,0]
    a_at_least = [a_prob[0],0,0,0,0]

    # Set up subplots to share central axis
    fig, ax = plt.subplots(1,2)
    fig.subplots_adjust(wspace=0)

    # Set up the bars
    h_bar = ax[0].barh(range(len(h_prob)), h_prob, color=h_colours[0], zorder=3)
    a_bar = ax[1].barh(range(len(a_prob)), a_prob, color=a_colours[0], zorder=3)
    h_al_bar = ax[0].barh(range(len(h_at_least)), h_at_least, color=h_colours[1], edgecolor=h_colours[0], hatch='//', zorder=2)
    a_al_bar = ax[1].barh(range(len(a_at_least)), a_at_least, color=a_colours[1], edgecolor=a_colours[0], hatch='//', zorder=2)

    # Add outline for white bars
    if h_colours[0] == 'white':
        h_outline = ax[0].barh(range(5), h_at_least, fill=False, edgecolor=h_colours[1], zorder=3)
    else:
        h_outline = ax[0].barh(range(5), h_at_least, fill=False, edgecolor=h_colours[0], zorder=3)
    if a_colours[0] == 'white':
        a_outline = ax[1].barh(range(5), a_at_least, fill=False, edgecolor=a_colours[1], zorder=3)
    else:
        a_outline = ax[1].barh(range(5), a_at_least, fill=False, edgecolor=a_colours[0], zorder=3)

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
    ax[0].set_xticks([1,0.8,0.6,0.4,0.2,0], labels=["100", "80", "60", "40", "20", "0"], color=text_colour)
    ax[0].set_xlabel('Probability (%)', color=text_colour)
    ax[0].spines['left'].set_visible(False)
    ax[0].spines['right'].set(zorder=4)

    ax[1].set_xlim(0,1.05)
    ax[1].set_xticks([0,0.2,0.4,0.6,0.8,1], labels=["0","20","40","60","80","100"], color=text_colour)
    ax[1].set_xlabel('Probability (%)', color=text_colour)
    ax[1].yaxis.set_label_position('right')
    ax[1].yaxis.set_ticks_position('right')
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['left'].set(zorder=4)

    # Create legend
    labels = ['Exactly','At Least']
    handles = [plt.Rectangle((0,0),1,1,color='black'), plt.Rectangle((0,0),1,1,facecolor='white',hatch='//',edgecolor='black')]
    ax[1].legend(labels=labels, handles=handles, loc='lower right', fancybox=False, framealpha=0.5)

    # Add Header Text
    minute_label = ax[0].text(0, -1, '0\'', size='x-large', ha='center', weight='bold', color=text_colour)
    match h_name:
        case 'Wolverhampton Wanderers':
            ax[0].text(0.75, -1.25, 'Wolves', size='large', ha='left', weight='bold', color=text_colour)
        case 'Tottenham':
            ax[0].text(0.75, -1.25, 'Spurs', size='large', ha='left', weight='bold', color=text_colour)
        case _:
            ax[0].text(0.75, -1.25, h_name, size='large', ha='left', weight='bold', color=text_colour)
    h_score_label = ax[0].text(0.75, -1, h_score, size='medium', ha='left', weight='bold', color=text_colour)
    h_xG_label = ax[0].text(0.75, -0.75, f'({round(h_xG,2)})', size='medium', ha='left', weight='normal', color=text_colour)
    match a_name:
        case 'Wolverhampton Wanderers':
            ax[1].text(0.75, -1.25, 'Wolves', size='large', ha='right', weight='bold', color=text_colour)
        case 'Tottenham':
            ax[1].text(0.75, -1.25, 'Spurs', size='large', ha='right', weight='bold', color=text_colour)
        case _:
            ax[1].text(0.75, -1.25, a_name, size='large', ha='right', weight='bold', color=text_colour)
    a_score_label = ax[1].text(0.75, -1, a_score, size='medium', ha='right', weight='bold', color=text_colour)
    a_xG_label = ax[1].text(0.75, -0.75, f'({round(a_xG,2)})', size='medium', ha='right', weight='normal', color=text_colour)

    # Add Team Crests to Header
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
    
    # Set up artists list for blitting
    artists = [minute_label, h_score_label, h_xG_label, a_score_label, a_xG_label]
    artists.extend(h_bar.patches)
    artists.extend(a_bar.patches)
    artists.extend(h_al_bar.patches)
    artists.extend(a_al_bar.patches)
    artists.extend(h_outline.patches)
    artists.extend(a_outline.patches)

    end = time.monotonic()
    print(f'Initial set up for {m} completed in {round(end - start,4)} seconds.')
    start = time.monotonic()

    def update(f):
        # Get updated values
        h_prob = [data['h_0'][f], data['h_1'][f], data['h_2'][f], data['h_3'][f], data['h_4'][f]]
        a_prob = [data['a_0'][f], data['a_1'][f], data['a_2'][f], data['a_3'][f], data['a_4'][f]]
        h_at_least[0] = h_prob[0]
        a_at_least[0] = a_prob[0]
        for i in range(1,len(h_at_least)):
            h_at_least[i] = sum(h_prob[i:])
            a_at_least[i] = sum(a_prob[i:])
        
        # Update header text
        minute_label.set_text(f'{data['minute'][f]}\'')
        h_score_label.set_text(f'{data['h_score'][f]}')
        h_xG_label.set_text(f'({round(data['h_xG'][f],2)})')
        a_score_label.set_text(f'{data['a_score'][f]}')
        a_xG_label.set_text(f'({round(data['a_xG'][f],2)})')

        # Update bar widths
        for r in range(len(h_bar.patches)):
            h_bar.patches[r].set_width(h_prob[r])
            a_bar.patches[r].set_width(a_prob[r])
            h_al_bar.patches[r].set_width(h_at_least[r])
            a_al_bar.patches[r].set_width(a_at_least[r])
            h_outline.patches[r].set_width(h_at_least[r])
            a_outline.patches[r].set_width(a_at_least[r])
        
        return artists
    
    def progress(i, n):
        current = time.monotonic()
        print(f'Saving frame {i} of {n} for {m}. Time elapsed: {round((current - start),2)} seconds')
    
    ani = FuncAnimation(fig, update, frames=range(data.shape[0]), interval=25, repeat=False, blit=True)
    end = time.monotonic()
    print(f'Animation for {m} created in {round(end - start,4)} seconds.')
    
    start = time.monotonic()
    ani.save(f'./output/animated/{m}.gif','pillow',fps=30) #, savefig_kwargs={'bbox_inches':'tight'}) #, progress_callback=progress)
    end = time.monotonic()
    print(f'{m}.gif saved in {round(end - start,4)} seconds.')

    start = time.monotonic()
    minute_label.set_text('')
    fig.savefig(f'./output/static/{m}.png', bbox_inches='tight')
    end = time.monotonic()
    print(f'Saved static graph as png in {round(end - start,4)} seconds.')

    start = time.monotonic()
    plt.close(fig)
    end = time.monotonic()
    print(f'Figure closed in {round(end - start,4)} seconds.')
    elapsed = time.monotonic()
    print(f'{int(((elapsed - start_start)/60) - (((elapsed - start_start)%60)/60))} minute(s) and {round((elapsed - start_start)%60,2)} second(s) elapsed...')