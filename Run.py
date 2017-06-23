import pandas as pd
import numpy as np
import datetime as dt
import time
from   bokeh.plotting import figure, show, output_file

# Local Python Class
from Account import Account

# Helpers ---------------------------------------------------------------

def PercentChange(d1, d2):
	return (d2-d1)/d1

def Profit(InitialCapital, Multiplier):
	return InitialCapital*(Multiplier+1.0)-InitialCapital

class Period():
	def __init__(self, Days):
		self.Days = Days

	def Day(self, i):
		if i > 1: raise ValueError("Error: Cannot look too far forward!")
		if i < -(len(self.Days)-2): raise ValueError("Error: Cannot look too far back!")		
		return self.Days[i]

# Helpers ---------------------------------------------------------------

class Run():
	def __init__(self, Data):
		self.Data = Data
		self.Data['date'] = pd.to_datetime(self.Data['date'])

	def Start(self, InitialCapital, Logic, Lookback=1, Start=False, End=False):
		# Initialize account
		self.Account = Account(InitialCapital)

		# Adjust custom timeframe
		if not(Start): Start = self.Data['date'].iloc[0]
		if not(End): End     = self.Data['date'].iloc[-1]
		self.Start, self.End = Start, End
		self.Timeframe = self.Data.loc[(self.Data['date'] >= Start) & (self.Data['date'] <= End)]

		# Enter backtest ---------------------------------------------
		
		for Index, Today in self.Timeframe.iterrows():
			Days = [self.Data.loc[Index]]
			for Day in range(Lookback):
				try: Days.insert(1, self.Data.loc[Index-Day-1])
				except KeyError: pass

			try: Days.insert(1, self.Data.loc[Index+1])
			except KeyError: pass
			
			# Update account variables
			self.Account.Date = Today['date']
			self.Account.Equity.append(self.Account.TotalValue(Today['open']))

			# Execute trading logic
			Logic(self.Account, Period(Days))

			# Cleanup empty positions
			self.Account.PurgePositions()
		  
		# ------------------------------------------------------------

	def Results(self):			
		print("-------------- Results ----------------\n")
		print("Period       : %s...%s" % (self.Start, self.End))
		
		BeginPrice = self.Timeframe.iloc[0]['open']
		FinalPrice = self.Timeframe.iloc[-1]['close']

		percentchange = PercentChange(BeginPrice, FinalPrice)
		print("Buy and Hold : %s%%" % round(percentchange*100, 2))
		print("Net Profit   : %s  " % round(Profit(self.Account.InitialCapital, percentchange), 2))
		
		percentchange = PercentChange(self.Account.InitialCapital, self.Account.TotalValue(FinalPrice))
		print("Strategy     : %s%%" % round(percentchange*100, 2))
		print("Net Profit   : %s  " % round(Profit(self.Account.InitialCapital, percentchange), 2))
		print("\n---------------------------------------")

	def AdvancedResults(self):
		print("-----------Advanced Results------------\n")
		
		Longs  = len([T for T in self.Account.OpenedTrades if T.Type == 'Long'])
		Sells  = len([T for T in self.Account.ClosedTrades if T.Type == 'Long'])
		Shorts = len([T for T in self.Account.OpenedTrades if T.Type == 'Short'])
		Covers = len([T for T in self.Account.ClosedTrades if T.Type == 'Short'])
		print("Longs        : %s" % Longs)
		print("Sells        : %s" % Sells)
		print("Shorts       : %s" % Shorts)
		print("Covers       : %s" % Covers)
		print("--------------------")
		print("Total Trades : %s" % (Longs+Sells+Shorts+Covers))

		LongPerformances  = [PercentChange(T.Entry, T.Exit) for T in self.Account.ClosedTrades if T.Type == 'Long']
		ShortPerformances = [-1*PercentChange(T.Entry, T.Exit) for T in self.Account.ClosedTrades if T.Type == 'Short']
		print("\nLong/Short Performance\n----------------------------")
		print("Long (Worst)     : %s%%"   % round(min(LongPerformances)*100,2))
		print("Long (Average)   : %s%%"   % round((sum(LongPerformances)/len(LongPerformances))*100,2))
		print("Long (Best)      : %s%%\n" % round(max(LongPerformances)*100,2))
		print("Short (Worst)    : %s%%"   % round(min(ShortPerformances)*100,2))
		print("Short (Average)  : %s%%"   % round((sum(ShortPerformances)/len(ShortPerformances))*100,2))
		print("Short (Best)     : %s%%"   % round(max(ShortPerformances)*100,2))

		Gains  = [T for T in LongPerformances+ShortPerformances if T > 0]
		Losses = [T for T in LongPerformances+ShortPerformances if T < 0]
		print("\nGains/Losses\n-----------------------------")
		print("Gain (Largest)   : %s%%" % round(max(Gains)*100, 2))
		print("Gain (Average)   : %s%%" % round((sum(Gains)/len(Gains))*100, 2))
		print("Gain (Smallest)  : %s%%" % round(min(Gains)*100, 2))
		print("Total Gains      : %s\n" % (len(Gains)))		
		print("Loss (Smallest)  : %s%%" % round(max(Losses)*100, 2))
		print("Loss (Average)   : %s%%" % round((sum(Losses)/len(Losses))*100, 2))
		print("Loss (Largest)   : %s%%" % round(min(Losses)*100, 2))
		print("Total Losses     : %s"   % (len(Losses)))		
		print("\n---------------------------------------")
	
	def Chart(self, ShowTrades=False):
		output_file("chart.html", title="Equity Curve")
		p = figure(x_axis_type="datetime", title="Equity Curve")
		p.legend.location = "top_left"
		p.grid.grid_line_alpha = 0.3
		p.xaxis.axis_label = 'Date'
		p.yaxis.axis_label = 'Equity'

		Shares = self.Account.InitialCapital/self.Timeframe.iloc[0]['open']
		BaseEquity = [Price*Shares for Price in self.Timeframe['open']]		
		p.line(self.Timeframe['date'], BaseEquity, color='#CAD8DE', legend='Buy and Hold')
		p.line(self.Timeframe['date'], self.Account.Equity, color='#49516F', legend='Strategy')

		if ShowTrades:
			
			for Trade in self.Account.OpenedTrades:
				x = time.mktime(Trade.Date.timetuple())*1000
				y = self.Account.Equity[np.where(self.Timeframe['date'] == Trade.Date.strftime("%Y-%m-%d"))[0][0]]
				if Trade.Type == 'Long': p.circle(x, y, size=6, color='green', alpha=0.5)
				elif Trade.Type == 'Short': p.circle(x, y, size=6, color='red', alpha=0.5)

			for Trade in self.Account.ClosedTrades:
				print(Trade.Type)
				x = time.mktime(Trade.Date.timetuple())*1000
				y = self.Account.Equity[np.where(self.Timeframe['date'] == Trade.Date.strftime("%Y-%m-%d"))[0][0]]
				if Trade.Type == 'Long': p.circle(x, y, size=6, color='blue', alpha=0.5)
				elif Trade.Type == 'Short': p.circle(x, y, size=6, color='orange', alpha=0.5)
		
		show(p)
