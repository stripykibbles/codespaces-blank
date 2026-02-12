import pytest
from project import get_characters, date_parse, date_format



def test_get_characters():
    assert get_characters("0") == 50
    assert get_characters("hello") == 50
    assert get_characters("It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of light, it was the season of darkness, it was the spring of hope, it was the winter of despair.") == 95
    with pytest.raises(TypeError):
        get_characters(50)



def test_date_parse():
    assert date_parse("2025-11-08 10:42:39.75") == ("2025-11-08", "10:42:39")
    assert date_parse("1990-06-02 23:42:00") == ("1990-06-02", "23:42:00")
    with pytest.raises(ValueError):
        date_parse("2025-11-8 10:42")
    with pytest.raises(ValueError):
        date_parse("11/8/25 10:42:39.75")
    with pytest.raises(ValueError):
        date_parse("November 8, 2025 at 10:42am")
    with pytest.raises(ValueError):
        date_parse("dog")



def test_date_format():
    assert date_format("2025-11-08") == "November 8, 2025"
    assert date_format("1953-06-25") == "June 25, 1953"
    assert date_format("1959-04-16") == "April 16, 1959"
    with pytest.raises(ValueError):
        date_format("2025-11-8 10:42")
    with pytest.raises(ValueError):
        date_format("11/8/25 10:42:39.75")
    with pytest.raises(ValueError):
        date_format("November 8, 2025 at 10:42am")
    with pytest.raises(ValueError):
        date_format("dog")
