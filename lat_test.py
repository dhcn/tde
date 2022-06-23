# coding:utf-8

'''
Created by denghui on 2020/7/7.

@author: Hayden

'''

# loading the class data from the package pandas_datareader
import numpy as np
from pandas_datareader import data
import pandas as pd
import matplotlib.pyplot as plt

def test_chapter1():
    import numpy as np
    from pandas_datareader import data
    import pandas as pd
    import matplotlib.pyplot as plt
    #pd.set_printoptions('max_colwidth', 1000)
    pd.set_option('display.width', 1000)

    # First day
    start_date = '2019-01-01'
    # Last day
    end_date = '2019-01-30'
    # Call the function DataReader from the class data
    goog_data = data.DataReader('GOOG', 'yahoo', start_date, end_date)
    #print(goog_data)
    goog_data_signal = pd.DataFrame(index=goog_data.index)
    goog_data_signal['price'] = goog_data['Adj Close']
    goog_data_signal['daily_difference'] = goog_data_signal['price'].diff()
    goog_data_signal['signal'] = 0.0
    goog_data_signal['signal'] = np.where(goog_data_signal['daily_difference']>0, 1.0, 0.0)

    goog_data_signal['positions'] = goog_data_signal['signal'] . diff()

    #print(goog_data_signal.head())
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    goog_data_signal['price'].plot(ax=ax1, color='r', lw=2. )
    ax1.plot(goog_data_signal.loc[goog_data_signal.positions ==1.0].index,
             goog_data_signal.price[goog_data_signal.positions == 1.0],'^', markersize=5, color='m')

    ax1.plot(goog_data_signal.loc[goog_data_signal.positions==-1.0].index,
              goog_data_signal.price[goog_data_signal.positions == -1.0] ,
              'v', markersize=5, color='k')
    plt.show()

    # backtesting
    initial_capital = float(1000.0)

    positions = pd.DataFrame(index=goog_data_signal. index) . fillna(0.0)
    portfolio = pd.DataFrame(index=goog_data_signal. index) . fillna(0.0)

    positions['GOOG'] = goog_data_signal['signal']
    portfolio['positions'] = (positions. multiply(goog_data_signal['price'] ,axis=0) )

    portfolio['cash'] = initial_capital -(positions. diff().multiply(goog_data_signal['price'] , axis=0) ).cumsum()
    portfolio['total'] = portfolio['positions'] + portfolio['cash']




def test_chapter2():
    import pandas as pd
    import numpy as np
    from pandas_datareader import data
    import matplotlib.pyplot as plt

    start_date = '2014-01-01'
    end_date = '2018-01-01'
    SRC_DATA_FILENAME = 'goog_data.pkl'
    try:
        goog_data = pd.read_pickle(SRC_DATA_FILENAME)
        print('File data found. . . reading GOOG data')
    except FileNotFoundError:
        print('File not found. . . downloading the GOOG data')
        goog_data = data.DataReader('GOOG', 'yahoo', start_date, end_date)
        goog_data.to_pickle(SRC_DATA_FILENAME)
    goog_data_signal = pd.DataFrame(index=goog_data.index)
    goog_data_signal['price'] = goog_data['Adj Close']

    def trading_support_resistance(data, bin_width=20):
        data['sup_tolerance'] = pd.Series(np.zeros(len(data)))
        data['res_tolerance'] = pd.Series(np.zeros(len(data)))
        data['sup_count'] = pd.Series(np.zeros(len(data)))
        data['res_count'] = pd.Series(np.zeros(len(data)))
        data['sup'] = pd.Series(np.zeros(len(data)))
        data['res'] = pd.Series(np.zeros(len(data)))
        data['positions'] = pd.Series(np.zeros(len(data)))
        data['signal'] = pd.Series(np.zeros(len(data)))
        in_support = 0
        in_resistance = 0
        for x in range((bin_width - 1) + bin_width, len(data)):
            data_section = data[x - bin_width: x + 1]
            support_level = min(data_section['price'])
            resistance_level = max(data_section['price'])
            range_level = resistance_level - support_level
            data['res'][x] = resistance_level
            data['sup'][x] = support_level
            data['sup_tolerance'][x] = support_level + 0.2 * range_level
            data['res_tolerance'][x] = resistance_level - 0.2 * range_level
            if data['price'][x] >= data['res_tolerance'][x] and data['price'][x] <= data['res'][x]:
                in_resistance += 1
                data['res_count'][x] = in_resistance
            elif data['price'][x] <= data['sup_tolerance'][x] and data['price'][x] >= data['sup'][x]:
                in_support += 1
                data['sup_count'][x] = in_support
            else:
                in_support = 0
                in_resistance = 0
            if in_resistance > 2:
                data['signal'][x] = 1
            elif in_support > 2:
                data['signal'][x] = 0
            else:
                data['signal'][x] = data['signal'][x - 1]
        data['positions'] = data['signal'].diff()
    trading_support_resistance(goog_data_signal)
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    goog_data_signal['sup'].plot(ax=ax1, color='g', lw=2.)
    goog_data_signal['res'].plot(ax=ax1, color='b', lw=2.)
    goog_data_signal['price'].plot(ax=ax1, color='r', lw=2.)
    ax1.plot(goog_data_signal.loc[goog_data_signal.positions == 1.0].index,
       goog_data_signal.price[goog_data_signal.positions == 1.0],
    '^', markersize = 7, color = 'k', label = 'buy')
    ax1.plot(goog_data_signal.loc[goog_data_signal.positions == -1.0].index,
       goog_data_signal.price[goog_data_signal.positions == -1.0],
    'v', markersize = 7, color = 'k', label = 'sell')
    plt.legend()
    plt.show()

