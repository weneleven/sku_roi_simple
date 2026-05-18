#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import argparse
import configparser
import logging
import datetime
import util

def run(conf, args):
    config = configparser.ConfigParser()
    config.read(conf)

    base_day = datetime.datetime.strptime(args.date, '%Y%m%d')
    day_before = config.getint('hadoop', 'day_before')
    run_day = base_day - datetime.timedelta(day_before)
    run_date = run_day.strftime('%Y%m%d')
    hive_date = run_day.strftime('%Y-%m-%d')
    logging.info('Running date is %s' % run_date)

    # 检查分区
    util.check_hive_partition_by_date('ad.ad_recommend_sku_feature', hive_date)
    util.check_hive_partition_by_date('ad.ad_r_olap_full_site_report', hive_date)

    # 清理旧输出
    output_dir = config.get('hadoop', 'output_path')
    output_path = output_dir + '/dt=' + hive_date
    util.hadoop_remove(output_path)

    # 提交 Hive
    hive_hql = config.get('hadoop', 'hive_hql')
    cmd = 'hive -f %s --define output_path=%s --define hive_date=%s' % (hive_hql, output_dir, hive_date)
    util.exe_cmd_system(cmd, True)
    util.hadoop_touch_success(output_path)

    # 清理历史
    keep_hdfs_days = config.getint('hadoop', 'keep_hdfs_days')
    if keep_hdfs_days != 0:
        remove_date = (run_day - datetime.timedelta(keep_hdfs_days)).strftime('%Y-%m-%d')
        hadoop_remove_path = output_dir + '/dt=' + remove_date
        util.hadoop_remove(hadoop_remove_path)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s %(filename)s line:%(lineno)d] [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        stream=sys.stderr,
                        filemode='a')

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='cmd', required=True, help='-t argument is necessary, run')
    parser.add_argument('-c', dest='conf', help='config')
    parser.add_argument('-d', dest='date', help='date')

    args = parser.parse_args()
    cmd = args.cmd
    if cmd == 'run':
        if args.conf is None:
            print('-c argument(conf file) is needed when cmd is run')
            sys.exit(1)
        if args.date is None:
            print('-d argument(date) is needed when cmd is run')
            sys.exit(1)
        run(args.conf, args)
    else:
        print('-t argument is wrong, run')
        sys.exit(1)
    sys.exit(0)