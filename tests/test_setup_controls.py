"""The setup screen's Segmented control and Switch."""

import pytest
from PySide6.QtWidgets import QApplication

from copilot.setup import Segmented, Switch

OPTIONS = [("Short", "short"), ("Medium", "medium"), ("Long", "long")]


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def segmented(application):
    widget = Segmented(OPTIONS)
    yield widget
    widget.close()
    widget.deleteLater()
    application.processEvents()


@pytest.fixture
def emitted(segmented):
    values = []
    segmented.changed.connect(values.append)
    return values


def checked(segmented):
    return [value for value, button in segmented.buttons.items() if button.isChecked()]


def test_segmented_has_one_button_per_option(segmented):
    assert list(segmented.buttons) == ["short", "medium", "long"]
    assert [button.text() for button in segmented.buttons.values()] == ["Short", "Medium", "Long"]


def test_segmented_value_is_empty_before_a_choice(segmented):
    assert segmented.value() == ""
    assert checked(segmented) == []


def test_clicking_a_button_emits_changed_and_selects_it(segmented, emitted):
    segmented.buttons["medium"].click()

    assert emitted == ["medium"]
    assert segmented.value() == "medium"


def test_only_one_button_is_checked_at_a_time(segmented, emitted):
    segmented.buttons["short"].click()
    segmented.buttons["long"].click()

    assert emitted == ["short", "long"]
    assert checked(segmented) == ["long"]
    assert segmented.value() == "long"


def test_set_value_selects_without_emitting_changed(segmented, emitted):
    segmented.set_value("long")

    assert segmented.value() == "long"
    assert checked(segmented) == ["long"]
    assert emitted == []


def test_set_value_replaces_the_previous_selection(segmented):
    segmented.set_value("short")
    segmented.set_value("medium")

    assert checked(segmented) == ["medium"]


def test_set_value_with_no_matching_option_selects_nothing(segmented, emitted):
    segmented.set_value("short")

    segmented.set_value("not-an-option")

    assert checked(segmented) == []
    assert segmented.value() == ""
    assert emitted == []


def test_group_still_works_after_an_unmatched_value(segmented, emitted):
    segmented.set_value("short")
    segmented.set_value("not-an-option")

    segmented.buttons["medium"].click()
    segmented.buttons["long"].click()

    assert segmented.group.exclusive()
    assert emitted == ["medium", "long"]
    assert checked(segmented) == ["long"]


@pytest.mark.parametrize("start", [False, True])
def test_switch_starts_as_given_and_a_click_toggles_it(application, start):
    switch = Switch(checked=start)
    try:
        assert switch.isCheckable()
        assert switch.isChecked() is start

        switch.click()
        assert switch.isChecked() is not start

        switch.click()
        assert switch.isChecked() is start
    finally:
        switch.deleteLater()
        application.processEvents()


def test_switch_is_off_by_default_and_34_by_20(application):
    switch = Switch()
    try:
        assert not switch.isChecked()
        assert (switch.width(), switch.height()) == (34, 20)
        assert switch.minimumSize() == switch.maximumSize()
    finally:
        switch.deleteLater()
        application.processEvents()
