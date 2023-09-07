To start using this application you will need to setup accounts and get api tokens from openai and huggingface: 

https://platform.openai.com/account/api-keys

https://huggingface.co/settings/tokens

From the root of the project, create a .env file with the following:

OPENAI_API_KEY={open_api_key}
HUGGINGFACEHUB_API_TOKEN={huggingface_api_key}

From the root of the project, run pip install -r requirements.txt

From the root of the project run: streamlit run app.py

A browser will pop up, before you start a conversation with the chat bot, choose files to feed into it and click process.  Once the file processing completes, you can then ask questions about the document.  If your documents include code, you may be able to ask the bot to provide examples using the code you've provided.



