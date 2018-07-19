#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from os.path import expandvars

import argparse
import datetime

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main(db=None):
    parser = argparse.ArgumentParser(
        formatter_class=lambda prog:
            argparse.RawTextHelpFormatter(prog, width=90, max_help_position=27))

    date_group = parser.add_argument_group(
        description="bestimmt den zu bearbeitenden Tag;"
                    " falls nichts gesetzt, nutze heute:")
    date_group.add_argument('--date', type=str, default=False,
                            help="zu bearbeitender Tag im ISO Format"
                                 " (z.B. 1970-12-31)")
    date_group.add_argument('-d', '--day', type=int, default=False,
                            help="bestimmt den zu bearbeitenden Tag")
    date_group.add_argument('-m', '--month', type=int, default=False,
                            help="bestimmt den zu bearbeitenden Monat")
    date_group.add_argument('-y', '--year', type=int, default=False,
                            help="bestimmt das zu bearbeitende Jahr")

    day_group = parser.add_argument_group(description="definiert den Arbeitstag:")
    day_group.add_argument('-s', '--start', type=str, nargs='?', default=False,
                           help="setzt Arbetisbeginn, falls ohne Argument:"
                                " nutze jetzt")
    day_group.add_argument('-e', '--end', type=str, nargs='?', default=False,
                           help="setzt Arbeitsende, falls ohne Argument:"
                                " nutze jetzt")

    day_group.add_argument('-p', '--pause', type=int, default='30',
                           help="Pausenzeit in Minuten")

    day_group.add_argument('-c', '--comment', type=str, nargs='*', default=None,
                           help="optionaler Kommentar zum Eintrag")

    day_group.add_argument('--multi_day', type=str, default=False,
                           help="ermöglicht mehrere Einträge pro Tag")

    parser.add_argument('-w', '--work_time', type=str, default='7:42',
                        help="Arbeitspensum pro Tag; Format H:MM")

    parser.add_argument('--db_path', type=str, default=os.getcwd(),
                        help="Ort, an dem die In- und Output Files liegen")
    parser.add_argument('--user', type=str, default="TinoMichael",
                        help="zu bearbeitender Mitarbeiter")
    parser.add_argument('--export', nargs='*', default=[],
                        help="schreibt erfasste Zeiten in gegebenen Formaten;\n"
                             "unterstützt: [yml, xls]")

    parser.add_argument('--remove', action='store_true', default=False,
                        help="entfernt den momentanen Tag aus der DB")
    parser.add_argument('--expand', action='store_false', default=None,
                        help="expandiert die anderweitig kompakte Ausgabe der erfassten"
                             " Zeiten")

    out_of_office_group = parser.add_mutually_exclusive_group()
    out_of_office_group.add_argument('-u', '--urlaub', action='store_true', default=None,
                                     help="deklariert den Tag als Urlaubstag:\n"
                                          "keine Arbeit erwartet, kein Saldo verbraucht")
    out_of_office_group.add_argument('-z', '--zeitausgleich', action='store_true',
                                     default=None, help="keine Arbeitszeit, Saldo wird "
                                     "um reguläre Zeit veringert")
    args = parser.parse_args()

    if args.urlaub:
        try:
            args.comment[0:0] = ["Urlaub;"]
        except TypeError:
            args.comment = ["Urlaub"]
    elif args.zeitausgleich:
        try:
            args.comment[0:0] = ["Zeitausgleich;"]
        except TypeError:
            args.comment = ["Zeitausgleich"]

    db_file = args.db_path + args.user + "_Zeiterfassung.yml"
    try:
        db = db or yaml.load(open(db_file), Loader=Loader) or {}
    except FileNotFoundError:
        db = {}

    now = datetime.datetime.now()

    date = args.date or now.date().__str__()
    year, month, day = (int(t) for t in date.split('-'))
    year = args.year or year
    month = args.month or month
    day = args.day or day
    week = datetime.date(year, month, day).isocalendar()[1]

    hours, minutes = (int(t) for t in str(now.time()).split(':')[:-1])
    minutes = minutes - minutes % 15  # rounding minutes to last quarter
    round_down = datetime.datetime(year, month, day, hours, minutes, 00)
    round_up = datetime.datetime(year, month, day, hours, minutes, 00) + \
        datetime.timedelta(minutes=15)

    # get the desired day and create its data base entry if not there yet
    this_day = get_day_from_db(db, year, month, week, day, args.multi_day)

    # populate the desired day with the given information
    if args.remove:
        this_day.update(dict((k, {}) for k in this_day))
    elif args.date is False and args.day is False and args.month is False and \
            args.year is False and args.start is False and args.end is False:
        # if neither of these is set, don't change the current day
        pass
    else:
        # The logic for `start` (and `end`) is as follows:
        # - By default, `start` is `False`, so if it doesn't show up in the list of CL
        #   arguments, the if-statement does not Trigger
        # - If `start` is used in the CL and followed by a time stamp, use that time
        #   as starting time
        # - If `start` is used in the CL but without any parameter, `args.start` will be
        #   `None` and the or-statement will use the current time
        if args.start is not False:
            this_day["start"] = args.start or format_time(round_down.time())
        if args.end is not False:
            this_day["end"] = args.end or format_time(round_up.time())
        if not (args.urlaub or args.zeitausgleich):
            this_day["pause"] = args.pause

        if args.comment is not None:
            # if `comment` flag is set but argument empty, try to remove present comment
            if args.comment:
                this_day["comment"] = " ".join(args.comment)
            else:
                try:
                    del this_day["comment"]
                except KeyError:
                    pass

        # ensure proper order of the start, end, pause tokens
        for key in ["start", "end", "pause", "comment"]:
            # Note: `comment` does get pushed to the end later anyway but do it here
            # aswell for clarity
            try:
                temp = this_day[key]
                del this_day[key]
                this_day[key] = temp
            except KeyError:
                pass

    # recursively remove empty dictionary leaves
    clean_db(db)

    # sort database by date
    db = sort_db(db)

    # calculate over-time saldos on a daily, weekly and monthly basis
    calculate_saldos(db, work_time=args.work_time)

    print(f"\nerfasste Zeiten für {args.user}:\n", db_file)
    print(yaml.dump(db, default_flow_style=args.expand))
    yaml.dump(db, open(db_file, mode="w"), Dumper=Dumper)

    for ending in args.export:
        export_file = args.db_path + args.user + \
            f"_{year}_{month:02}_Zeiterfassung.{{}}"
        if ending in ["yml", "yaml"]:
            yaml.dump(db[year][month],
                      open(export_file.format("yml"), mode="w"),
                      Dumper=Dumper)
        if ending in ["xls", "xlsx", "excel"]:
            export_excel(db, export_file.format("xlsx"))

    return db


