from app.configs.settings import parse_movie_ids


def test_parse_movie_ids_empty():
    assert parse_movie_ids(None) == []
    assert parse_movie_ids("") == []


def test_parse_movie_ids_valid_and_invalid_tokens():
    raw = "299534, abc, 19995, , 140607"
    assert parse_movie_ids(raw) == [299534, 19995, 140607]
