"""
Pittsburgh RecDesk Pickleball Court Availability Scraper
Usage: python get_courts.py
       python get_courts.py --date 2026-03-01
       python get_courts.py --date 2026-03-01 --time 10:00
       python get_courts.py --location frick schenley --date 2026-03-01 --time 14:00
"""

import argparse
from datetime import date, datetime
import get_courts_lib

LOCATIONS = {
    "allegheny": "Allegheny",
    "bud-hammer": "Bud Hammer",
    "fineview": "Fineview",
    "frick": "Frick",
    "schenley": "Schenley",
    "washingtons-landing": "Washington",
}


def main():
    parser = argparse.ArgumentParser(
        description="Pittsburgh pickleball court availability"
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Date to check (YYYY-MM-DD), default: today",
    )
    parser.add_argument(
        "--time",
        metavar="HH:MM",
        help="Filter slots to a specific start time, e.g. 10:00",
    )
    parser.add_argument(
        "--location",
        nargs="+",
        choices=LOCATIONS.keys(),
        metavar="LOCATION",
        help=f"Filter by location(s): {', '.join(LOCATIONS.keys())}",
        default=["washingtons-landing"],
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Just list courts, don't check availability",
    )
    args = parser.parse_args()

    check_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    session = get_courts_lib.get_session()
    facilities = get_courts_lib.get_all_facilities(session)

    if args.location:
        keywords = [LOCATIONS[loc].lower() for loc in args.location]
        facilities = [
            f for f in facilities if any(kw in f["Name"].lower() for kw in keywords)
        ]

    if not facilities:
        print("No facilities found.")
        return

    if args.list_only:
        return

    time_label = f" from {args.time}" if args.time else ""
    print(f"\nChecking courts in {', '.join (args.location)}...")
    print(f"\n=== Available courts on {check_date}{time_label} ===\n")

    available = []
    for f in facilities:
        slots = get_courts_lib.get_availability(session, f["Id"], check_date)
        if not slots:
            continue
        result = get_courts_lib.first_available_after(slots, after_time=args.time)
        if result:
            available.append((f["Name"], result[0], result[1]))

    if not available:
        print("  No courts available.")
        return

    name_w = max(len(name) for name, _, _ in available) + 2
    for name, start, duration in available:
        hrs, mins = divmod(duration, 60)
        dur_str = f"{hrs}h {mins}m" if hrs else f"{mins}m"
        print(f"  {name:<{name_w}}  available from {start}  ({dur_str})")


if __name__ == "__main__":
    main()
