"""Scratch pruning rides the gateway housekeeping tick, because the per-process gate in
``get_scratch_dir`` fires once per process.

A gateway that stays up for days spends that single chance on whichever call comes first. When
that call lands inside the hour the previous pass stamped -- a restart minutes after a prune, or
any boot short of the hour -- it prunes nothing and the process never asks again, so a long-lived
deployment accumulates every artifact it wrote since. One such deployment reached 5 days and
18 MB that way. The chore re-asks the stamped hour on every tick; the hour, not the process age,
is the floor.
"""

import gateway.run as gateway_run


class _OneTickStopEvent:
    def __init__(self):
        self.waited = False

    def is_set(self):
        return self.waited

    def wait(self, timeout=None):
        self.waited = True
        return True


def test_gateway_housekeeping_reasks_the_scratch_hour(monkeypatch):
    import hermes_constants as constants

    calls = []
    monkeypatch.setattr(constants, "prune_scratch_dir_if_due", lambda: calls.append(True))

    gateway_run._start_gateway_housekeeping(_OneTickStopEvent(), interval=0)

    assert calls == [True]
