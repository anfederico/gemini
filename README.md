### Short documentation on basic architecture

#### Account Class
The account class represents (as you probably guessed) an account on an arbitrary exchange. The account starts with capital and can buy/sell the asset in what is simulated as open positions.

#### Run Class
The run class is the meat and bones of the backtester. It starts off with a fresh account class, a dataset (preprocessed with your signals), and some logic as to how the account class should behave. You'll set a lookback period and the run class will iterate through the dataset and apply the custom logic on the lookback period. At the end of the dataset, you can graph the equity curve along with indicators of where positions were opened and closed.
