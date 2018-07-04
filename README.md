# Tino's Zeiterfassungs Tool

Because tracking time in excel is an utter atrocity, here is a small script that does it
for you.

It stores start time, end time, break time and a comment in a yaml construct.
It even supports multi-part days, in case you are on a travel, go see a physician, split
home and on-site office or for whatever reasons.

It calculates over-time saldos on a daily, weekly and monthly basis

## Dependencies
Dependencies are minimal

### necessary
- python
- (py)yaml

### optional
- setuptools (to install)
- whatever I pick to write out excel
(probably pandas and its excel deps)


## Usage
Usage is simple, run the script with a user name and a db_path (default is current path).  
If you just started working, run the `--start` flag without options, when you leave,
run the script again with `--end`. The script with use the current time -- rounded to
quarter hours -- for the time tracking. If you want to use another time, give it to the
flag in form of `HH:MM`.  
If you want to change the date use either `--date YYYY-MM-DD` or any combination of
`--year YYYY`, `--month MM`, `--day DD`.  
You can add a comment, change the length of your break or even declare the current entry
a sub-day (and then go on and add more sub-days).

### Command Line Options
```
--work_time WORK_TIME    Arbeitspensum pro Tag; Format H:MM
--db_path DB_PATH        Ort, an dem die In- und Output Files liegen
--user USER              zu bearbeitender Mitarbeiter
--export [EXPORT]        schreibt erfasste Zeiten in gegebenen Formaten;
                         unterstützt: [yml, xls]

bestimmt den zu bearbeitenden Tag; falls nichts gesetzt, nutze heute:
--date DATE              zu bearbeitender Tag im ISO Format (z.B. 1970-12-31)
--day DAY                bestimmt den zu bearbeitenden Tag
--month MONTH            bestimmt den zu bearbeitenden Monat
--year YEAR              bestimmt das zu bearbeitende Jahr

definiert den Arbeitstag
--start [START]          setzt Arbetisbeginn, falls ohne Argument: nutze jetzt
--end [END]              setzt Arbeitsende, falls ohne Argument: nutze jetzt
--pause PAUSE            Pausenzeit in Minuten
--comment COMMENT        optionaler Kommentar zum Eintrag
--multi_day MULTI_DAY    ermöglicht mehrere Einträge pro Tag
```


### Example yml file
To see the yaml data structure, have a look at this output of recorded pseudo-times.
Keep in mind the hierarchy of  
`year -> month -> week -> day [-> part-day]`
```
erfasste Zeiten für TinoMichael:
2018:
  5:
    18:
      3: {Tagessaldo: '-2:42:00', end: '14:00:00', pause: 0, start: '9:00:00'}
      6:
        Tagessaldo: '-4:42:00'
        a: {end: '10:00:00', pause: 0, start: '9:00:00'}
        b: {end: '14:00:00', pause: 0, start: '12:00:00'}
      Wochensaldo: '-7:24:00'
    Monatssaldo: '-7:24:00'
```


## TODO

`Urlaub` and `Zeitausgleich` options?  
For now, these workarounds should work:
- Urlaub: set `start` and `end` to the same time (e.g. 0:00) and `pause` to be equal to
`work_time`, add a comment `"Urlaub"`
- Zeitausgleich: set `start` and `end` to the same time (e.g. 0:00) and `pause` to 0,
add a comment `"Zeitausgleich"`

(If I'll implement some command line flags, they would just automatise these steps.)
