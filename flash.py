# %%
import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random
from sklearn.tree import DecisionTreeRegressor

# %%
class RealSystem:
    def __init__(self, features, measurements_path, target_max):
        all_confs = np.array(list(itertools.product(*features))).astype(np.float32)
        all_confs = [str(conf) for conf in all_confs]
        self.all_confs = all_confs
        self.target_max = target_max
        self.eval_data_df = pd.read_csv(measurements_path)
        self.measurements_path = measurements_path
        
    def measure(self, conf):
        """测量conf的性能值"""
        assert isinstance(conf, str)
        print("measuring manually...")
        inp = input("input measurement result of conf {} : ".format(conf))
        inp = float(inp)
        return inp
    
    def add_conf_perf(self, conf, perf):
        """将已测量配置写入文件
        Args:
            conf (numpy.ndarray or str): shape(n, )
            perf (float): _description_
        """
        if isinstance(conf, str):
            conf = np.array(list(map(float, conf[1:-1].split())))
        item = np.concatenate([conf, [perf]])
        self.eval_data_df.loc[len(self.eval_data_df)] = item
        self.eval_data_df.to_csv(self.measurements_path, index=False)
        
    def get_eval_data(self):
        """返回用于建模的已测量配置的numpy数组"""
        data = self.eval_data_df.to_numpy().astype(np.float32)
        X = data[:, :-1]
        y = data[:, -1:].flatten()
        return X, y


def argmax_acquisition(model, uneval_configs, target_max=True):
    """对uneval_configs进行预测，返回最优配置"""
    X = np.array([np.array(list(map(float, key[1:-1].split()))) for key in uneval_configs])
    y = model.predict(X)
    if target_max:
        optimal = np.max(y)
    else:
        optimal = np.min(y)
    indices = np.where(y == optimal)[0]
    np.random.seed(42)
    idx = np.random.choice(indices)
    return str(X[idx]), y[idx]


def flash(system, budget):

    target_max = system.target_max
    
    # 初始化未测量池为 全部配置，测量池为 空集
    eval_configs = system.eval_data_df.values[:, :-1]
    eval_configs = set([str(conf) for conf in eval_configs])
    uneval_configs = system.all_confs.copy()
    for conf in eval_configs:
        uneval_configs.remove(conf)

    # 循环迭代建模
    for i in range(budget):
        # 建模
        X, y = system.get_eval_data()
        dtr = DecisionTreeRegressor(random_state=42)
        dtr.fit(X, y)
        
        # 建模后，使用采样函数，从未测量集合中选取下一个测量的点
        # 返回字符串
        acquired_conf, pred_perf = argmax_acquisition(dtr, uneval_configs, target_max=target_max)
        print("pred perf: {}, ".format(pred_perf), end="")
        
        # 测量配置
        perf = system.measure(acquired_conf)
        
        # 更新配置池
        eval_configs.add(acquired_conf)
        uneval_configs.remove(acquired_conf)

        # 更新系统已测量数据
        system.add_conf_perf(acquired_conf, perf)
    
    print("flash done")

# %%
features = [
    [0, 1, 2],
    [0, 30, 70, 100],
    [0, 1],
    [0, 1],
    [0, 1],
    [0, 1],
    [0, 1]
]
system = RealSystem(features, "./data.csv", target_max=False)
flash(system, 15)
# system.all_confs8.57361

# %%



