# **S.A.B**
SlackBot can communicate with users. It can send messages, detect bad words and help you search things within Slack using Yelp - API Search

# **Download and create API keys**
[ngrok](https://ngrok.com/download): route public IP addresses to the slackbot's local webserver <br/>
[api-slack](https://api.slack.com/apps): create an app in slack api to set up the bot <br/>
[yelp](https://www.yelp.com/login?return_url=%2Fdevelopers%2Fv3%2Fmanage_app): set up search engine **(Make sure to use VPN (America region,..) because they don't allow users with Asia or Africa IP addresses to sign up for an account)**

# **Setup**
**Create virtualenv for the project**
```
pipenv --python 3
```
**Install all the dependencies by using the command below.**
```
pipenv install -r requirements.txt
```

**Create an environment file (.env) with 5 variables:**
- **SIGNING_SECRET:** register in the your slack app for event handling.
- **SLACK_TOKEN:** allow to work directly on behalf of users, based on the OAuth scopes.
- **YELP_API_KEY:** authenticate requests.
- **DEFAULT_LIMIT:** Maximum number of places that BotSearch can recommend.
- **DEFAULT_LOCATION:** BotSearch can recommend places around this location.

# **Run**
Test an individual module. For example:
```
pipenv run python -m pytest tests/news/[test_module].py
```

Activate bot:
```
pipenv run python main.py
```

# **Results**
**Count messages and detect bad words**
![gif1](results/gif1.gif)

**Welcome message and perform searching based on given term and location**<br/>
**Ex: search food, München** <br/>
**Valid locations: [locations](https://www.yelp.com/locations)**
![gif2](results/gif2.gif)

# **Cautions**
I have to set a new **request URL** to **SlackAPI** in every 2 hours because the free version of **ngrok**.<br/><br/>
It's really a pain to make a search request to Yelp. I received the **500 internal server error** until i use the **API key** in **developer beta mode**. Sometimes it doesn't even work with the search request too.<br/><br/>
The settings for this project are larger than the project itself. Having to deal a lot with the **environment variables** and **API documentations** (Slack API, Yelp Fusion API).


# **References**
- Adapted from *Kaylode* on his ```Discord Bot```: https://github.com/kaylode/KAI/