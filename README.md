# <p align="center"> S.A.B - an epical Slack Bot  </p>

<p align="center">
 <a><img height=300px src="./assets/SAB.png"></a>
  <br>
  <a style="font-size: 40px; color:red;"> <strong> I'm S.A.B, let me help you </strong> </a>
</p>


<p align="center">
<a href="https://www.codefactor.io/repository/github/lannguyen0910/sab/overview/master"><img src="https://www.codefactor.io/repository/github/lannguyen0910/sab/badge/master?s=9716a4eb0076053fa36e0d967bba5161b85b8fb5" alt="CodeFactor" /></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Python" /></a>
<a href="./LICENSE"><img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="MIT" /></a>
<a href="https://slack.com/"><img src="https://badgen.net/badge/icon/slack?icon=slack&label" alt="Slack" /></a>
 
 </p>
<!-- 
# **Download and create API keys**
[ngrok](https://ngrok.com/download): route public IP addresses to the slackbot's local webserver <br/>
[api-slack](https://api.slack.com/apps): create an app in slack api to set up the bot <br/>
[yelp](https://www.yelp.com/login?return_url=%2Fdevelopers%2Fv3%2Fmanage_app): set up search engine **(Make sure to use VPN (America region,..) because they don't allow users with Asia or Africa IP addresses to sign up for an account)** -->

<!-- # **Setup**
**Create conda env for the project**
```
conda create --name <project-name>
```
**Install all the dependencies by using the command below**
```
pip install -r requirements.txt
``` -->

<details open>
 <summary><strong>Status</strong></summary>
 <strong><i>[03/11/2021]</i></strong> S.A.B is still in development stage and has some drawbacks. Documentation is on the way. If you want to integrate to your own slack channel, contact me for guidance. 
</details>

# **Set up**
```
pip install -r requirements.txt
```
- Need to set up some API keys, oauth ...
- Contact me for more info: [mail](mailto:18120051@student.hcmus.edu.vn)

# **Run S.A.B**
```
python main.py
```
- Run this to clear cache (__pycache__) when finish running
```
run.bat
```

- Testing:
```
python tests/news/<test_module>.py
```


# **Demo**
<h3>Paper summarization</h3>

![arxiv](./assets/arxiv_1.PNG)

<h3>Location search</h3>

![location_search](./assets/location_search.PNG)

<h3>Stackoverflow search</h3>

![stackoverflow](./assets/stackoverflow.PNG)

<h3>News search</h3>

![news](./assets/news.PNG)

# **References**
- **Adapted from _Kaylode_: [Discord Bot](https://github.com/kaylode/KAI/)**
- **[Starter Tutorial](https://www.youtube.com/watch?v=KJ5bFv-IRFM&list=PLzMcBGfZo4-kqyzTzJWCV6lyK-ZMYECDc)**
- **[SlackOverflow](https://github.com/karan/slack-overflow)**
