from bs4 import BeautifulSoup
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json
import os
import argparse
from datetime import datetime, timedelta
import asyncio

# Telegram bot token
TOKEN = 'put_token_here'
# Telegram channel username or ID
CHANNEL_ID = 'put_channel_id_here'

# JSON file path
JSON_FILE_PATH = 'discovered_movies.json'

# URL of the webpage
url = 'https://www.regmovies.com/movies'

# Set up Selenium with Firefox
options = Options()
options.add_argument('--headless')
driver_path = '/usr/local/bin/geckodriver'  # Update this path to where you have geckodriver
service = FirefoxService(executable_path=driver_path)
driver = webdriver.Firefox(service=service, options=options)


def fetch_movies():
    # Fetch the HTML content from the URL
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10)

    # Parse the HTML content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find all div tags with the specified class
    category_divs = soup.find_all('div', class_='css-csvbwb e1t9pql65')

    # Dictionary to hold categories and their respective movies
    categories = {}

    for div in category_divs:
        # Get the category title from the first h3 tag
        category_title = div.find('h3').get_text(strip=True)

        # Find all movies in the current category
        slide_divs = div.find_all('div', class_='embla__slide')
        movies = []
        for slide_div in slide_divs:
            figcaption = slide_div.find('figcaption')
            a_tag = slide_div.find('a', href=True)

            if figcaption and a_tag:
                movie_title = figcaption.get_text(strip=True).replace('[', '(').replace(']', ')')  # Make sure titles with brackets do not mess up the formatting.
                movie_link = 'https://regmovies.com' + a_tag['href']
                movies.append((movie_title, movie_link))

        # Add the category and its movies to the dictionary
        categories[category_title] = movies

    return categories


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
    for category in list(discovered_movies.keys()):
        discovered_movies[category] = [movie for movie in discovered_movies[category] if
                                       datetime.strptime(movie['last_seen'], '%Y-%m-%d') >= two_months_ago]
        if not discovered_movies[category]:
            del discovered_movies[category]


async def send_new_movies_message(new_movies, testing=False):
    messages = []
    current_message = ""
    movie_count = 0

    for category, movies in new_movies.items():
        if movie_count + len(movies) > 100:
            messages.append(current_message)
            current_message = ""
            movie_count = 0

        current_message += f"\n*{category}*\n"
        for movie, link in movies:
            current_message += f"[{movie}]({link})\n"
            movie_count += 1

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
    # Fetch the current movies from the website
    current_movies = fetch_movies()

    # Load previously discovered movies from the JSON file
    discovered_movies = load_discovered_movies()

    # Dictionary to hold new movies to announce
    new_movies = {}

    # Check for new movies and new categories
    for category, movies in current_movies.items():
        if category not in discovered_movies:
            # This is a new category, mark it as [NEW!] and add all movies
            new_movies[category + " (NEW!)"] = movies
            discovered_movies[category] = [
                {'title': movie[0], 'link': movie[1], 'last_seen': datetime.now().strftime('%Y-%m-%d')} for movie in
                movies]
        else:
            # This is an existing category, check for new movies
            new_category_movies = []
            for movie in movies:
                found = False
                for discovered_movie in discovered_movies[category]:
                    if discovered_movie['title'] == movie[0] and discovered_movie['link'] == movie[1]:
                        discovered_movie['last_seen'] = datetime.now().strftime('%Y-%m-%d')
                        found = True
                        break
                if not found:
                    new_category_movies.append(movie)
                    discovered_movies[category].append(
                        {'title': movie[0], 'link': movie[1], 'last_seen': datetime.now().strftime('%Y-%m-%d')})
            if new_category_movies:
                new_movies[category] = new_category_movies

    # Send message if there are new movies to announce
    if new_movies:
        await send_new_movies_message(new_movies, testing)
        # Save the updated discovered movies to the JSON file
        save_discovered_movies(discovered_movies)
    else:
        print("No new movies detected.")

    # Remove old movies
    remove_old_movies(discovered_movies)
    save_discovered_movies(discovered_movies)


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Fetch and announce new movie releases.')
    parser.add_argument('--testing', action='store_true',
                        help='Run the script in testing mode with console output instead of Telegram messages.')

    args = parser.parse_args()

    # Run the main function with the testing argument
    asyncio.run(main(testing=args.testing))
