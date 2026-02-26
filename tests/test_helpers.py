from app.extraction.helpers import load_json, save_json


def test_save_and_load_json_round_trip(tmp_path):
    payload = {"id": 1, "title": "Test Movie"}
    file_path = tmp_path / "movie.json"

    save_json(payload, file_path)
    loaded = load_json(file_path)

    assert loaded == payload
