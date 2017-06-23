def Logic(Account, Period):

	try:
		Yesteray = Period.Day(-1)
		Today    = Period.Day(0)
		Tomorrow = Period.Day(1)
	
		# ----- Modifying Positions --------------------

		CurrentPrice = Today['open']

		for Position in Account.Positions:
			
			if Position.Type == 'Long':
				if CurrentPrice <= Position.StopLoss:
					Account.ClosePosition(Position, 1.0, CurrentPrice)

				elif CurrentPrice >= Position.ExitPrice and Yesteray['color'] != 'red':
					Account.ClosePosition(Position, 1.0, CurrentPrice)

			elif Position.Type == 'Short':
				if CurrentPrice >= Position.StopLoss:
					Account.ClosePosition(Position, 1.0, CurrentPrice)

				elif CurrentPrice <= Position.ExitPrice:
					Account.ClosePosition(Position, 1.0, CurrentPrice)

		# ----- Entering Positions ---------------------
		
		Reward       = 2
		EntryPrice   = Tomorrow['open']
		AccountValue = Account.TotalValue(Tomorrow['open'])
		AccountRisk  = AccountValue*0.01
		
		# ----- Enter Long -----------------------------

		if Today['color'] == 'blue':

			StopLoss     = Today['low'] if Today['low'] < Yesteray['low'] else Yesteray['low']
			StopLossRisk = (EntryPrice-StopLoss)/EntryPrice
			EntryCapital = AccountRisk/StopLossRisk
			ExitPrice    = Today['open']+(StopLossRisk*Today['open']*Reward)

			if EntryCapital >= 0:
				try: Account.EnterPosition('Long', EntryCapital, EntryPrice, ExitPrice, StopLoss)
				except ValueError: pass

		# ----- Enter Short ----------------------------

		if Today['color'] == 'orange':

			StopLoss     = Today['high'] if Today['high'] > Yesteray['high'] else Yesteray['high']
			StopLossRisk = (StopLoss-EntryPrice)/EntryPrice
			EntryCapital = AccountRisk/StopLossRisk
			ExitPrice    = Today['open']-(StopLossRisk*Today['open']*Reward)

			if EntryCapital >= 0:
				try: Account.EnterPosition('Short', EntryCapital, EntryPrice, ExitPrice, StopLoss)
				except ValueError: pass

	except ValueError: pass

import pandas as pd
from Run import Run

data = pd.read_csv('TSLA.csv')
r = Run(data)
r.Start(1000, Logic, Lookback=1, Start='10/13/2013', End='1/10/2014')
r.Results()
r.AdvancedResults()
r.Chart(ShowTrades=True)
#for trade in r.Account.OpenedTrades:
#	print(trade)
#	print()

#for trade in r.Account.ClosedTrades:
#	print(trade)
#	print()
