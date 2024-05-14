
# KYC Watermark Bot

KYC Watermark Bot is a Telegram bot designed to add a watermark to KYC (Know Your Customer) images. 


## How to Use
**1. Clone the Repository:** Clone this repository to your local machine.

``git clone https://github.com/luqmanhy/KYC-Watermark-Bot
cd KYC-Watermark-Bot``

**2. Create Your Bot:** Create a bot on Telegram and get the API token. Follow this guide to create your bot.

**3. Configure Your Environment:** Create a .env file in the project directory and add your bot API token and default watermark text:

``TELEGRAM_API=YOUR_TELEGRAM_BOT_API_TOKEN``


**4. Set the Webhook:** Replace YOUR_WEBHOOK_URL with your actual URL where the bot is hosted. This step is necessary for Telegram to communicate with your bot.


``curl -F "url=https://YOUR_WEBHOOK_URL" https://api.telegram.org/botYOUR_TELEGRAM_BOT_API_TOKEN/setWebhook``

**5. Run the Bot:** Start the bot with the following command:

``python bot.py``

**6. Using the Bot:**
- Send a photo to the bot and add caption **/wm your_text** to the photo to add a custom watermark to the photo.
- The original photos will automatically deleted after processing

## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.

