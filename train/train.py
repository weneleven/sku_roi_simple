#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简 GBDT 训练脚本
输入：HDFS 上 TSV 文件 (sku_id, sku_name, roi)
输出：LightGBM 模型 + 评估指标
"""

import os
import sys
import subprocess
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import mean_squared_error

# 1. 拉取数据
hdfs_path = sys.argv[1]          # e.g. hdfs://ns82004/.../dt=2026-05-19
local_dir = './data'
os.makedirs(local_dir, exist_ok=True)
cmd = f'hadoop fs -get {hdfs_path}/* {local_dir}/'
subprocess.check_call(cmd, shell=True)

# 2. 加载
df = pd.read_csv(os.path.join(local_dir, '000000_0'), sep='\t', header=None,
                 names=['sku_id', 'sku_name', 'roi'])

# 3. 特征工程：只保留 sku_name
le = LabelEncoder()
X = le.fit_transform(df['sku_name']).reshape(-1, 1)
y = df['roi']

# 4. 训练 / 验证拆分
split = int(len(df) * 0.8)
lgb_train = lgb.Dataset(X[:split], y[:split])
lgb_valid = lgb.Dataset(X[split:], y[split:], reference=lgb_train)

# 5. 训练
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'verbosity': -1,
    'seed': 42,
}
gbm = lgb.train(params, lgb_train, valid_sets=[lgb_valid],
                num_boost_round=100, early_stopping_rounds=10)

# 6. 评估
pred = gbm.predict(X[split:])
rmse = mean_squared_error(y[split:], pred, squared=False)
print('RMSE:', rmse)

# 7. 保存
gbm.save_model('gbm_model.txt')
print('模型已保存到 gbm_model.txt')