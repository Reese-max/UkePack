"""Song library page tests."""

from fastapi.testclient import TestClient


def test_library_page_renders(client: TestClient) -> None:
    response = client.get("/library")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "library-grid" in response.text
    assert "quick-start" in response.text


def test_library_page_shows_difficulty_badges(client: TestClient) -> None:
    """Library cards should display difficulty level badges."""
    response = client.get("/library")

    # Badge CSS classes indicate difficulty levels rendered
    assert "badge-level-" in response.text


def test_library_page_shows_filter_controls(client: TestClient) -> None:
    """When multiple keys exist, filter dropdowns should appear."""
    response = client.get("/library")

    assert 'id="filter-level"' in response.text
    assert 'id="filter-key"' in response.text
    assert 'id="filter-count"' in response.text


def test_library_page_shows_song_metadata(client: TestClient) -> None:
    """Each song card should show key and BPM data cells."""
    response = client.get("/library")

    assert "data-cell" in response.text
    assert "twinkle.musicxml" in response.text


def test_library_page_shows_composer(client: TestClient) -> None:
    """Songs with embedded composer metadata should display the name."""
    response = client.get("/library")

    # twinkle.musicxml has <creator type="composer">Traditional</creator>
    assert "Traditional" in response.text


def test_library_quick_start_creates_project(client: TestClient) -> None:
    """One-click from library should create a project and redirect to analysis."""
    response = client.post(
        "/library/twinkle.musicxml/quick-start",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "/projects/" in response.headers["location"]


def test_library_quick_start_rejects_path_traversal(client: TestClient) -> None:
    """Path traversal attempts should be rejected."""
    response = client.post("/library/..%2F..%2Fetc%2Fpasswd/quick-start")

    # FastAPI returns 400 for invalid path params or 404 if route doesn't match
    assert response.status_code in (400, 404)


def test_library_quick_start_rejects_missing_song(client: TestClient) -> None:
    response = client.post("/library/nonexistent.musicxml/quick-start")

    assert response.status_code == 404


def test_library_quick_start_result_has_score_data(client: TestClient) -> None:
    """Quick-start project should have parsed score data for analysis."""
    resp = client.post(
        "/library/twinkle.musicxml/quick-start",
        follow_redirects=True,
    )

    assert resp.status_code == 200
    # Analysis page should show chords (score was parsed)
    assert "chord" in resp.text.lower() or "和弦" in resp.text
