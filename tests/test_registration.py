import pytest

from swarm_powerbi_bot.services.registration import parse_start_arg


def test_parse_valid_arg():
    cid, did = parse_start_arg("123-be17610e-e46e-406c-9a51-c1ec76ee82b1")
    assert cid == 123
    assert did == "be17610e-e46e-406c-9a51-c1ec76ee82b1"


def test_parse_empty_arg():
    with pytest.raises(ValueError, match="не активирована"):
        parse_start_arg("")


def test_parse_no_dash():
    with pytest.raises(ValueError, match="некорректна"):
        parse_start_arg("nope")


def test_parse_bad_customer_id():
    with pytest.raises(ValueError, match="customerId"):
        parse_start_arg("abc-be17610e-e46e-406c-9a51-c1ec76ee82b1")


def test_parse_short_dataset_id():
    with pytest.raises(ValueError, match="datasetId"):
        parse_start_arg("123-short")