def test_seasonality():
    import pandas as pd
    import matplotlib.pyplot as plt
    from pandas_datareader import data
    start_date = '2001-01-01'
    end_date = '2018-01-01'
    SRC_DATA_FILENAME = 'goog_data_large. pkl'
    try:
        goog_data = pd.read_pickle(SRC_DATA_FILENAME)
        print('File data found. . . reading GOOG data')
    except FileNotFoundError:
        print('File not found. . . downloading the GOOG data')
        goog_data = data.DataReader('GOOG', 'yahoo', start_date,
                                end_date)
        goog_data.to_pickle(SRC_DATA_FILENAME)
    goog_monthly_return = goog_data['Adj Close'].pct_change().groupby(
        [goog_data['Adj Close'].index.year,
         goog_data['Adj Close'].index.month]).mean()
    goog_montly_return_list = []
    for i in range(len(goog_monthly_return)):
        goog_montly_return_list.append \
            ({'month': goog_monthly_return.index[i][1],
              'monthly_return': goog_monthly_return[i]})
    goog_montly_return_list = pd.DataFrame(goog_montly_return_list,
                                           columns=('month', 'monthly_return'))
    goog_montly_return_list.boxplot(column='monthly_return',
                                    by='month')
    ax = plt.gca()
    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', \
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_xticklabels(labels)
    ax.set_ylabel('GOOG return')
    plt.tick_params(axis='both', which='major', labelsize=7)
    plt.title("GOOG Monthly return 2001-2018")
    plt.suptitle("")
    plt.show()



def load_financial_data(start_date, end_date, output_file) :
    import pandas as pd
    from pandas_datareader import data
    try:
        df = pd. read_pickle(output_file)
        print('File data found. . . reading GOOG data')
    except FileNotFoundError:
        print('File not found. . . downloading the GOOG data')
        df = data.DataReader('GOOG', 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df

def create_classification_trading_condition(df) :
    df['Open-Close'] = df. Open - df. Close
    df['High-Low'] = df. High - df. Low
    df = df.dropna()
    X = df[['Open-Close', 'High-Low'] ]
    Y = np.where(df['Close'].shift(-1) > df['Close'] , 1, -1)
    return (X, Y)

def create_regression_trading_condition(df) :
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    X = df[['Open-Close', 'High-Low'] ]
    Y = df['Close'].shift(-1) - df['Close']
    df['Target']=Y
    return (X, Y)


def create_train_split_group(X, Y, split_ratio=0.8):
    from sklearn.model_selection import train_test_split
    return train_test_split(X, Y, shuffle=False,train_size=split_ratio)



def test_chapter3():
    goog_data = load_financial_data(
        start_date='2001-01-01',
        end_date='2018-01-01',
        output_file='goog_data_large.pkl')
    X, Y = create_regression_trading_condition(goog_data)
    pd.plotting.scatter_matrix(goog_data[['Open-Close', 'High-Low']], grid=True, diagonal='kde')
    X_train, X_test, Y_train, Y_test = create_train_split_group(X, Y, split_ratio = 0.8)
    from sklearn import linear_model
    ols = linear_model.LinearRegression()
    ols.fit(X_train, Y_train)
    print(' Coefficients: \n', ols.coef_)
    from sklearn.metrics import mean_squared_error, r2_score
    print("Mean squared error: %.2f" % mean_squared_error(Y_train, ols. predict(X_train)))
    print('Variance score: %.2f' % r2_score(Y_train,ols.predict(X_train)))
    print("Mean squared error: %.2f"% mean_squared_error(Y_test, ols.predict(X_test)))
    print('Variance score: %.2f' % r2_score(Y_test,ols.predict(X_test)))
    goog_data[' Predicted_Signal'] = ols.predict(X)
    goog_data[' GOOG_Returns'] = np.log(goog_data[' Close'] /
                                        goog_data[' Close'].shift(1))

    def calculate_return(df, split_value, symbol):
        cum_goog_return = df[split_value:][' %s_Returns' %
                                           symbol].cumsum() * 100

        df[' Strategy_Returns'] = df[' %s_Returns' % symbol] *df[' Predicted_Signal'].shift(1)
        return cum_goog_return

    def calculate_strategy_return(df, split_value, symbol):
        cum_strategy_return =df[split_value:][' Strategy_Returns'].cumsum() * 100
        return cum_strategy_return
    cum_goog_return = calculate_return(goog_data,
                                       split_value=len(X_train), symbol=' GOOG')
    cum_strategy_return = calculate_strategy_return(goog_data,
                                                    split_value=len(X_train), symbol=' GOOG')

    def plot_chart(cum_symbol_return, cum_strategy_return, symbol):
        plt.figure(figsize=(10, 5))

    # plt.plot(cum_symbol_return, label=' %s Returns' % symbol)

def test_predict():
    pass



#------------------
if __name__ == '__main__':
    test_chapter3()


















