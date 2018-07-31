import sys
from pytest import raises
from zeiterfassung import main


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
