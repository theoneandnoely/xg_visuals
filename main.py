# Imports
from get_shot_data import get_league_shot_data
from create_minute_data import create_minute_data
from util import prob
from colours import TEAM_COLOURS, BG_COLOUR, TEXT_COLOUR, PITCH_COLOUR
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


def main(**kwargs):
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
                raise KeyError(f'{k} is not a valid keyword for main().')
    matches, shots = get_league_shot_data(league, season, period_start, period_end)
    match_minutes = create_minute_data(matches,shots)

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

    
    