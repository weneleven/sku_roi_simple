# SKU ROI 简单模型执行指南

## 1. 进入项目目录
```bash
cd /Users/chenke.188/Documents/code/COI/sku_roi_simple
```

## 2. 执行数据抽取任务
```bash
# 执行脚本，生成数据到 HDFS
bash script/run.sh 20260519
```

## 3. 等待任务完成
任务执行完成后会显示类似：
```
[INFO] hadoop fs -touchz hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple/dt=2026-05-19/_SUCCESS
```

## 4. 检查输出数据
```bash
# 查看输出目录
hadoop fs -ls hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple/dt=2026-05-19

# 查看数据样本
hadoop fs -cat hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple/dt=2026-05-19/* | head -5
```

## 5. 执行训练
```bash
# 进入训练目录
cd train

# 执行训练脚本
python train.py hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple/dt=2026-05-19
```

## 6. 查看结果
训练完成后会显示 RMSE 值，并生成模型文件 `gbm_model.txt`

## 常见问题

### 权限问题
如果遇到权限问题，可以尝试：
```bash
hadoop fs -chmod -R 777 hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple
```

### 数据日期
如果想处理其他日期的数据，修改 run.sh 中的日期参数：
```bash
bash script/run.sh 20260518
```

### 查看 Hive 执行日志
如果 Hive 执行失败，可以查看详细日志：
```bash
hive -f script/sku_roi_simple.hql --define output_path=hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188/sku_roi_simple --define hive_date=2026-05-19 -hiveconf hive.root.logger=DEBUG,console
```