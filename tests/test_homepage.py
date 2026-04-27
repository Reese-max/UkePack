"""Homepage UI smoke tests."""

from fastapi.testclient import TestClient


def test_homepage_renders_message_and_ctas(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "把你的歌變成小朋友也能練的烏克麗麗練習包。" in response.text
    for label in ("建立練習包", "匯入 MusicXML", "看範例", "老師專區"):
        assert label in response.text
    assert 'href="/samples/public_domain/twinkle.musicxml"' in response.text


def test_public_sample_route_serves_twinkle_fixture(client: TestClient) -> None:
    response = client.get("/samples/public_domain/twinkle.musicxml")

    assert response.status_code == 200
    assert "charset=utf-8" in response.headers["content-type"]
    assert "<score-partwise" in response.text
