from typing import Iterator, Protocol, TypeVar


class Spannable(Protocol):
    def span(self) -> tuple[int, int]:
        raise NotImplementedError()


T = TypeVar("T", bound=Spannable)


def best_distinct_spans(primary: Iterator[T], secondary: Iterator[T]) -> Iterator[T]:
    """
    Return an Iterator of all non-overlapping Spannables in the primary and secondary
    collections of Spannables. In the case of overlap, the Spannable from the secondary
    collection will be omitted.

    :param primary: A sorted iterator of non-overlapping Spannable objects
    :param secondary: A sorted iterator of non-overlapping Spannable objects
    :return: The non-overlapping spannables in sorted order
    """

    primary_span = next(primary, None)
    secondary_span = next(secondary, None)

    while secondary_span is not None:
        if primary_span is None:
            yield secondary_span
            secondary_span = next(secondary, None)
            continue

        (primary_start, primary_end) = primary_span.span()
        (secondary_start, secondary_end) = secondary_span.span()

        # Need to cover direct overlaps
        if secondary_end <= primary_start:
            # No overlap (before start)
            yield secondary_span
            secondary_span = next(secondary, None)
        elif secondary_end <= primary_end:
            # overlap at start, fully contained, or identical
            secondary_span = next(secondary, None)
        elif secondary_start < primary_end <= secondary_end:
            # overlap at end
            secondary_span = next(secondary, None)
            yield primary_span
            primary_span = next(primary, None)
        elif secondary_start >= primary_end:
            # no overlap (after end)
            yield primary_span
            primary_span = next(primary, None)

    while primary_span is not None:
        yield primary_span
        primary_span = next(primary, None)
