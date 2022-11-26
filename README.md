
### grabAreena

Are you a fan of classical music? In particular, live on the Finnish radio, because you are fed up with lists and bookmarks, and listening to music live keeps you centered in the present? Are you so lazy that you can't be bothered to search through the day's pieces for your favorite composers to see _when exactly_ you should remember to have the radio on? And do you listen to it on the Finnish radio? If you answered yes to all of these, you are most likely me, and you should probably stop writing this silliness and do something else. But nevertheless, _grabAreena_ is for you!

_grabAreena_ performs a simple html grab of the list of pieces played during a given day on the classical channel of the Finnish Yle ~~radio~~ Areena (yeah, sorry, this is tailored for a very niche audience, most likely just me, like we established above). It massages the html string to create a list of the useful information, i.e. the beginning times, end times and the pieces themselves. But we don't want to read it all, of course, so we pick out only the ones we want. Use your own _"pattern"_ to match the composer, or just use the default ones. 

```bash
$ python grabAreena.py
$ python grabAreena.py --pattern bach
$ python grabAreena.py -p bach          # equivalent
```

You can set the date using command line arguments for the day (and even month), or simply "tomorrow"

```bash
$ python grabAreena.py --day 24 --month 12
$ python grabAreena.py --tomorrow       # automatically sets the date to tomorrow
$ python grabAreena.py -d 24 -m 12
$ python grabAreena.py -tmrw
```

### Note:
- The language of the data set itself (i.e. the output) is Finnish
- The yle website doesn't have data for all days of the year, but more like XXXXX (a month forward?) (and backward?)
- Due to the html data used being so un-clean, it's kind of hopeless to try and even separate composer vs. piece... 😒


### TODO:
- Requirements (python3, only non-standard package is 'termcolor')





Needless to say, don't be a jerk and endlessly spam scrape websites.

### License

MIT