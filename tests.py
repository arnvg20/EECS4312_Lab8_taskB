import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

# Covers C3, AC3
# Verifies that multiple cancellations promote waitlisted users in FIFO order
def test_multiple_waitlist_promotions_after_cancellations():
    er = EventRegistration(capacity=2)

    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")

    er.cancel("u1")
    er.cancel("u2")

    snap = er.snapshot()
    assert snap["registered"] == ["u3", "u4"]
    assert snap["waitlist"] == []

# Covers C4, AC4
# Verifies that a user can re-register after being cancelled from the waitlist
def test_reregister_after_being_waitlisted_and_cancelled():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")  # waitlisted

    er.cancel("u2")

    status = er.register("u2")

    assert status == UserStatus("waitlisted", 1)

# Covers C6, AC6
# Verifies that querying a user not in the system returns "none"
def test_status_of_nonexistent_user_returns_none():
    er = EventRegistration(capacity=3)

    er.register("u1")
    er.register("u2")

    assert er.status("u5") == UserStatus("none")

# Covers C2, C6, AC6
# Verifies deterministic ordering of registered users after operations
def test_snapshot_deterministic_order_after_operations():
    er = EventRegistration(capacity=2)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")

    snap = er.snapshot()

    assert snap["registered"] == ["u2", "u3"]
    assert snap["waitlist"] == []

# Covers C5, AC5
# Verifies that a waitlisted user cancelling updates the waitlist correctly
def test_waitlisted_user_cancels_before_promotion():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u2")

    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]

