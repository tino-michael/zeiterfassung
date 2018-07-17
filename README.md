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
If you want to change the date, use either `--date YYYY-MM-DD` or any combination of
`--year YYYY`, `--month MM`, `--day DD`.  
You can add a comment, change the length of your break or even declare the current entry
a sub-day (and then go on and add more sub-days).

You can declare vacation or Zeitausgleich with the `--urlaub` and `--zeitausgleich`
flags, respectively.

You can delete a day with `--remove`.

### Command Line Options
```
--work_time WORK_TIME    Arbeitspensum pro Tag; Format H:MM
--db_path DB_PATH        Ort, an dem die In- und Output Files liegen
--user USER              zu bearbeitender Mitarbeiter
--export [EXPORT]        schreibt erfasste Zeiten in gegebenen Formaten;
                         unterstützt: [yml, xls]
--expand                 expandiert die anderweitig kompakte Ausgabe der erfassten Zeiten

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

Out of Office Flaggen:
-u, --urlaub             deklariert den Tag als Urlaubstag:
                         keine Arbeit erwartet, kein Saldo verbraucht
-z, --zeitausgleich      keine Arbeitszeit, Saldo wird um reguläre Zeit veringert
```


### Example yml file
To see the yaml data structure, have a look at this output of recorded pseudo-times.
Keep in mind the hierarchy of  
`year -> month -> week -> day [-> part-day]`
```
erfasste Zeiten für TinoMichael:
 /tmp/TinoMichael_Zeiterfassung.yml
2018:
  5:
    18:
      3: {start: '9:00', end: '14:00', pause: 0, Arbeitszeit: '5:00', Tagessaldo: '-2:42'}
      Wochensaldo: '-2:42'
    19:
      7:
        a: {start: '9:00', end: '10:00', pause: 0, comment: pre-noon}
        b: {start: '13:00', end: '16:00', pause: 0, comment: post-noon}
        Arbeitszeit: '4:00'
        Tagessaldo: '-3:42'
      Wochensaldo: '-3:42'
    Monatssaldo: '-6:24'
  Jahressaldo: '-6:24'
```


## TODO
- export to excel
