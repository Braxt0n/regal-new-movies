# 🎬 Regal New Movies Announcer 🎬

**Regal New Movies Announcer** is a Python-based script designed to fetch and announce new movie releases from the Regal Movies website to a Telegram channel. The tool utilizes Selenium for web scraping and integrates with the Telegram API for sending messages.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [To-Do](#to-do)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)
- [Contact](#contact)

## Introduction

Regal New Movies Announcer automates the process of monitoring new movie releases on the Regal Movies website and announcing them to a specified Telegram channel. This script is particularly useful for movie enthusiasts and communities who want to stay updated with the latest movie releases.

## Demo

[Check out the bot's channel on Telegram!](https://t.me/newregalmovies)

![screenshot of the telegram bot in action](https://mokuroh.club/images/regal-bot-demo.png)

## Features

- **Duplicate Detection**: Avoid announcing movies that have already been discovered.
- **Automatic Cleanup**: Remove movies that haven't been seen for over two months to avoid bloat.
- **Testing Mode**: Output messages to the console for testing purposes.

## Installation

To install Regal New Movies Announcer, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/Braxt0n/regal-new-movies
    ```
2. Navigate to the project directory:
    ```sh
    cd regal-new-movies
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Ensure you have the required dependencies installed.
2. Set up your Telegram bot token and channel ID in the script:
    ```python
    # Telegram bot token
    TOKEN = 'put_token_here'
    # Telegram channel username or ID
    CHANNEL_ID = 'put_channel_id_here'
    ```
3. Run the script:
    ```sh
    python regal_new_movies.py
    ```
4. Throw it in a cron job to have it run on a regular interval.

### Testing Mode

To run the script in testing mode (which outputs messages to the console instead of sending them to Telegram), use the `--testing` flag:
```sh
python regal_new_movies.py --testing
```
## To-Do

- **Add More Movie Sources**: Extend the script to fetch movie releases from additional websites.
- **Enhance Error Handling**: Improve error handling and logging.
- **Add Custom Notification Options**: Allow users to customize notification messages.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature-branch
    ```
3. Make your changes.
4. Commit your changes:
    ```sh
    git commit -am 'Add new feature'
    ```
5. Push to the branch:
    ```sh
    git push origin feature-branch
    ```
6. Create a new Pull Request.

Please ensure all pull requests adhere to the existing code style and include appropriate tests.

## Credits

This project utilizes the following tools and libraries:

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium](https://www.selenium.dev/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LISCENSE) file for more details.

## Contact

For any questions or feedback, feel free to open an issue or [email me](https://mokuroh.club/about/).