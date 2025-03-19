# CarePal

A chatbot that provides personalized emotional support for patients, built on real experiences and trusted medical advice, powered by InterSystems IRIS Vector Search and Google Gemini.

## Prototype Usage

Requires Python >=3.10 <=3.12
1. Set up InterSystems IRIS using [the instructions here](https://github.com/intersystems-community/hackathon-2024/tree/main "intersystems-community/hackathon-2024/tree/main").
2. Install necessary dependencies.
3. Fill in your [Google Gemini API key](https://aistudio.google.com/apikey "Get API key | Google AI Studio") in [`Config.py`](./utils/Config.py).
4. After the containerized IRIS instance is up and running, run `init.py` to populate the IRIS database.
5. To use the chatbot, run `main.py`. This is an early prototype running on Gradio, so you must restart `main.py` in order to select a different avatar.

---
###### From CarePal Team comprising Clarice, Pierre, Xinnan, Rui Hong, Kwan Tze
