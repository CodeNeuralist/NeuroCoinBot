# Mini-Bank Telegram Bot

This Telegram bot allows users to perform various banking operations, such as checking balances, transferring NeuroCoin (a fictional currency), purchasing NeuroCoin, and more.

## Features

- **Balance Checking**: Users can check their NeuroCoin balance by sending the `/balance` command.
- **Transfers**: Users can transfer NeuroCoin to other users by using the `/transfer [user_id] [amount]` command.
- **View All Users**: Admins can view the data of all users by using the `/all_users` command.
- **Purchasing NeuroCoin**: Users can purchase NeuroCoin by using the `/getCoin [amount]` command.
- **Payment Confirmation**: Users receive a notification when a transfer or purchase is successful.

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/your-username/mini-bank-telegram-bot.git
    ```

2. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Obtain API tokens:

    - Telegram Bot API token (`TOKEN`)
    - YooMoney API token (`YOOMONEY_TOKEN`)

4. Replace the placeholder tokens in the `config.py` file with your actual tokens.

5. Run the bot:

    ```
    python bot.py
    ```

## Usage

1. Start the bot by sending the `/start` command.
2. Perform banking operations using the available commands.
3. Follow the prompts and instructions provided by the bot.

## Contributing

Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
