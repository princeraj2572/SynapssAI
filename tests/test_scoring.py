import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.analytics import compute_score


def test_perfect_day_scores_100():
    score = compute_score(coding_hours=6, study_hours=3, sleep_hours=7, gym_done=True)
    assert score == 100.0


def test_zero_activity_scores_zero():
    score = compute_score(coding_hours=0, study_hours=0, sleep_hours=0, gym_done=False)
    assert score == 0.0


def test_score_caps_at_100():
    score = compute_score(coding_hours=20, study_hours=20, sleep_hours=20, gym_done=True)
    assert score == 100.0


def test_no_gym_loses_points():
    with_gym    = compute_score(coding_hours=6, study_hours=3, sleep_hours=7, gym_done=True)
    without_gym = compute_score(coding_hours=6, study_hours=3, sleep_hours=7, gym_done=False)
    assert with_gym > without_gym


def test_partial_day():
    score = compute_score(coding_hours=3, study_hours=1.5, sleep_hours=6, gym_done=False)
    assert 0 < score < 100
