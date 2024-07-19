import requests
import json
import os
import argparse
from datetime import datetime, timedelta
import asyncio
from telegram import Bot

# Telegram bot token
TOKEN = 'put_telegram_token_here'
# Telegram channel username or ID
CHANNEL_ID = 'put_telegram_channel_id_here'

# JSON file path
JSON_FILE_PATH = 'discovered_movies.json'

# API endpoints and theaters
API_ENDPOINT = 'https://www.regmovies.com/api/getShowtimes'
THEATRES = '1937,1942,1958'  # Example theater codes

# Define headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_showtimes():
    response = requests.get(f'{API_ENDPOINT}?theatres={THEATRES}', headers=HEADERS)
    return response.json()

def fetch_showtimes_by_ho_code(ho_code, date=None):
    url = f'{API_ENDPOINT}?theatres={THEATRES}&hoCode={ho_code}'
    if date:
        url += f"&date={date}"
    response = requests.get(url, headers=HEADERS)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for HO code {ho_code} on date {date}")
        return None

def format_film_link(title, code):
    formatted_title = title.lower().replace(':', '').replace('&', '').replace(',', '').replace('.','').replace('(','').replace(')','').replace('/','').replace('- ', '-').replace(' ','-').replace('--','-').replace("'","").replace('!','').replace('[','').replace(']','')
    return f'https://www.regmovies.com/movies/{formatted_title}-{code}'.lower()

def format_showtime(showtime):
    return showtime.strftime('%I:%M %p')

def format_showdate(showtime):
    today = datetime.now().date()
    if showtime.date() == today:
        return "Today"
    elif showtime.date() < today + timedelta(days=7):
        return showtime.strftime('%A')
    else:
        return showtime.strftime('%Y-%m-%d')

def fetch_ho_codes(testing=False):
    data = fetch_showtimes()
    movies = data['movies']
    ho_codes = []

    for movie in movies:
        ho_codes.append((movie['MasterMovieCode'], movie['Title']))

    if testing:
        print(f"Total HO codes discovered: {len(ho_codes)}")

    return list(set(ho_codes))

def load_discovered_movies():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_discovered_movies(discovered_movies):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(discovered_movies, file, indent=4)

def remove_old_movies(discovered_movies):
    two_months_ago = datetime.now() - timedelta(days=60)
    for ho_code in list(discovered_movies.keys()):
        if datetime.strptime(discovered_movies[ho_code]['last_seen'], '%Y-%m-%d') < two_months_ago:
            del discovered_movies[ho_code]

def fetch_movies(ho_codes, testing=False):
    movies = {}

    for ho_code, title in ho_codes:
        data = fetch_showtimes_by_ho_code(ho_code)
        if not data:
            continue
        dates_with_shows = data.get('datesWithShows', [])

        for date in dates_with_shows:
            data_by_date = fetch_showtimes_by_ho_code(ho_code, date)
            if not data_by_date:
                continue
            shows = data_by_date['shows']
            showtime_found = False

            for show in shows:
                films = show['Film']
                for film in films:
                    code = film['MasterMovieCode']
                    link = format_film_link(title, code)
                    performances = film['Performances']

                    if not performances:
                        if testing:
                            print(f"Skipping {title} ({code}): No performances found on {date}")
                        continue

                    earliest_showtime = None
                    for performance in performances:
                        showtime_str = performance['CalendarShowTime']
                        showtime = datetime.strptime(showtime_str, '%Y-%m-%dT%H:%M:%S')
                        if earliest_showtime is None or showtime < earliest_showtime:
                            earliest_showtime = showtime

                    if earliest_showtime:
                        formatted_showtime = format_showtime(earliest_showtime)
                        formatted_showdate = format_showdate(earliest_showtime)
                        if code not in movies:
                            movies[code] = (title, link, formatted_showtime, formatted_showdate)
                        else:
                            existing_showtime = datetime.strptime(movies[code][2], '%I:%M %p')
                            if earliest_showtime < existing_showtime:
                                movies[code] = (title, link, formatted_showtime, formatted_showdate)
                        showtime_found = True
                        if testing:
                            print(f"Processed {title} ({code}): Earliest Showtime {formatted_showtime} on {formatted_showdate}")
                        break

                if showtime_found:
                    break

            if showtime_found:
                break

    return dict(sorted(movies.items()))

async def send_new_movies_message(new_movies, testing=False):
    messages = []
    current_message = ""
    movie_count = 0

    for movie, details in new_movies.items():
        current_message += f"[{details[0].replace('[','(').replace(']',')')}]({details[1]}) - {details[2]} ({details[3]})\n" # Replace brackets from film titles to avoid breaking markdown.
        movie_count += 1

        if movie_count % 30 == 0:
            messages.append(current_message)
            current_message = ""

    if current_message:
        messages.append(current_message)

    if testing:
        for message in messages:
            print(message)
        print("Console output for testing completed.")
    else:
        bot = Bot(token=TOKEN)
        for message in messages:
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')
        print("Messages sent to Telegram channel successfully.")

async def main(testing=False):
    ho_codes = fetch_ho_codes(testing=testing)
    discovered_movies = load_discovered_movies()
    new_movies = {}
    new_ho_codes = []

    for code, title in ho_codes:
        if code in discovered_movies:
            discovered_movies[code]['last_seen'] = datetime.now().strftime('%Y-%m-%d')
        else:
            new_ho_codes.append((code, title))

    if testing:
        print(f"New HO codes discovered: {len(new_ho_codes)}")

    if new_ho_codes:
        current_movies = fetch_movies(new_ho_codes, testing=testing)
        for code, details in current_movies.items():
            new_movies[code] = details
            discovered_movies[code] = {'title': details[0], 'link': details[1], 'showtime': details[2], 'showdate': details[3], 'last_seen': datetime.now().strftime('%Y-%m-%d')}

    if new_movies:
        await send_new_movies_message(new_movies, testing)
        save_discovered_movies(discovered_movies)
    else:
        print("No new movies detected.")

    remove_old_movies(discovered_movies)
    save_discovered_movies(discovered_movies)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and announce new movie releases.')
    parser.add_argument('--testing', action='store_true', help='Run the script in testing mode with console output instead of Telegram messages.')

    args = parser.parse_args()

    asyncio.run(main(testing=args.testing))
