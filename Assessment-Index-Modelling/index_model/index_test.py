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
        self.data['Best_three'] = 0
        self.data.Best_three[cond] = self.data.iloc[:,1:].apply(lambda row: row.nlargest(3).index.tolist(),axis=1).shift(1)[cond]
        self.data['Best_three_untrue'] = self.data.Best_three.replace(to_replace=0, method='ffill')
        self.data.Best_three = self.data.Best_three.replace(to_replace=0, method='ffill').shift(1)
        self.data = self.data.fillna(method='bfill')
        
        self.Index = pd.concat([self.data.Date.to_frame(),
                           pd.DataFrame(np.zeros((self.data.shape[0], 6)),
                                        columns  = ['First_best','Second_best','Third_best',
                                                    'First_best1','Second_best1','Third_best1'])],
                          axis=1)
        for i in range(len(self.data)):
            self.Index.iloc[i,1:4] = self.data.loc[i][self.data.iloc[i,-2]]
        for i in range(len(self.data)):
           self. Index.iloc[i,4:] = self.data.loc[i][self.data.iloc[i,-1]]
        self.Index = self.Index[self.Index.Date>=self.start_date][self.Index.Date<=self.end_date]        
        self.Index['Value_start_unadj'] = 0.5*self.Index.First_best + \
            0.25*self.Index.Second_best + 0.25*self.Index.Third_best
        self.Index['Value_end_unadj'] = 0.5*self.Index.First_best1 + \
            0.25*self.Index.Second_best1 + 0.25*self.Index.Third_best1
        self.Index = self.Index[['Date', 'Value_start_unadj', 'Value_end_unadj']]
        self.Index['cond'] = self.Index['Date'].dt.month != self.Index['Date'].shift(1).dt.month
        self.Index['cond'] = self.Index['cond'].shift(1)
        self.Index['adj']=0
        self.Index['Value'] = 0
        self.Index.iloc[0,-1]=100
        for i in range(len(self.Index)):
            if self.Index.iloc[i,3] == True:
                self.Index.iloc[i,-2] = self.Index.iloc[i-1,-1]/self.Index.iloc[i-1,2]
                self.Index.iloc[i,-1] = self.Index.iloc[i,-2]*self.Index.iloc[i,1]
            if self.Index.iloc[i,3] == False:
                self.Index.iloc[i,-2] = self.Index.iloc[i-1,-2]
                self.Index.iloc[i,-1] = self.Index.iloc[i,-2]*self.Index.iloc[i,1]
        self.Index = round(self.Index[['Date', 'Value']],2)
        

    def export_values(self, file_name: str) -> None:
        self.Index.to_csv(file_name)