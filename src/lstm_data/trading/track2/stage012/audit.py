"""Bounded calendar-only witness CLI. No market prices, intents or returns."""
from datetime import timedelta
from pathlib import Path
import argparse
import json
from zoneinfo import ZoneInfo
import exchange_calendars
from .calendar_schedule import MarketClock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise SystemExit('APPEND_ONLY_OUTPUT_REQUIRED')
    clock=MarketClock('2012-10-01','2025-01-10')
    rows=[]
    for day in ('2024-01-08','2024-11-29','2024-03-08','2024-11-01','2012-10-26','2018-12-04'):
        for origin in clock.origins(day):
            issue=origin+timedelta(minutes=2)
            endpoint=clock.endpoint(origin)
            rows.append(dict(origin_et=origin.astimezone(ZoneInfo('America/New_York')).isoformat(),
                             endpoint_et=endpoint.astimezone(ZoneInfo('America/New_York')).isoformat(),
                             assumed_issue_utc=issue.isoformat(),
                             earliest_entry_observation_utc=clock.next_observation(issue).isoformat(),
                             earliest_exit_observation_utc=clock.next_observation(endpoint+timedelta(minutes=2)).isoformat()))
    # Bounded geometry-only concurrency including Thanksgiving half session/weekend.
    events=[]
    for day in clock.calendar.loc['2024-11-25':'2024-12-03'].index:
        for origin in clock.origins(str(day.date())):
            events.extend(((clock.next_observation(origin+timedelta(minutes=2)),1),
                           (clock.next_observation(clock.endpoint(origin)+timedelta(minutes=2)),-1)))
    active=maximum=0
    for _,delta in sorted(events):
        active+=delta
        maximum=max(maximum,active)
    payload=dict(kind='SYNTHETIC_CALENDAR_ONLY',calendar_package_version=exchange_calendars.__version__,
                 rows=rows, concurrency_window='2024-11-25 through2024-12-03',
                 max_cohort_vintages_assuming_all_entries=maximum,
                 warning='bounded geometry witness; never a universal concurrency cap')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2)+'\n')


if __name__=='__main__':
    main()
