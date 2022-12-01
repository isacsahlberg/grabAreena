# Here we gather auxiliary functions, which we call from the main program
import argparse
from datetime import date, timedelta
import re
from termcolor import colored


def parser_():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day"    , "-d", help="set day")
    parser.add_argument("--month"  , "-m", help="set month")
    parser.add_argument("--pattern", "-p", help='set specific search pattern string (default: "Bach", "Mozart" and "Schumann")')
    parser.add_argument("--tomorrow", "-tmrw", action='store_true', help='force date to be "tomorrow"')
    parser.add_argument("--nocolor", "-nc", action='store_true', help='skip highlighting matches with color')
    parser.add_argument("--giveall", "-ga", action='store_true', help='print all times/pieces for the day')
    parser.add_argument("--giveurl", "-gu", action='store_true', help='print url for easy copy-pasting and checking')
    # return parser.parse_args()  # (fails running interactively...)
    return parser.parse_known_args()[0]


def setDate(args):
    '''
    Set the date based on the given arguments. 
    If none are given, use the current date.
    If the date was specified using --day [and --month]
        but --tomorrow is used, override to tomorrow's date.
    '''

    # Default time is now
    today = date.today()
    today_m = today.month
    today_d = today.day

    if args.day:
        if len(args.day) in [1,2]:
            today_d = int(args.day)
        if args.month:
            if len(args.month) in [1,2]:
                today_m = int(args.month)

    if args.tomorrow:  # If we wanted "tomorrow", then change the date
        today = today + timedelta(1)
        if args.day:
            print('\n(NOTE: You specified both a date and "tomorrow"', end='')
            print(f' -- going with "tomorrow", i.e. {today})')
        today_m = today.month
        today_d = today.day
    # So we arrive at the date
    return date(today.year, today_m, today_d)


def makeURL(today):
    # url = "https://yle.fi/ohjelmaopas/data/2502-r17.htm"  # example
    url_base1 = 'https://yle.fi/ohjelmaopas/data/'
    url_base2 = '-r17.htm'
    today_str = f"{today.day:02d}{today.month:02d}"
    return url_base1 + today_str + url_base2


### Replace part of a string with a colored version
# Maybe there are modules with this functionality, but let's just code it
def repl_str(str_, match):
    new_str = ''

    # Find matches and iterate over
    ite = re.finditer(match.lower(), str_.lower())
    start_idx = 0
    for i in ite:
        # Add preceding part
        new_str += str_[start_idx:i.start()]
        
        # Add matching part, but replace by colored version
        new_str += colored(str_[i.start():i.end()], 'blue', 'on_cyan')
        
        # Change starting point for next iteration
        start_idx = i.end()
    
    new_str += str_[start_idx:]
    return new_str


def day_str(today):
    str_  = f"{today.strftime('%A')}"
    # str_ += f" ({today_d:02d}-{today_m:02d})" # 24-08 except we don't actually have the variables here 
                                                #       (why does it work anyway in python again?)
    # str_ += f" ({today.strftime('%d-%m')})"   # 24-08
    # str_ += f" ({today.strftime('%d %b')})"   # 24 Aug
    str_ += f" ({today.strftime('%d %b %Y')})"  # 24 Aug 2022
    return str_


#----------------------------------------------------------------------


# Fix the times and program names list (last program has 2 times!)
def fixProgramTitlesTimes(list_titles):
    times  = []
    titles = []
    for t_i in range(len(list_titles)):
        time1 = list_titles[t_i].strip().split()[0]
        
        if t_i < len(list_titles)-1:
            time2 = list_titles[t_i+1].strip().split()[0]
            title = ' '.join(list_titles[t_i].strip().split()[1:])
        else:
            time2 = list_titles[-1].strip().split()[2]
            title = ' '.join(list_titles[-1].strip().split()[3:])
        
        # Save times into list, but make sure 6:00 becomes 06:00 etc.
        if len(time1)<5:
            time1 = '0'+time1
        if len(time2)<5:
            time2 = '0'+time2

        # Save into lists
        titles.append(title)
        times.append((time1,time2))
    return titles, times


def getProgramsAndTimes(html_str, pattern_titles="<B>.*?</B>"):
    programs_and_times = []

    for match in re.finditer(pattern_titles, html_str):
        index = match.start()
        value = match.group()
        programs_and_times.append(value[3:-4])

    programs, program_times = fixProgramTitlesTimes(programs_and_times)

    # Let's fix all the times to have a colon separator
    for i,(t1,t2) in enumerate(program_times):
        # program_times[i] = tuple(s.replace('.', ':') for s in program_times[i])
        program_times[i] = (t1.replace('.', ':'), t2.replace('.', ':'))

    # Extract the time which ends the programs for the day
    _, endtime = program_times[-1]
    # Fix the look of the end time variable, e.g.  '06:00' --> '+06:00'
    endtime = '+' + endtime

    return programs, program_times, endtime


