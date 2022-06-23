# coding:utf-8

'''
Created by denghui on 2020/7/23.

@author: Hayden

'''
#%%
import matplotlib as mpl
mpl.rcParams['font.sans-serif']=['SimHei']

import matplotlib.pyplot as plt

x = ['c', 'a', 'd', 'b']
y = [1, 2, 3, 4]

plt.bar(x, y, alpha=0.5, width=0.3, color='yellow', edgecolor='red', label='The First Bar', lw=3)
plt.legend(loc='upper left')

plt.show()
#%%
import json
with open('data/OkexSubscriber2020-05-24', 'r') as f:
    #update_count =0
    for line in f.readlines():
        line_data = json.loads(line)

        if "stream" in line_data:
            pass
            print("stream")
        else:
            print(line_data)
