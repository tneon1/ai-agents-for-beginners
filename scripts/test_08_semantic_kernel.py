# Small unit tests for the parsers in 08-semantic-kernel.ipynb
# This script does NOT perform any network calls. It only validates
# the parsing logic for selection and termination functions.

REVIEWER_NAME = "Concierge"
FRONTDESK_NAME = "FrontDesk"


def termination_parser(result):
    try:
        if not result or not getattr(result, "value", None):
            return False
        return str(result.value[0]).strip().lower() == "yes"
    except Exception:
        return False


def selection_parser(result):
    try:
        if not result or not getattr(result, "value", None):
            return FRONTDESK_NAME
        val = str(result.value[0]).strip()
        val_norm = val.lower()
        if val_norm == REVIEWER_NAME.lower():
            return REVIEWER_NAME
        if val_norm == FRONTDESK_NAME.lower():
            return FRONTDESK_NAME
        return FRONTDESK_NAME
    except Exception:
        return FRONTDESK_NAME


class MockResult:
    def __init__(self, value):
        # value should be a list-like sequence (matching notebook expectations)
        self.value = value


def run_tests():
    failures = []

    # termination_parser tests
    cases_term = [
        (MockResult(["yes"]), True),
        (MockResult([" Yes "]), True),
        (MockResult(["no"]), False),
        (None, False),
        (MockResult([]), False),
        (MockResult([None]), False),
    ]

    for i, (inp, expected) in enumerate(cases_term, start=1):
        out = termination_parser(inp)
        ok = out == expected
        print(f"termination case {i}: expected={expected} got={out} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(("termination", i, expected, out))

    # selection_parser tests
    cases_sel = [
        (None, FRONTDESK_NAME),
        (MockResult(["Concierge"]), REVIEWER_NAME),
        (MockResult(["frontdesk"]), FRONTDESK_NAME),
        (MockResult(["unknown"]), FRONTDESK_NAME),
        (MockResult([" FrontDesk "]), FRONTDESK_NAME),
    ]

    for i, (inp, expected) in enumerate(cases_sel, start=1):
        out = selection_parser(inp)
        ok = out == expected
        print(f"selection case {i}: expected={expected} got={out} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(("selection", i, expected, out))

    if failures:
        print('\nSome tests failed:')
        for f in failures:
            print(f)
        return 1

    print('\nAll tests passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(run_tests())
