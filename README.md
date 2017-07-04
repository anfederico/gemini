<p align="center"><img src="https://raw.githubusercontent.com/Crypto-AI/Gemini/master/media/gemini-logo.png" width="100px"><p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v2.7%20%2F%20v3.6-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
[![GitHub Issues](https://img.shields.io/github/issues/Crypto-AI/Gemini.svg)](https://github.com/anfederico/flaskex/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<br><br>

#### Account Class
The account class represents (as you probably guessed) an account on an arbitrary exchange. The account starts with capital and can buy/sell the asset in what is simulated as open positions.

#### Run Class
The run class is the meat and bones of the backtester. It starts off with a fresh account class, a dataset (preprocessed with your signals), and some logic as to how the account class should behave. You'll set a lookback period and the run class will iterate through the dataset and apply the custom logic on the lookback period. At the end of the dataset, you can graph the equity curve along with indicators of where positions were opened and closed.