def get_day_from_db(db, year, month, week, day, multi_day=False):
    # get the desired day and create its data base entry if not there yet
    # iteratively creates nested dicts up to the desired depth
    while True:
        try:
            if multi_day:
                this_day = db[year][month][week][day][multi_day]

                # if current day was previously a one-block day, reset the relevant
                # entries (they will be removed later by `clean_db`)
                for a in ["start", "end", "pause"]:
                    db[year][month][week][day][a] = {}
            else:
                this_day = db[year][month][week][day]

                # if `this_day` was previously declared multi-day,
                # reset the multi-day fields (they will be removed later by `clean_db`)
                for a, b in this_day.items():
                    if type(b) == dict:
                        this_day[a] = {}
            return this_day

        except KeyError:
            db_temp = db
            try:
                for k in [year, month, week, day, multi_day]:
                    if k:
                        db_temp = db_temp[k]
            except KeyError:
                db_temp[k] = {}


def clean_db(db):
    try:
        for k, v in db.items():
            if isinstance(v, dict):
                clean_db(v)
            if v == {} or "saldo" in str(k) or "Arbeit" in str(k):
                del db[k]
    except RuntimeError:
        clean_db(db)


def sort_db(old_db):
    '''sorts the DB numerically by year -> month -> week -> day
    this assumes all the saldo entries have been removed by `clean_db` just before;
    otherwise, this will break

    preserves the order of strings, i.e. "start" - "end" - "pause", and multi-day tokens,
    it's your responsibility to sort them properly (you can always move them around in
    the .yml file later)
    '''
    try:
        new_db = {}
        for k in sorted(int(l) for l in old_db):
            new_db[k] = sort_db(old_db[k])
        return new_db
    except ValueError:
        # if `l` is a string that cannot be converted to integer, we hit the maximum
        # depth; return the original, not resorted dict
        return old_db


def calculate_saldos(db, work_time="7:42"):
    # calculate over-time saldos on a daily, weekly and monthly basis

    work_hours, work_minutes = (int(t) for t in work_time.split(':'))

    for y, year in db.items():
        year_balance = datetime.timedelta()
        for m, month in year.items():
            month_balance = datetime.timedelta()
            for w, week in month.items():
                week_balance = datetime.timedelta()
                for d, day in week.items():
                    try:
                        # assume this is a multi-part day
                        day_balance = datetime.timedelta()
                        for part in day.values():
                            day_balance += calc_balance(part)

                    except TypeError:
                        # if not, `part["start"]` should throw a `TypeError`
                        # -> "string indices must be integers"
                        # so, go on with the single-part approach
                        day_balance = calc_balance(day)

                    day["Arbeitszeit"] = format_timedelta(day_balance)

                    # check if we are on a working day
                    # TODO check for legal holidays?
                    if datetime.datetime(y, m, d).weekday() < 5:
                        if "comment" not in day or "urlaub" not in day["comment"].lower():
                            day_balance -= datetime.timedelta(hours=work_hours,
                                                              minutes=work_minutes)
                    else:
                        # we are on a weekend day; make this clear in the comment
                        # and set the expected work time to zero
                        day_balance = datetime.timedelta()
                        if "comment" in day:
                            if "Wochenende" not in day["comment"]:
                                day["comment"] = "Wochenende; " + day["comment"]
                        else:
                            day["comment"] = "Wochenende"

                    day["Tagessaldo"] = format_timedelta(day_balance)
                    week_balance += day_balance

                    # if there is a comment, move it to the back of the day-dict
                    try:
                        comm = day["comment"]
                        del day["comment"]
                        day["comment"] = comm
                    except KeyError:
                        pass

                week["Wochensaldo"] = format_timedelta(week_balance)
                month_balance += week_balance
            month["Monatssaldo"] = format_timedelta(month_balance)
            year_balance += month_balance
        year["Jahressaldo"] = format_timedelta(year_balance)


def format_time(t):
    return t[:-3]


def format_timedelta(td):
    if td < datetime.timedelta(0):
        return '-' + format_timedelta(-td)
    else:
        return format_time(str(td))


def calc_balance(day):
    try:
        start = day["start"]
        end = day["end"]
        try:
            pause = day["pause"]
        except KeyError:
            pause = 0
        return (datetime.datetime.strptime(end, '%H:%M') -
                datetime.datetime.strptime(start, '%H:%M') -
                datetime.timedelta(minutes=pause))
    except KeyError:
        print("Achtung: Anfangs- oder Endzeit scheinen zu fehlen!")
        return datetime.timedelta()


def export_excel(db, db_path):
    # TODO implement
    print("export to excel not yet implemented")


if __name__ == "__main__":
    db = main()
