# Deploying to Streamlit Cloud

Follow these steps to deploy your **Gemini PDF Chat** app to the web for free using Streamlit Cloud.

## Prerequisites
- You have a GitHub account.
- This code is pushed to your GitHub repository: `chandran65/pdf-chat-app`

## Steps

1. **Go to Streamlit Cloud**
   - Click this link: [https://share.streamlit.io/deploy](https://share.streamlit.io/deploy)

2. **Connect GitHub**
   - If this is your first time, you will need to authorize Streamlit to access your GitHub repositories.

3. **Deploy the App**
   - Fill in the deployment form with the following details:
     - **Repository**: `chandran65/pdf-chat-app`
     - **Branch**: `main`
     - **Main file path**: `app.py`
   - Click **Deploy!** 🚀

4. **Configure Secrets (Optional but Recommended)**
   - Once the app is deployed (or while it's building), go to the app's **Settings** (three dots in top right) -> **Secrets**.
   - Add your Google API key so you don't have to paste it every time:
     ```toml
     GOOGLE_API_KEY = "your-google-api-key-here"
     ```
   - *Note: The app is designed to look for this secret if you don't provide one in the sidebar.*

## Troubleshooting
- If the build fails, check the logs on the right side of the Streamlit dashboard.
- Ensure `requirements.txt` is present (it is!).