def getContents(html_str, program_times):
    # Extract the program contents, one long string (with all pieces) for each program
    pattern_contents = "<dd>.*?<p>"

    # content_idx = []  # was helpful for debugging purposes
    list_contents = []

    for match in re.finditer(pattern=pattern_contents, string=html_str):
        index = match.start()
        value = match.group()
        # content_idx.append(index)
        list_contents.append(value[4:-3])  # slice to get rid of "<dd>" and "<p>"

    # Still missing beginning time of the program (i.e. of the first piece of every program)
    program_contents = [program_times[i][0]+' '+list_contents[i] for i,_ in enumerate(list_contents)]
    
    return program_contents


def massagePieces(list_pieces):
    # 1 -- The data has a mix of single and double digits
    # e.g.  8:45   09:00   9:21 ... so add a missing zero, if it is needed
    for i,(t,p) in enumerate(list_pieces):
        # Check if already the 2nd character is a colon
        if t[1] == ':':
            list_pieces[i] = ('0'+t,p)

    # 2 -- Fix next-morning times to have a '+' in them
    for i,(t,p) in enumerate(list_pieces):
        # Assumption: they are all located at the latter half of the list of pieces
        if i > round(len(list_pieces)/2):
            # Check if the time starts with 0
            if t[0]=='0':
                list_pieces[i] = ('+'+t,p)
    return list_pieces


def getPieces(contents):
    pieces = []
    for cont in contents:
        # Split for single- OR double-digit hours    
        list_pieces =  re.split('\d+:\d\d ', cont)[1:]  # \d+ means "\d" repeated 0 or more times
        list_times = re.findall('\d+:\d\d ', cont)
        # If everything went well, we have an equal number of pieces as times
        assert len(list_pieces) == len(list_times), \
            f'# of times ({len(list_times)}) and # of pieces ({len(list_pieces)}) do not match....'
        
        for (t,p) in zip(list_times,list_pieces):
            pieces.append((t.strip(),p))
    return pieces


def getMatches(time_piece_tuples, pattern, endtime, color=True):
    list_matches = []
    for i,(t,piece) in enumerate(time_piece_tuples):
        if i == len(time_piece_tuples)-1:
            t2 = endtime
        else:
            t2, _ = time_piece_tuples[i+1]
        
        if pattern.lower() in piece.lower():

            if color:
                piece = repl_str(piece, pattern)
            
            # How to handle midday programs, where the times are not given beforehand in the dataset?
            # If the description is long and the hour of the start time is roughly midday, then give a friendly warning
            if len(piece) > 250 and int(t[:2]) in [12,13,14]:
                piece += '\n'+' '*4
                piece += '💀 NOTE: -Possibly mid-day program with a long description'
                piece += '\n'+' '*4+'💀'+' '*7
                piece += '-The start/end time not necessarily accurate for the matching piece'
            
            # Aligning the entries, and the times may include leading "+"-symbol
            list_matches.append(t.rjust(6)+' -'+t2.rjust(6)+'  --  '+piece)
    return list_matches


def printMatches(matches, pattern, today):
    assert isinstance(pattern, list), 'please input a list'

    if isinstance(pattern, str):
        pattern_str = '"' + pattern + '"'
    else:
        pattern_str = ', '.join(['"'+pat+'"' for pat in pattern])
        
    N_matches = len(matches) - (len(pattern) - 1)  # removing '----' lines

    if N_matches>0:
        print("\n"*4 + f'----> There are {N_matches} entries matching {pattern_str} ',end='')
        # print(f"for the day {today_d:02d}-{today_m:02d}: \n")
        print(f"for {day_str(today)}: \n")
        
        for match in matches:
            print(match)
        print("\n\n\n")
    else:
        print(f'\n\n----> There are {N_matches} entries matching {pattern_str} ',end='')
        print(f"for {day_str(today)}: \n")
        # print(f'for the date {today_d:02d}-{today_m:02d}.\n\n')


def makeMatchesList(pieces, pattern_list, endtime, color):
    matches = []
    N_patterns = len(pattern_list)
    for i,pattern in enumerate(pattern_list):
        matches += getMatches(pieces, pattern, endtime, color=color)
        matches += ['--------------'] if i<N_patterns-1 else ''
    return matches


# For debugging/clarification purposes
# If specified "--giveall", print all times and pieces
def printAllPieces(pieces):
    print("\n\n---> OK, here are all times/pieces for the day:")
    for t,p in pieces:
        print(t, "--", p)