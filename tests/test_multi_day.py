import sys
from pytest import raises
from zeiterfassung import main


def test_multi_day_add():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_multi_day_add",
        "--start", "8:00",
        "--end", "12:00",
        "--multi_day", "a",
        "--export", "",
        "--pause", "30",
        "--work_time", "8:00"
    ]

    db = main(db={})
    day = db[2018][7][29][18]

    assert "a" in day.keys()
    assert day["a"] == {"start": '8:00', "end": '12:00', "pause": 30}

    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_multi_day_add",
        "--start", "12:00",
        "--end", "18:00",
        "--multi_day", "b",
        "--export", "",
        "--pause", "0",
        "--work_time", "8:00"
    ]

    db = main(db={})
    day = db[2018][7][29][18]

    assert "a" in day.keys() and "b" in day.keys()
    assert day["Arbeitszeit"] == '9:30'
    assert day["Tagessaldo"] == '1:30'


def test_multi_day_remove_part():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_multi_day_remove_part",
        "--multi_day", "b",
        "--export", "",
        "--remove"
    ]

    db = {2018: {7: {29: {18: {
        "a": {"start": '8:00', "end": '12:00', "pause": 30},
        "b": {"start": '12:00', "end": '18:00', "pause": 0}
    }}}}}

    db = main(db=db)
    day = db[2018][7][29][18]

    assert "a" in day.keys()
    assert "b" not in day.keys()


def test_multi_day_remove_day():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-18",
        "--user", "test_multi_day_remove_day",
        "--export", "",
        "--remove"
    ]

    db = {2018: {7: {29: {
        17: {"start": '8:00', "end": '18:00', "pause": 30},
        18: {
            "a": {"start": '8:00', "end": '12:00', "pause": 30},
            "b": {"start": '12:00', "end": '18:00', "pause": 0}
        }}}}}

    db = main(db=db)

    with raises(KeyError):
        day = db[2018][7][29][18]
