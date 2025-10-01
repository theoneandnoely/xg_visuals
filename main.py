# Imports
from get_shot_data import get_league_shot_data
from create_minute_data import create_minute_data
from colours import TEAM_COLOURS, BG_COLOUR, TEXT_COLOUR, PITCH_COLOUR, PAINT_COLOUR
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, Arc
from matplotlib.animation import FuncAnimation
import pandas as pd
import time
from PIL import Image
from io import BytesIO
from sys import argv
import datetime
import os
folder_path = os.path.abspath('./venv/Lib/site-packages/cairo/bin/')
path_env = os.environ['PATH']
if folder_path not in path_env:
    os.environ['PATH'] = folder_path + os.pathsep + path_env
from cairosvg import svg2png


def main(marker_size:int=300, **kwargs) -> None:
    '''
    '''
    league = None
    team = None
    season = None
    period_start = None
    period_end = None

    for k, val in kwargs.items():
        match k:
            case 'league' | 'l':
                league = val
            case 'team' | 't':
                team = val
            case 'season' | 's':
                season = val
            case 'period_start' | 'start':
                period_start = val
            case 'period_end' | 'end':
                period_end = val
            case _:
                raise KeyError(f'{k} is not a valid keyword argument for main().')
    
    start = time.monotonic()

    matches, shots = get_league_shot_data(league, season, period_start, period_end)
    match_minutes = create_minute_data(matches,shots)

    for m_ix in range(len(match_minutes)):
        print(f'Creating visual {m_ix + 1} of {len(match_minutes)}...')
        # Get match code, match id, and team names from matches
        code = matches['match_code'][m_ix]
        id = matches['match_id'][m_ix]
        h_team = matches['h_team'][m_ix]
        a_team = matches['a_team'][m_ix]
        
        # Get minute by minute data and raw shot data for match
        minute_data = match_minutes[m_ix]
        h_shots = shots[(shots['match_id']==id) & (shots['h_a']=='h')].reset_index()
        a_shots = shots[(shots['match_id']==id) & (shots['h_a']=='a')].reset_index()

        # Invert away team x and y coordinates
        a_shots['x_adj'] = a_shots['x'].apply(lambda x: 1 - x)
        a_shots['y_adj'] = a_shots['y'].apply(lambda y: 1 - y)

        # Get team crests, converting from SVG to PNG
        h_crest = Image.open(BytesIO(svg2png(url=f'./icons/{h_team}.svg')))
        a_crest = Image.open(BytesIO(svg2png(url=f'./icons/{a_team}.svg')))

        # Set team colours [primary, accent, outline]
        h_colour = TEAM_COLOURS[h_team]
        if TEAM_COLOURS[a_team][0] == h_colour[0]:
            a_colour = TEAM_COLOURS[a_team][::-1]
        else:
            a_colour = TEAM_COLOURS[a_team]
        if h_colour[0] == 'white':
            h_colour.append(h_colour[1])
        else:
            h_colour.append(h_colour[0])
        if a_colour[0] == 'white':
            a_colour.append(a_colour[1])
        else:
            a_colour.append(a_colour[0])
        
        # Initialise variable data
        h_score = minute_data['h_score'][0]
        a_score = minute_data['a_score'][0]
        h_xG = minute_data['h_xG'][0]
        a_xG = minute_data['a_xG'][0]
        h_prob = [minute_data['h_0'][0], minute_data['h_1'][0], minute_data['h_2'][0], minute_data['h_3'][0], minute_data['h_4'][0]]
        a_prob = [minute_data['a_0'][0], minute_data['a_1'][0], minute_data['a_2'][0], minute_data['a_3'][0], minute_data['a_4'][0]]
        h_at_least = [h_prob[0],0,0,0,0]
        a_at_least = [a_prob[0],0,0,0,0]

        # Set up mpl figure with 10*8 grid and 0 wspace to allow prob bars to share central axis
        fig = plt.figure(figsize=(10,10))
        gs = fig.add_gridspec(10, 8, wspace=0)
        shotmap_ax = fig.add_subplot(gs[1:4,2:6])
        h_prob_ax = fig.add_subplot(gs[4:,0:4])
        a_prob_ax = fig.add_subplot(gs[4:,4:])
        ax = [h_prob_ax, a_prob_ax, shotmap_ax]

        # Add bars for exact and at least probabilities, and outline
        h_p_bar = ax[0].barh(range(5), h_prob, color=h_colour[0], zorder=3)
        h_al_bar = ax[0].barh(range(5), h_at_least, color = h_colour[1], hatch='//', edgecolor=h_colour[0], zorder=2)
        h_ol_bar = ax[0].barh(range(5), h_at_least, fill=False, edgecolor=h_colour[2], zorder=3)
        a_p_bar = ax[1].barh(range(5), a_prob, color=a_colour[0], zorder=3)
        a_al_bar = ax[1].barh(range(5), a_at_least, color=a_colour[1], hatch='//', edgecolor=a_colour[0], zorder=2)
        a_ol_bar = ax[1].barh(range(5), a_at_least, fill=False, edgecolor=a_colour[2], zorder=3)

        # Add scatter plots for missed/blocked shots, own goals, and goals
        h_s_scat = ax[2].scatter(
            x=h_shots[(h_shots['minute'] <= 0) & (h_shots['result'] != 'Goal') & (h_shots['result']!='OwnGoal')]['x'],
            y=h_shots[(h_shots['minute'] <= 0) & (h_shots['result'] != 'Goal') & (h_shots['result']!='OwnGoal')]['y'],
            s=[marker_size*n**2 for n in h_shots[(h_shots['minute']<=0) & (h_shots['result'] != 'Goal') & (h_shots['result'] != 'OwnGoal')]['xG']],
            color=h_colour[0],
            alpha=0.6,
            zorder=2
        )
        h_og_scat = ax[2].scatter(
            x=h_shots[(h_shots['minute']<=0) & (h_shots['result']=='OwnGoal')]['x'],
            y=h_shots[(h_shots['minute']<=0) & (h_shots['result']=='OwnGoal')]['y'],
            s=[marker_size*n**2 for n in h_shots[(h_shots['minute']<=0) & (h_shots['result']=='OwnGoal')]['xG']],
            color=h_colour[1],
            marker='*',
            edgecolors=h_colour[0],
            alpha=0.6,
            zorder=3
        )
        h_g_scat = ax[2].scatter(
            x=h_shots[(h_shots['minute']<=0) & (h_shots['result']=='Goal')]['x'],
            y=h_shots[(h_shots['minute']<=0) & (h_shots['result']=='Goal')]['y'],
            s=[marker_size*n**2 for n in h_shots[(h_shots['minute']<=0) & (h_shots['result']=='Goal')]['xG']],
            color=h_colour[0],
            marker='*',
            edgecolors=h_colour[1],
            alpha=0.6,
            zorder=3
        )
        a_s_scat = ax[2].scatter(
            x=a_shots[(a_shots['minute'] <= 0) & (a_shots['result'] != 'Goal') & (a_shots['result']!='OwnGoal')]['x_adj'],
            y=a_shots[(a_shots['minute'] <= 0) & (a_shots['result'] != 'Goal') & (a_shots['result']!='OwnGoal')]['y_adj'],
            s=[marker_size*n**2 for n in a_shots[(a_shots['minute']<=0) & (a_shots['result'] != 'Goal') & (a_shots['result'] != 'OwnGoal')]['xG']],
            color=a_colour[0],
            alpha=0.6,
            zorder=2
        )
        a_og_scat = ax[2].scatter(
            x=a_shots[(a_shots['minute']<=0) & (a_shots['result']=='OwnGoal')]['x_adj'],
            y=a_shots[(a_shots['minute']<=0) & (a_shots['result']=='OwnGoal')]['y_adj'],
            s=[marker_size*n**2 for n in a_shots[(a_shots['minute']<=0) & (a_shots['result']=='OwnGoal')]['xG']],
            color=a_colour[1],
            marker='*',
            edgecolors=a_colour[0],
            alpha=0.6,
            zorder=3
        )
        a_g_scat = ax[2].scatter(
            x=a_shots[(a_shots['minute']<=0) & (a_shots['result']=='Goal')]['x_adj'],
            y=a_shots[(a_shots['minute']<=0) & (a_shots['result']=='Goal')]['y_adj'],
            s=[marker_size*n**2 for n in a_shots[(a_shots['minute']<=0) & (a_shots['result']=='Goal')]['xG']],
            color=a_colour[0],
            marker='*',
            edgecolors=a_colour[1],
            alpha=0.6,
            zorder=3
        )

        # Set background colour and shared formatting for bar plots
        fig.set_facecolor(BG_COLOUR)
        for a in ax[:-1]:
            a.set_facecolor(BG_COLOUR)
            a.set_yticks(range(5), labels=["0", "1", "2", "3", "4+"], color=TEXT_COLOUR)
            a.tick_params(axis='y',length=0)
            a.set_ylabel('Goals Scored', color=TEXT_COLOUR)
            a.set_xlabel('Probability (%)', color=TEXT_COLOUR)
            a.invert_yaxis()
            a.spines['top'].set_visible(False)
            a.spines['bottom'].set_visible(False)
            a.grid(True, color='0.85', axis='x', zorder=1)
        
        # Set inverted formatting for subplots
        ax[0].set_xlim(1,0)
        ax[0].set_xticks([1,.9,.8,.7,.6,.5,.4,.3,.2,.1,0], labels=range(100,-10,-10), color=TEXT_COLOUR)
        ax[0].spines['left'].set_visible(False)
        ax[0].spines['right'].set(zorder=4)
        ax[1].set_xlim(0,1)
        ax[1].set_xticks([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1], labels=range(0,105,10), color=TEXT_COLOUR)
        ax[1].spines['right'].set_color('0.85')
        ax[1].spines['right'].set(zorder=1)
        ax[1].yaxis.set_label_position('right')
        ax[1].yaxis.set_ticks_position('right')

        # Set formatting for scatterplot
        ax[2].set_xlim(0,1)
        ax[2].set_ylim(0,1)
        ax[2].tick_params(axis='both', length=0)
        ax[2].get_xaxis().set_ticks([])
        ax[2].get_yaxis().set_ticks([])
        ax[2].set_facecolor(PITCH_COLOUR)
        # Add penalty boxes and halfway line to scatterplot
        ax[2].axvline(x=0.5, color=PAINT_COLOUR, zorder=1)
        centre_circle = ax[2].add_patch(Ellipse(xy=(0.5,0.5),width=0.11,height=0.175,color=PAINT_COLOUR,fill=False))
        centre_circle.set_zorder(1)
        ax[2].hlines(y=[0.19, 0.81],xmin=0,xmax=0.17,colors=PAINT_COLOUR,zorder=1)
        ax[2].axvline(x=0.17,ymin=0.19,ymax=0.81,color=PAINT_COLOUR,zorder=1)
        ax[2].hlines(y=[0.37,0.63],xmin=0,xmax=0.055,colors=PAINT_COLOUR,zorder=1)
        ax[2].axvline(x=0.055,ymin=0.37,ymax=0.63,color=PAINT_COLOUR,zorder=1)
        ax[2].hlines(y=[0.19,0.81],xmin=0.83,xmax=1,colors=PAINT_COLOUR,zorder=1)
        ax[2].axvline(x=0.83,ymin=0.19,ymax=0.81,color=PAINT_COLOUR,zorder=1)
        ax[2].hlines(y=[0.37,0.63],xmin=0.945,xmax=1,colors=PAINT_COLOUR,zorder=1)
        ax[2].axvline(x=0.945,ymin=0.37,ymax=0.63,color=PAINT_COLOUR,zorder=1)
        h_pen_arc = ax[2].add_patch(Arc(xy=(0.115,0.5),width=0.16,height=0.15,angle=270,theta1=49,theta2=131,color=PAINT_COLOUR))
        a_pen_arc = ax[2].add_patch(Arc(xy=(0.885,0.5),width=0.16,height=0.15,angle=90,theta1=49,theta2=131,color=PAINT_COLOUR))
        h_pen_arc.set_zorder(1)
        a_pen_arc.set_zorder(1)
        # Add arrow showing direction of attack
        ax[2].axhline(y=0.85,xmin=0.3,xmax=0.7,color=TEXT_COLOUR,zorder=2)
        ax[2].plot([0.67,0.7],[0.9,0.85],color=TEXT_COLOUR,zorder=2)
        ax[2].plot([0.67,0.7],[0.8,0.85],color=TEXT_COLOUR,zorder=2)
        

        # Create legend
        labels = ['Exactly','At Least']
        handles = [Rectangle((0,0),1,1,color='black'), Rectangle((0,0),1,1,facecolor='white',hatch='//',edgecolor='black')]
        ax[1].legend(labels=labels, handles=handles, loc='lower right', fancybox=False, framealpha=0.5)

        # Add Header Text
        minute_label = ax[2].text(0.5, 1.1, '0\'', size='x-large',ha='center',weight='bold',color=TEXT_COLOUR)
        match h_team:
            case 'Wolverhampton Wanderers':
                h_team_label = 'Wolves'
            case 'Tottenham':
                h_team_label = 'Spurs'
            case _:
                h_team_label = h_team
        match a_team:
            case 'Wolverhampton Wanderers':
                a_team_label = 'Wolves'
            case 'Tottenham':
                a_team_label = 'Spurs'
            case _:
                a_team_label = a_team
        ax[2].text(0.5,0.925,f'{h_team_label} attacking',ha='center',size='medium',color=TEXT_COLOUR,zorder=2)
        ax[2].text(-0.45,0.2,h_team_label,size='large',ha='left',weight='bold',color=TEXT_COLOUR)
        h_score_label = ax[2].text(-0.45,0.1,h_score,size='x-large',ha='left',weight='bold',color=TEXT_COLOUR)
        h_xG_label = ax[2].text(-0.45,0,f'({round(h_xG,2)})',size='large',ha='left',weight='normal',color=TEXT_COLOUR)
        ax[2].text(1.45,0.2,a_team_label,size='large',ha='right',weight='bold',color=TEXT_COLOUR)
        a_score_label = ax[2].text(1.45,0.1,a_score,size='x-large',ha='right',weight='bold',color=TEXT_COLOUR)
        a_xG_label = ax[2].text(1.45,0,f'({round(a_xG,2)})',size='large',ha='right',weight='normal',color=TEXT_COLOUR)
        h_event_label = ax[2].text(0.4,1.1,'',size='medium',ha='right',weight='normal',color=TEXT_COLOUR)
        a_event_label = ax[2].text(0.6,1.1,'',size='medium',ha='left',weight='normal',color=TEXT_COLOUR)

        # Add Team crests either side of scatter plot
        ax_h_crest = fig.add_subplot(gs[1:3,0:2])
        ax_h_crest.imshow(h_crest)
        ax_h_crest.set_zorder(5)
        ax_h_crest.axis('off')
        ax_a_crest = fig.add_subplot(gs[1:3,-2:])
        ax_a_crest.imshow(a_crest)
        ax_a_crest.set_zorder(5)
        ax_a_crest.axis('off')

        # Adjust margins to allow room for minute and events text at top
        fig.subplots_adjust(left=0.075, bottom=0.075, right=0.925, top=1.025)

        # Set up artists list for blitting
        artists = [minute_label, h_score_label, h_xG_label, a_score_label, a_xG_label, h_event_label, a_event_label]
        artists.extend(h_p_bar.patches)
        artists.extend(a_p_bar.patches)
        artists.extend(h_al_bar.patches)
        artists.extend(a_al_bar.patches)
        artists.extend(h_ol_bar.patches)
        artists.extend(a_ol_bar.patches)
        artists.append(h_s_scat)
        artists.append(a_s_scat)
        artists.append(h_og_scat)
        artists.append(a_og_scat)
        artists.append(h_g_scat)
        artists.append(a_g_scat)

        n_h_shots = [0]
        n_a_shots = [0]

        def update(f):
            h_prob = [minute_data['h_0'][f], minute_data['h_1'][f], minute_data['h_2'][f], minute_data['h_3'][f], minute_data['h_4'][f]]
            a_prob = [minute_data['a_0'][f], minute_data['a_1'][f], minute_data['a_2'][f], minute_data['a_3'][f], minute_data['a_4'][f]]
            h_at_least[0] = h_prob[0]
            a_at_least[0] = a_prob[0]
            for i in range(1,len(h_at_least)):
                h_at_least[i] = sum(h_prob[i:])
                a_at_least[i] = sum(a_prob[i:])
            frame_minute = minute_data['minute'][f]

            # Update text
            minute_label.set_text(f'{frame_minute}\'')
            h_score_label.set_text(f'{minute_data['h_score'][f]}')
            h_xG_label.set_text(f'({round(minute_data['h_xG'][f],2)})')
            h_event_label.set_text(f'{minute_data['h_event_log'][f]}')
            a_score_label.set_text(f'{minute_data['a_score'][f]}')
            a_xG_label.set_text(f'({round(minute_data['a_xG'][f],2)})')
            a_event_label.set_text(f'{minute_data['a_event_log'][f]}')

            # Update bar widths
            for r in range(len(h_p_bar.patches)):
                h_p_bar.patches[r].set_width(h_prob[r])
                a_p_bar.patches[r].set_width(a_prob[r])
                h_al_bar.patches[r].set_width(h_at_least[r])
                a_al_bar.patches[r].set_width(a_at_least[r])
                h_ol_bar.patches[r].set_width(h_at_least[r])
                a_ol_bar.patches[r].set_width(a_at_least[r])
            
            # Update scatter plots
            if h_shots[h_shots['minute']<=frame_minute].shape[0] > n_h_shots[-1]:
                h_s_scat = ax[2].scatter(
                    x=h_shots[(h_shots['minute'] == frame_minute) & (h_shots['result'] != 'Goal') & (h_shots['result']!='OwnGoal')]['x'],
                    y=h_shots[(h_shots['minute'] == frame_minute) & (h_shots['result'] != 'Goal') & (h_shots['result']!='OwnGoal')]['y'],
                    s=[marker_size*n**2 for n in h_shots[(h_shots['minute']==frame_minute) & (h_shots['result'] != 'Goal') & (h_shots['result'] != 'OwnGoal')]['xG']],
                    color=h_colour[0],
                    alpha=0.6,
                    zorder=3
                )
                h_og_scat = ax[2].scatter(
                    x=h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='OwnGoal')]['x'],
                    y=h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='OwnGoal')]['y'],
                    s=[marker_size*n**2 for n in h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='OwnGoal')]['xG']],
                    color=h_colour[1],
                    marker='*',
                    edgecolors=h_colour[0],
                    alpha=0.8,
                    zorder=3
                )
                h_g_scat = ax[2].scatter(
                    x=h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='Goal')]['x'],
                    y=h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='Goal')]['y'],
                    s=[marker_size*n**2 for n in h_shots[(h_shots['minute']==frame_minute) & (h_shots['result']=='Goal')]['xG']],
                    color=h_colour[0],
                    marker='*',
                    edgecolors=h_colour[1],
                    alpha=0.8,
                    zorder=3
                )
                n_h_shots.append(h_shots[h_shots['minute']<=frame_minute].shape[0])
            if a_shots[a_shots['minute']<=frame_minute].shape[0] > n_a_shots[-1]:
                a_s_scat = ax[2].scatter(
                    x=a_shots[(a_shots['minute'] == frame_minute) & (a_shots['result'] != 'Goal') & (a_shots['result']!='OwnGoal')]['x_adj'],
                    y=a_shots[(a_shots['minute'] == frame_minute) & (a_shots['result'] != 'Goal') & (a_shots['result']!='OwnGoal')]['y_adj'],
                    s=[marker_size*n**2 for n in a_shots[(a_shots['minute']==frame_minute) & (a_shots['result'] != 'Goal') & (a_shots['result'] != 'OwnGoal')]['xG']],
                    color=a_colour[0],
                    alpha=0.6,
                    zorder=3
                )
                a_og_scat = ax[2].scatter(
                    x=a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='OwnGoal')]['x_adj'],
                    y=a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='OwnGoal')]['y_adj'],
                    s=[marker_size*n**2 for n in a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='OwnGoal')]['xG']],
                    color=a_colour[1],
                    marker='*',
                    edgecolors=a_colour[0],
                    alpha=0.8,
                    zorder=3
                )
                a_g_scat = ax[2].scatter(
                    x=a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='Goal')]['x_adj'],
                    y=a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='Goal')]['y_adj'],
                    s=[marker_size*n**2 for n in a_shots[(a_shots['minute']==frame_minute) & (a_shots['result']=='Goal')]['xG']],
                    color=a_colour[0],
                    marker='*',
                    edgecolors=a_colour[1],
                    alpha=0.8,
                    zorder=3
                )
                n_a_shots.append(a_shots[a_shots['minute']<=frame_minute].shape[0])
            return artists
        
        def progress(i, n):
            current = time.monotonic()
            print(f'Saving frame {i} of {n} for {code} (match {m_ix + 1}/{len(match_minutes)}). Time elapsed: {round((current - animation_start),2)} seconds')

        animation_start = time.monotonic()
        ani = FuncAnimation(fig, update, frames=range(minute_data.shape[0]), interval=25, repeat=False, blit=True)
        ani.save(f'./output/animated/{code}.gif','pillow',fps=30, progress_callback=progress)
        
        minute_label.set_text('')
        h_event_label.set_text('')
        a_event_label.set_text('')
        fig.subplots_adjust(top=1.05)
        fig.savefig(f'./output/static/{code}.png')

        elapsed = time.monotonic()
        print(f'Visuals created for {code}. Total time elapsed: {int(((elapsed - start)/60) - (((elapsed - start)%60)/60))} minutes and {round((elapsed - start)%60,2)} seconds.')

if __name__ == '__main__':
    if len(argv) > 1:
        cl_args = argv[1:]
        if cl_args[0][0] != '-':
            raise ValueError(f'Unknown command line argument "{cl_args[0]}". Use -h or --help for list of command line arguments.')
        elif cl_args[0] in ('-h','--help'):
            print('''
    -h\t\tPrint this help page.
    -l\t\tLeague ID(s) to determine matches to create visuals for, as str or list[str]
    -t\t\tTeam ID(s) to determine matches to create visuals for, as str or list[str]
    -s\t\tSeason ID(s) to determine matches to create visuals for, as str or list[str]
    -ps\t\tStart Date for filtering visualised matches in "YYYY-MM-DD" format
    -pe\t\tEnd Date for filtering visualised matches in "YYYY-MM-DD" format'''
            )
    else:
        league = 'EPL'
        period_start = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        period_end = datetime.datetime.today().strftime('%Y-%m-%d')
        main(l=league,start=period_start,end=period_end)

    
    