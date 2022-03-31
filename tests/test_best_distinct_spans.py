from src.best_distinct_spans import Spannable, best_distinct_spans


class Span(Spannable):
    def __init__(self, left: int, right: int):
        self._span = (left, right)

    def span(self) -> tuple[int, int]:
        return self._span

    def __eq__(self, other):
        return self._span == other._span


def test_secondary_span_before():
    spans = best_distinct_spans(
        primary=iter([Span(4, 6)]), secondary=iter([Span(0, 2), Span(2, 4)])
    )

    assert list(spans) == [Span(0, 2), Span(2, 4), Span(4, 6)]


def test_secondary_span_after():
    spans = best_distinct_spans(
        primary=iter([Span(2, 5)]),
        secondary=iter([Span(5, 7), Span(7, 9)]),
    )

    assert list(spans) == [Span(2, 5), Span(5, 7), Span(7, 9)]


def test_secondary_span_exactly_equal():
    spans = best_distinct_spans(
        primary=iter([Span(2, 5)]),
        secondary=iter([Span(2, 5)]),
    )

    assert list(spans) == [Span(2, 5)]


def test_secondary_span_starting_overlap():
    spans = best_distinct_spans(
        primary=iter([Span(2, 5)]), secondary=iter([Span(1, 3)])
    )

    assert list(spans) == [Span(2, 5)]


def test_secondary_span_fully_contained():
    spans = best_distinct_spans(
        primary=iter([Span(2, 6)]),
        secondary=iter([Span(3, 5)]),
    )

    assert list(spans) == [Span(2, 6)]


def test_secondary_span_fully_contains_primary():
    spans = best_distinct_spans(
        primary=iter([Span(2, 5)]), secondary=iter([Span(1, 6)])
    )

    assert list(spans) == [Span(2, 5)]
