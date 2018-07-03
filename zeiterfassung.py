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

    day_group.add_argument('-c', '--comment', type=str, nargs='*', default=[],
                           help="optionaler Kommentar zum Eintrag")

    day_group.add_argument('--multi_day', type=str, default=False,
                           help="ermoeglicht mehrere Eintraege pro Tag")

    parser.add_argument('-w', '--work_time', type=str, default='7:42',
                        help="Arbeitspensum pro Tag; Format H:MM")

    parser.add_argument('--db_path', type=str, default=os.getcwd(),
                        help="Ort, an dem die In- und Output Files liegen")
    parser.add_argument('--user', type=str, default="TinoMichael",
                        help="zu bearbeitender Mitarbeiter")
    parser.add_argument('--export', nargs='*', default=["yml"],
                        help="schreibt erfasste Zeiten in gegebenen Formaten;\n"
                             "unterstuetzt: [yml, xls]")

    args = parser.parse_args()

    args.work_hours, args.work_minutes = (int(t) for t in args.work_time.split(':'))

    if args.start is None and args.end is None:
        print("bitte nicht 'jetzt' fuer Arbeitsanfang und -ende benutzen")
        sys.exit()

    db_file = args.db_path + os.sep + args.user + "_Zeiterfassung.yml"
    try:
        db = db or yaml.load(open(db_file), Loader=Loader)
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
    while True:
        try:
            if args.multi_day:
                this_day = db[year][month][week][day][args.multi_day]
            else:
                this_day = db[year][month][week][day]
            break
        except KeyError:
            db_temp = db
            try:
                for k in [year, month, week, day, args.multi_day]:
                    if k:
                        db_temp = db_temp[k]
            except KeyError:
                db_temp[k] = {}

    # populate the desired day with the given information
    if args.start is not False:
        this_day["start"] = args.start or format_time(round_down.time())
    if args.end is not False:
        this_day["end"] = args.end or format_time(round_up.time())
    if args.comment is not None:
        if not args.comment:
            try:
                del this_day["comment"]
            except KeyError:
                pass
        else:
            this_day["comment"] = " ".join(args.comment)

    this_day["pause"] = args.pause

    # recursively remove empty dictionary leaves
    clean_db(db)

    # calculate over-time on a daily, weekly and monthly basis
    for year in db.values():
        for month in year.values():
            month_balance = datetime.timedelta()
            for week in month.values():
                week_balance = datetime.timedelta()
                for day in week.values():
                    day_balance = -datetime.timedelta(hours=args.work_hours,
                                                      minutes=args.work_minutes)
                    try:
                        # assume this is a multi-part day
                        for part in day.values():
                            day_balance += calc_balance(part)

                    except TypeError:
                        # if not, `part["start"]` should throw a `TypeError`
                        # -> "string indices must be integers"
                        # so, go on with the single-part approach
                        day_balance += calc_balance(day)

                    day["Tagessaldo"] = format_time(format_timedelta(day_balance))
                    week_balance += day_balance
                week["Wochensaldo"] = format_time(format_timedelta(week_balance))
                month_balance += week_balance
            month["Monatssaldo"] = format_time(format_timedelta(month_balance))

    print(f"erfasste Zeiten fuer {args.user}:")
    print(yaml.dump(db))

    for ending in args.export:
        if ending in ["yml", "yaml"]:
            yaml.dump(db, open(db_file, mode="w"), Dumper=Dumper)
        if ending in ["xls", "xlsx", "excel"]:
            export_excel(db, args.db_path)

    return db


def clean_db(db):
    try:
        for k, v in db.items():
            if isinstance(v, dict):
                clean_db(v)
            if v == {} or "saldo" in str(k):
                del db[k]
    except RuntimeError:
        clean_db(db)


def format_time(t):
    return ':'.join(str(t).split(':')[:-1])


def format_timedelta(td):
    if td < datetime.timedelta(0):
        return '-' + format_timedelta(-td)
    else:
        return str(td)


def calc_balance(day):
    start = day["start"]
    end = day["end"]
    pause = day["pause"]
    return (datetime.datetime.strptime(end, '%H:%M') -
            datetime.datetime.strptime(start, '%H:%M') -
            datetime.timedelta(minutes=pause))


def export_excel(db, db_path):
    # TODO implement
    pass


if __name__ == "__main__":
    db = main()
