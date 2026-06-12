"""Song library page tests."""

from fastapi.testclient import TestClient


def test_library_page_renders(client: TestClient) -> None:
    response = client.get("/library")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "library-grid" in response.text
    assert "quick-start" in response.text
    assert "quick-pdf" in response.text


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


def test_library_quick_pdf_returns_pdf(client: TestClient) -> None:
    """One-click PDF from library should return a valid PDF."""
    response = client.post("/library/twinkle.musicxml/quick-pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_library_quick_pdf_rejects_path_traversal(client: TestClient) -> None:
    """Path traversal attempts should be rejected."""
    response = client.post("/library/..%2F..%2Fetc%2Fpasswd/quick-pdf")

    assert response.status_code in (400, 404)


def test_library_quick_pdf_rejects_missing_song(client: TestClient) -> None:
    response = client.post("/library/nonexistent.musicxml/quick-pdf")

    assert response.status_code == 404


def test_library_page_shows_chord_chips(client: TestClient) -> None:
    """Library page should render chord filter chips for search-by-chords."""
    response = client.get("/library")

    assert response.status_code == 200
    assert "chord-chip" in response.text
    assert "chord-checkboxes" in response.text
    assert "data-chords=" in response.text


def test_library_page_shows_known_chord_only_toggle(client: TestClient) -> None:
    """Library page should offer a mode to show songs playable with only known chords."""
    response = client.get("/library")

    assert response.status_code == 200
    assert 'id="filter-known-only"' in response.text
    assert "只看我會彈的歌" in response.text


def test_library_page_uses_subset_logic_for_known_chord_mode(client: TestClient) -> None:
    """Known-chord mode should require every song chord to be inside the selected set."""
    response = client.get("/library")

    assert response.status_code == 200
    assert "songChords.every(function(c)" in response.text
    assert "selectedChords.indexOf(c) >= 0" in response.text


def test_library_cards_have_chord_data_attribute(client: TestClient) -> None:
    """Each library card should have a data-chords attribute with simplified chords."""
    response = client.get("/library")

    # twinkle.musicxml should have at least C and G chords
    assert 'data-chords="' in response.text
    # Check that chord data is non-empty for at least one card
    import re
    chord_attrs = re.findall(r'data-chords="([^"]*)"', response.text)
    non_empty = [c for c in chord_attrs if c]
    assert len(non_empty) > 0, "At least one song should have chord data"


def test_library_cards_show_chord_count_badge(client: TestClient) -> None:
    """Each library card should display a chord count badge for beginners."""
    response = client.get("/library")

    assert response.status_code == 200
    assert "badge-chords" in response.text
    assert "和弦" in response.text


def test_library_sorted_by_chord_count_easiest_first(client: TestClient) -> None:
    """Library should sort songs by chord count so easiest songs appear first."""
    import re

    response = client.get("/library")
    assert response.status_code == 200

    chord_attrs = re.findall(r'data-chords="([^"]*)"', response.text)
    counts = [len(c.split(",")) if c else 0 for c in chord_attrs]
    # Songs with chords should be sorted ascending by chord count
    nonzero = [c for c in counts if c > 0]
    assert nonzero == sorted(nonzero), f"Chord counts not sorted: {nonzero}"


def test_library_page_has_mastery_sync_button(client: TestClient) -> None:
    """Library page should include a sync-mastery button for importing chord mastery from practice."""
    response = client.get("/library")

    assert response.status_code == 200
    assert 'id="sync-mastery-btn"' in response.text
    assert "syncMasteryChords" in response.text
    assert "ukepack_chord_mastery" in response.text


def test_library_page_has_smart_recommendations_section(client: TestClient) -> None:
    """Library page should include a hidden smart recommendations section populated by JS."""
    response = client.get("/library")

    assert response.status_code == 200
    assert 'id="smart-recommendations"' in response.text
    assert 'id="rec-grid"' in response.text
    assert "推薦給你" in response.text


def test_library_page_has_recommendation_engine_js(client: TestClient) -> None:
    """Library page should include the smart recommendation JS engine."""
    response = client.get("/library")

    assert response.status_code == 200
    # Core recommendation logic
    assert "coverage" in response.text
    assert "rec-card" in response.text
    assert "rec-coverage-fill" in response.text
    assert "Smart Recommendations Engine" in response.text


def test_library_recommendation_shows_coverage_bar(client: TestClient) -> None:
    """Recommendation cards should include a visual coverage progress bar."""
    response = client.get("/library")

    assert response.status_code == 200
    assert "rec-ready" in response.text
    assert "rec-almost" in response.text
    assert "rec-learning" in response.text
    assert "已掌握" in response.text


def test_library_recommendation_sorts_by_coverage_desc(client: TestClient) -> None:
    """Recommendation engine should sort by coverage descending, then level ascending."""
    response = client.get("/library")
    text = response.text

    # Verify sort comparator: coverage descending (b.coverage - a.coverage)
    assert "b.coverage - a.coverage" in text
    # Verify tiebreaker: level ascending (a.level - b.level)
    assert "a.level - b.level" in text


def test_library_recommendation_filters_top_5_with_coverage(client: TestClient) -> None:
    """Recommendation engine should show only top 5 songs with coverage > 0."""
    response = client.get("/library")
    text = response.text

    # Verify coverage > 0 filter
    assert "s.coverage > 0" in text
    # Verify top-5 slice
    assert ".slice(0, 5)" in text


def test_library_recommendation_calculates_coverage(client: TestClient) -> None:
    """Recommendation engine should calculate coverage as knownCount / total chords."""
    response = client.get("/library")
    text = response.text

    # Verify coverage formula: knownCount / songChords.length
    assert "knownCount / songChords.length" in text
    # Verify knownCount is computed via filter
    assert "mastered.indexOf(c) >= 0" in text


def test_library_recommendation_uses_dom_api_not_innerhtml_for_user_data(client: TestClient) -> None:
    """Recommendation cards should use textContent/createElement, not innerHTML with user data."""
    response = client.get("/library")
    text = response.text

    # The recommendation engine section should use createElement + textContent
    # Find the Smart Recommendations Engine block
    engine_start = text.find("Smart Recommendations Engine")
    assert engine_start > 0, "Recommendation engine block not found"
    engine_block = text[engine_start:]

    # Should use textContent for user-derived values (title, chords, etc.)
    assert "textContent" in engine_block
    # Should use createElement for building DOM
    assert "createElement" in engine_block
    # Should NOT use innerHTML with string concatenation of user data
    # (innerHTML is acceptable only for static/structural markup, not user content)
    innerhtml_count = engine_block.lower().count("innerhtml")
    textcontent_count = engine_block.count("textContent")
    assert textcontent_count > innerhtml_count, (
        f"Expected more textContent than innerHTML usage in recommendation engine, "
        f"got textContent={textcontent_count}, innerHTML={innerhtml_count}"
    )


def test_library_recommendation_empty_boundary_has_log(client: TestClient) -> None:
    """Recommendation engine should log when no songs qualify for recommendations."""
    response = client.get("/library")
    text = response.text

    # Verify console.log exists for empty boundary case
    assert "console.log" in text
    assert "跳過推薦" in text or "coverage=0" in text
