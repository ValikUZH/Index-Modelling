import datetime as dt
import pandas as pd
import numpy as np

class IndexModel:
    def __init__(self) -> None:
        self.data = pd.read_csv('data_sources/stock_prices.csv')
        

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
        self.data.Date = pd.to_datetime(self.data.Date,format='%d/%m/%Y')
        cond = self.data['Date'].dt.month != self.data['Date'].shift(1).dt.month
        returns = self.data.iloc[:,1:].pct_change()
        self.data['Best_three'] = 0
        self.data.Best_three[cond] = self.data.iloc[:,1:].apply(lambda row: row.nlargest(3).index.tolist(),axis=1).shift(1)[cond]
        self.data.Best_three = self.data.Best_three.replace(to_replace=0, method='ffill').shift(1)
        self.data.Best_three = self.data.Best_three.fillna(method='bfill')
        self.data.iloc[:,1:-1] = returns.iloc[:,:]
        
        self.Index = pd.concat([self.data.Date.to_frame(),
                           pd.DataFrame(np.zeros((self.data.shape[0], 3)),
                                        columns  = ['First_best','Second_best','Third_best'])],
                          axis=1)
        for i in range(len(self.data)):
            self.Index.iloc[i,1:] = self.data.loc[i][self.data.iloc[i,-1]]
        self.Index = self.Index[self.Index.Date>=self.start_date][self.Index.Date<=self.end_date]        
        self.Index['Index_value'] = 0.5*self.Index.First_best + \
            0.25*self.Index.Second_best + 0.25*self.Index.Third_best+1
        self.Index.iloc[0,-1] = 100
        self.Index.Index_value = round(self.Index.Index_value.cumprod(), 2)
        self.Index = self.Index[['Date', 'Index_value']]
        

    def export_values(self, file_name: str) -> None:
        self.Index.to_csv(file_name)