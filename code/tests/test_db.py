import pytest
import bluefind.db as bdb
import datetime

def test_insert_and_select():
    database = bdb.Database("../find.db")
    now = datetime.datetime.now()
    entries = [("AB:CD:EF:GH:IJ:KL", "57.0461, -10.9456", now)]
    database.insert(entries)
    entries = database.select(1)
    assert "57.0461, -10.9456" in entries[0]
    assert "AB:CD:EF:GH:IJ:KL" in entries[1]

def test_insert_and_select_em():
    database = bdb.Database("../find.db")
    now = datetime.datetime.now()
    database = bdb.Database("../find.db")
    now = datetime.datetime.now()
    entries = [("MN:OP:QR:ST:UV:WX", "57.0461, -10.9456", now)]
    database.insert(entries)
    entries = database.select_em(100)
    assert "57.0461, -10.9456" in entries[0]
    assert "MN:OP:QR:ST:UV:WX" in entries[1]
    assert now.strftime("%Y-%m-%d %H:%M:%S.%f") in entries[2]