## grabAreena

Are you a fan of classical music? In particular, do you listen to it live on the radio, because you are 
fed up with lists and bookmarks, and listening to music live keeps you centered in the present?
Are you so lazy that you can't be bothered to search through the day's pieces for your favorite composers 
to see _when exactly_ you should remember to have the radio on? And do you listen to it on the Finnish radio?
If you answered yes to all of these, you are most likely me, and you should probably stop writing this silliness and do something else.
But nevertheless, _grabAreena_ is for you!

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
$ python grabAreena.py -d 24 -m 12      # equivalents
$ python grabAreena.py -tmrw            # equivalents
```



## Example usage:
```bash
$ python grabAreena.py
```
produed the output

```bash
----> There are 4 entries matching "Bach", "Mozart", "Schumann" for Thursday (19 Jan 2023): 

 15:41 - 15:58  --  J.S. Bach: Aaria ja muunnelmia italialaiseen tapaan a-molli. (Emil Gilels, piano). 
--------------
 14:36 - 15:04  --  W.A. Mozart: Sinfonia n:o 40 g-molli (Clevelandin ork./Christoph von Dohnanyi). 
 23:04 - 23:33  --  W.A. Mozart: Klarinettikonsertto A-duuri (Jon Manasse ja Seattlen SO/Gerard Schwarz). 
--------------
 19:32 - 19:49  --  Schumann: Fantasia viululle ja pianolle C-duuri (Jennifer Koh ja Reiko Uchida). 
```
[where the ```Names``` is highlighted in color, but I don't know how to make that appear here in markdown]



### Notes:
- The language of the data set itself (i.e. the output) is Finnish
- The yle website doesn't have data for all days of the year, only 1-2 days backwards, and a handful of days forward
- One "day" typically runs from 6AM to 6AM
- Due to the html data used being so un-clean and varied, it's kind of hopeless to try and even separate composer vs. piece... 😒
- Sometimes, parts of the day's program is missing from the page we use, even if it is available elsewhere. Maybe one day we'll switch over to that other page if it seems like a good idea, but for now, ```¯\_(ツ)_/¯```
- Requires ```python3```, only non-standard package is ```termcolor```
- There are a few other arguments which can be given, e.g. ```--giveall``` additionally prints the entire set of pieces for the day, in readable form
- Noobtip: on Unix, using ```chmod```, you can make the script an executable (the shebang ```#!/usr/bin/env python3``` is already included), and aliasing a keyword to the location of the script allows you to simply run e.g. ```grabAreena``` from anywhere — the convenience is what the script was originally intended for!

Usual web scraping ethics apply. Don't be a tool and use this is a loop with zillions of calls. 
(Instead, *use* this tool, and-- get it? cause, tool?-- oh, they already left...)



### License
MIT