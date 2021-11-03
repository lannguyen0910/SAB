# **S.A.B**
SlackBot can communicate with users. It can send messages, detect bad words and help you search things within Slack using Yelp - API Search

<!-- 
# **Download and create API keys**
[ngrok](https://ngrok.com/download): route public IP addresses to the slackbot's local webserver <br/>
[api-slack](https://api.slack.com/apps): create an app in slack api to set up the bot <br/>
[yelp](https://www.yelp.com/login?return_url=%2Fdevelopers%2Fv3%2Fmanage_app): set up search engine **(Make sure to use VPN (America region,..) because they don't allow users with Asia or Africa IP addresses to sign up for an account)** -->

# **Setup**
**Create conda env for the project**
```
conda create --name <project-name>
```
**Install all the dependencies by using the command below**
```
pip install -r requirements.txt
```


# **Run S.A.B**
```
python main.py
```
Or this to clear cache (__pycache__) when finish running
```
run.bat
```

- Testing:
```
python tests/news/<test_module>.py
```


# **Results**
**Count messages and detect bad words**
![gif1](results/gif1.gif)

**Welcome message and perform searching based on given term and location**<br/>
**Ex: search food, München** <br/>
**Valid locations: [locations](https://www.yelp.com/locations)**
![gif2](results/gif2.gif)


# **References**
- Adapted from *Kaylode* on his ```Discord Bot```: https://github.com/kaylode/KAI/
- https://github.com/hueds/slack-gpt2
- https://github.com/karan/slack-overflow