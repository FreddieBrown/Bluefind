import pytest
import bluefind.bluezutils as bz

def test_break_down_message():
    msg = "1=(57.0461, -10.9456)|2=AB:CD:EF:GH:IJ:KL|"
    broken = bz.break_down_message(msg)
    assert "AB:CD:EF:GH:IJ:KL" in broken["2"]

def test_build_message():
    locations = ["57.0461, -10.9456"]
    addresses=["AB:CD:EF:GH:IJ:KL"]
    msg = bz.build_message(locations, addresses)
    assert msg == "1=(57.0461, -10.9456)|2=AB:CD:EF:GH:IJ:KL|"
    broken = bz.break_down_message(msg)
    assert "AB:CD:EF:GH:IJ:KL" in broken["2"]

def test_build_message_filter():
    locations = ["57.0461, -10.9456"]
    addresses=["AB:CD:EF:GH:IJ:KL", "MN:OP:QR:ST:UV:WX"]
    msg = bz.build_message(locations, addresses, filter_addr= ["MN:OP:QR:ST:UV:WX"])
    assert msg == "1=(57.0461, -10.9456)|2=AB:CD:EF:GH:IJ:KL|"
    broken = bz.break_down_message(msg)
    assert "AB:CD:EF:GH:IJ:KL" in broken["2"]
    assert "MN:OP:QR:ST:UV:WX" not in broken["2"]

def test_from_byte_array():
    msg = "string"
    bytev = [115, 116, 114, 105, 110, 103]
    out = bz.from_byte_array(bytev)
    assert out == msg

def test_split_message():
    msg = "HelloThereMyNameIsFreddie"
    gold = ["HelloThereMyNam", "eIsFreddie", "\x05"]
    split = bz.split_message(msg)
    assert gold == split

def test_dbus_to_MAC():
    string = "/org/bluez/hci0/dev_AB_CD_EF_GH_IJ_KL"
    mac = bz.dbus_to_MAC(string)
    assert "AB:CD:EF:GH:IJ:KL" == mac

def test_get_sequence_number():
    msg = "1\x01HelloThereMyNam"
    seq, message = bz.get_sequence_number(msg)
    assert seq == "1"
    assert message == "HelloThereMyNam"

def test_build_generic_message():
    msg_to_build = {
        1 : ["(57.0461, -10.9456)"], 
        2 : ["AB:CD:EF:GH:IJ:KL"]
    }
    generic = bz.build_generic_message(msg_to_build)
    assert generic == "1=(57.0461, -10.9456)|2=AB:CD:EF:GH:IJ:KL|"
    broken = bz.break_down_message(generic)
    assert "AB:CD:EF:GH:IJ:KL" in broken["2"]

def test_utf_to_byte_string():
    msg = "Hi"
    byte_msg = b'Hi'
    converted = bz.utf_to_byte_string(msg)
    assert converted == byte_msg

def test_bytestring_to_uf8():
    msg = "Hi"
    byte_msg = b'Hi'
    converted = bz.bytestring_to_uf8(byte_msg)
    assert converted == msg