import sys
from pytest import raises
from zeiterfassung import main


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


def test_wochenend():
    sys.argv[1:] = [
        "--db_path", "/tmp/",
        "--date", "2018-07-21",
        "--user", "test_zeitausgleich",
        "--work_time", "8:00",
        "--start", "9:00",
        "--end", "18:00",
        "--pause", "0",
        "--export", ""
    ]

    db = main(db={})
    day = db[2018][7][29][21]
    assert day["Arbeitszeit"] == day["Tagessaldo"]
    assert "wochenende" in day["comment"].lower()
