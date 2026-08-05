from app.services.reranking import reciprocal_rank_fusion


def test_rrf_gives_overlap_higher_score():
    rankings = [["a", "b", "c"], ["b", "a", "d"]]
    scores = reciprocal_rank_fusion(rankings)
    assert scores["a"] == scores["b"]
    assert scores["a"] > scores["c"]
    assert scores["a"] > scores["d"]


def test_rrf_favors_top_ranked_overlap():
    scores = reciprocal_rank_fusion([["x", "y"], ["x", "z"]])
    assert scores["x"] > scores["y"]
    assert scores["x"] > scores["z"]


def test_rrf_handles_empty_lists():
    assert reciprocal_rank_fusion([[], []]) == {}


def test_rrf_deterministic_order():
    first = reciprocal_rank_fusion([["x", "y"], ["y", "x"]])
    second = reciprocal_rank_fusion([["x", "y"], ["y", "x"]])
    assert first == second
