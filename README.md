# TDE
> Trading Data Engineering

## 数据分析策略

- 市场决定策略模型，策略模型决定策略决策，决策方法决定分析预测状态，分析预测状态来自数据分析
- 从数据中来，到数据中去，万事不明看数据:定量问题要从数据量化分析决定，定性问题还是由数据量化分析决定，并最终在数据结果中验证。
- 双向流动性供需的模型比单纯价格分析更要细腻一点，同时需要注意双向供需之间又有影响

## 架构设计
1. Tensorflow对Python的版本形成限制，经过验证的最高版本是python3.8

## 主要python库
```
jupyter = "*"
numpy = "*"
pandas = "*"
pandas-datareader = "*"
matplotlib = "*"
statsmodels = "*"
scikit-learn = "*"
mplfinance = "*"
tensorflow = "*" 
torch = "*"
torchvision = "*"
dask = {extras = ["complete"], version = "*"}
```
