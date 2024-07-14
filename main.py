import datetime
from dateutil import parser

def get_unix_timestamp(date_string):
    date = parser.parse(date_string)
    return int(date.timestamp())

def main():
    date_confirmed_from = get_unix_timestamp(input("Enter start date (YYYY-MM-DD): "))
    date_confirmed_to = get_unix_timestamp(input("Enter end date (YYYY-MM-DD): "))

    # Ustawienia przekazywane do plików
    config = {
        'date_confirmed_from': date_confirmed_from,
        'date_confirmed_to': date_confirmed_to
    }

    # Run PLN summary
    exec(open('main_pln.py').read(), config)

    # Run EUR summary
    exec(open('main_eur.py').read(), config)

    # Run CZK summary
    exec(open('main_czk.py').read(), config)

if __name__ == "__main__":
    main()
