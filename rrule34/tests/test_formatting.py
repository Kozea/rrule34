from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule)

from ..formatting import format_rrule


def test_simple_rrules():
    assert format_rrule(rrule(freq=SECONDLY)) == 'Every seconds'
    assert format_rrule(rrule(freq=MINUTELY)) == 'Every minutes'
    assert format_rrule(rrule(freq=HOURLY)) == 'Every hours'
    assert format_rrule(rrule(freq=DAILY)) == 'Every days'
    assert format_rrule(rrule(freq=WEEKLY)) == 'Every weeks'
    assert format_rrule(rrule(freq=MONTHLY)) == 'Every months'
    assert format_rrule(rrule(freq=YEARLY)) == 'Every years'

    assert format_rrule(rrule(freq=SECONDLY), 'fr_FR') == 'Toutes les secondes'
    assert format_rrule(rrule(freq=MINUTELY), 'fr_FR') == 'Toutes les minutes'
    assert format_rrule(rrule(freq=HOURLY), 'fr_FR') == 'Toutes les heures'
    assert format_rrule(rrule(freq=DAILY), 'fr_FR') == 'Tous les jours'
    assert format_rrule(rrule(freq=WEEKLY), 'fr_FR') == 'Toutes les semaines'
    assert format_rrule(rrule(freq=MONTHLY), 'fr_FR') == 'Tous les mois'
    assert format_rrule(rrule(freq=YEARLY), 'fr_FR') == 'Tous les ans'
