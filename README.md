
### grabAreena

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

### Example usage:
```bash
$ python grabAreena.py -p mozart
```
outputs
```bash
----> There are 3 entries matching "mozart" for Wednesday (18 Jan 2023): 

 11:17 - 11:43  --  W.A. Mozart: Kvartetto g-molli (Emanuel Ax, piano, Isaac Stern, viulu, Jaime Laredo, alttoviulu, ja Yo-Yo Ma, sello). 
 12:09 - 12:16  --  W.A. Mozart: Laudate Dominum (Joshua Bell, viulu, ja St. Luken ork./Michael Stern). 
 20:04 - 20:18  --  W.A. Mozart: Sonaatti viululle ja pianolle n:o 18 G-duuri (Yefim Bronfman ja Isaac Stern). 
```
[where ```Mozart``` is highlighted in color, but I don't know how to make that appear here in markdown]

### Notes:
- The language of the data set itself (i.e. the output) is Finnish
- The yle website doesn't have data for all days of the year, only 1-2 days backwards, and a handful of days forward.
- One "day" typically runs from 6AM to 6AM
- Due to the html data used being so un-clean and varied, it's kind of hopeless to try and even separate composer vs. piece... 😒
- Sometimes, parts of the day's program is missing from the page we use, even if it is available elsewhere. Maybe one day we'll switch over to that other page if it seems like a good idea, but for now, ```¯\_(ツ)_/¯```
- Requires ```python3```, only non-standard package is ```termcolor```




Usual web scraping ethics apply. Don't be a tool and use this is a loop with zillions of calls. 
(Instead, *use* this tool, and-- get it? cause, tool?-- oh, they already left...)

### License

MIT