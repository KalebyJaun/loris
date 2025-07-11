# Loris API

API developed with FastAPI to receive WhatsApp webhooks, process images of financial transaction receipts, and return the extracted information.

## Features
- Receives WhatsApp messages via webhook
- Processes sent images
- Extracts and returns information from financial receipts

## Requirements
- Python 3.10+
- Facebook Developers account with a configured WhatsApp Business API app
- WhatsApp app credentials (Access Token, App ID, App Secret, Phone Number ID, Verify Token)
- OpenAI API key
- Ngrok (or another service to expose the FastAPI endpoint to the internet)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/loris.git
cd loris/app
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. **Install the dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file in the `app` folder with the following format (example):

```
META_ACCESS_TOKEN=your_access_token
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_API_VERSION=v23.0
META_PHONE_NUMBER_ID=your_phone_number_id
META_VERIFY_TOKEN=your_verify_token

OLLAMA_HOST=https://datamasters.ai/ollama/
OLLAMA_VISION_MODEL=llama3.2-vision

AI_MODEL=gpt-4o
LOCAL_IMAGE_PATH=/path/to/save/images
OPEN_AI_API_KEY=your_openai_api_key
```

> **Important:**
> - WhatsApp credentials must be obtained from the [Facebook Developers Portal](https://developers.facebook.com/).
> - The OpenAI key can be obtained at [https://platform.openai.com/](https://platform.openai.com/).

5. **Run the API:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Expose the endpoint using ngrok:**

```bash
ngrok http 8000 --domain $NGROK_DOMAIN
```

Copy the HTTPS address generated by ngrok and configure your WhatsApp app webhook in Facebook Developers to point to `https://YOUR_NGROK_URL/webhook`.

## Usage
- Send a financial receipt image to the configured WhatsApp number.
- The API will process the image and return the extracted information via WhatsApp message.

## Notes
- Make sure the endpoint is publicly accessible so WhatsApp can send webhooks.
- Check the Facebook Developers documentation for details on app and webhook configuration.

---

Developed by Kaleby Jaun.

