#!/usr/bin/env python3

from grabAreena_functions import *
from urllib.request import urlopen



# Here you can change the default patterns if you like
default_patterns = ['Bach', 'Mozart', 'Schumann']

# Initiate the parser
args = parser_()

# The default patterns can be overridden using the input parameter -p
pattern_list = [args.pattern] if args.pattern else default_patterns

# Check that if month was given, day should also be given
assert bool(args.month) <= bool(args.day), \
    'If you specify the month "-m", you must also specify the day "-d"'

# Default: color-highlight the match in the piece description
color = False if args.nocolor else True 

# Get the date based on the given arguments
today = setDate(args)

# Make appropriate URL corresponding to the chosen date
url = makeURL(today)

# Grab html from the url
enc = "ISO-8859-1"  # This encoding found in the HTML of the yle.fi website (may change?)
html_str = urlopen(url).read().decode(enc)

# Get program names and their (start,end) times
programs, program_times, endtime = getProgramsAndTimes(html_str)

# Extract the program contents, one long string (with all pieces) for each program
program_contents = getContents(html_str, program_times)

# List all pieces for the day
pieces = getPieces(program_contents)

# For aesthetics purposes, fix the times in the list of all pieces
pieces = massagePieces(pieces)

# If specified "--giveall", print all times and pieces (for debugging purposes)
if args.giveall:
    printAllPieces(pieces)

# Finally, grab matches and print
matches = makeMatchesList(pieces, pattern_list, endtime, color)

printMatches(matches, pattern_list, today)
