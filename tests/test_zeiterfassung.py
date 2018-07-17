from zeiterfassung import main
import sys
import yaml


def print_yaml(db):
    print(yaml.dump(db, default_flow_style=False))


def test_db_from_scratch():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_db_from_scratch",
        "--work_time", "8:00",
        "--start", "9:00",
        "--end", "17:30",
        "--export", ""]

    db = main(db={})

    assert db == {2018: {7: {29: {
        18: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '0:00'},
        'Wochensaldo': '0:00'},
        'Monatssaldo': '0:00'},
        'Jahressaldo': '0:00'}}


def test_add_day():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_add_day",
        "--work_time", "8:00",
        "--start", "8:00",
        "--end", "17:30",
        "--export", ""]

    pre_db = {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '0:00'},
        'Wochensaldo': '0:00'},
        'Monatssaldo': '0:00'},
        'Jahressaldo': '0:00'}}

    db = main(db=pre_db)

    assert db == {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '0:00'},
        18: {'start': '8:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '9:00',
             'Tagessaldo': '1:00'},
        'Wochensaldo': '1:00'},
        'Monatssaldo': '1:00'},
        'Jahressaldo': '1:00'}}


def test_fix_saldos():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_fix_saldos",
        "--work_time", "8:00",
        "--start", "8:00",
        "--end", "17:30",
        "--export", ""]

    pre_db = {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '5:00'},
        'Wochensaldo': '1:00'},
        'Monatssaldo': '2:00'},
        'Jahressaldo': '3:00'}}

    db = main(db=pre_db)

    assert db == {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '0:00'},
        18: {'start': '8:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '9:00',
             'Tagessaldo': '1:00'},
        'Wochensaldo': '1:00'},
        'Monatssaldo': '1:00'},
        'Jahressaldo': '1:00'}}


def test_pause():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_pause",
        "--work_time", "8:00",
        "--start", "8:00",
        "--end", "18:00",
        "--export", "",
        "--pause", "0"]

    db = main(db={})
    day = db[2018][7][29][18]
    assert day["start"] == "8:00"
    assert day["end"] == "18:00"
    assert day["pause"] == 0
    assert day["Arbeitszeit"] == "10:00"
    assert day["Tagessaldo"] == "2:00"

    sys.argv[-1] = "30"
    db = main(db={})
    day = db[2018][7][29][18]
    assert day["start"] == "8:00"
    assert day["end"] == "18:00"
    assert day["pause"] == 30
    assert day["Arbeitszeit"] == "9:30"
    assert day["Tagessaldo"] == "1:30"


def test_urlaub():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_urlaub",
        "--export", "",
        "--urlaub"
    ]

    db = main(db={})
    day = db[2018][7][29][18]
    assert "urlaub" in day["comment"].lower()
    assert "start" not in day
    assert "end" not in day
    assert "pause" not in day
    assert day["Tagessaldo"] == "0:00"


def test_zeitausgleich():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_zeitausgleich",
        "--work_time", "8:00",
        "--export", "",
        "--zeitausgleich"
    ]

    db = main(db={})
    day = db[2018][7][29][18]
    assert "zeitausgleich" in day["comment"].lower()
    assert "start" not in day
    assert "end" not in day
    assert "pause" not in day
    assert day["Tagessaldo"] == "-8:00"


def test_work_time():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_work_time",
        "--start", "8:00",
        "--end", "18:00",
        "--export", "",
        "--pause", "0",
        "--work_time", "8:00"
    ]

    # pause is at 0 min and working time is at 8 h
    db = main(db={})
    day = db[2018][7][29][18]
    assert day["pause"] == 0
    assert day["Arbeitszeit"] == "10:00"
    assert day["Tagessaldo"] == "2:00"

    # set pause to 30 min and working time to 8 h
    sys.argv[-4:] = ["--pause", "30", "--work_time", "8:00"]
    db = main(db={})
    day = db[2018][7][29][18]
    assert day["pause"] == 30
    assert day["Arbeitszeit"] == "9:30"
    assert day["Tagessaldo"] == "1:30"

    # set pause to 0 min working time to 7:30 h
    sys.argv[-4:] = ["--pause", "0", "--work_time", "7:30"]
    db = main(db={})
    day = db[2018][7][29][18]
    assert day["pause"] == 0
    assert day["Arbeitszeit"] == "10:00"
    assert day["Tagessaldo"] == "2:30"

    # set pause to 30 min and working time to 7:30
    sys.argv[-4:] = ["--pause", "30", "--work_time", "7:30"]
    db = main(db={})
    day = db[2018][7][29][18]
    assert day["pause"] == 30
    assert day["Arbeitszeit"] == "9:30"
    assert day["Tagessaldo"] == "2:00"
