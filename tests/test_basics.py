import sys
from pytest import raises
from zeiterfassung import main


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

    db = {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '5:00'},
        'Wochensaldo': '1:00'},
        'Monatssaldo': '2:00'},
        'Jahressaldo': '3:00'}}

    db = main(db=db)

    assert db == {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '8:00',
             'Tagessaldo': '0:00'},
        18: {'start': '8:00', 'end': '17:30', 'pause': 30, 'Arbeitszeit': '9:00',
             'Tagessaldo': '1:00'},
        'Wochensaldo': '1:00'},
        'Monatssaldo': '1:00'},
        'Jahressaldo': '1:00'}}


def test_no_new_day():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_no_new_day",
        "--export", ""]

    db = {2018: {7: {29: {
        17: {'start': '9:00', 'end': '17:30', 'pause': 30}}}}}

    db = main(db=db)

    with raises(KeyError):
        day = db[2018][7][29][18]
