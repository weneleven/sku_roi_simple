#!/usr/bin/env python
#coding:utf-8

import logging
import sys
import os
import subprocess
import time
import datetime


# 安全护栏：所有 hadoop 写/删操作必须落在以下前缀下
SAFE_HDFS_PREFIX = 'hdfs://ns82004/user/mart_ads/mart_ads_delivery/user/chenke188'


def _assert_safe_path(hadoop_path):
    """确保 hadoop_path 在 chenke188 自己的目录下，且不是顶级目录本身"""
    p = hadoop_path.strip()
    if not p.startswith(SAFE_HDFS_PREFIX + '/'):
        msg = 'UNSAFE PATH refused: [%s], must start with [%s/]' % (p, SAFE_HDFS_PREFIX)
        logging.error(msg)
        sys.exit(msg)
    # 防止 dt= 后面是空串，导致整个 sku_roi_simple 被删
    if p.endswith('/dt=') or p.endswith('dt=') or p.endswith('/'):
        msg = 'SUSPICIOUS PATH refused: [%s], looks like an empty date partition' % p
        logging.error(msg)
        sys.exit(msg)


def exe_cmd_system(cmd, exit=True):
    logging.info(cmd)
    ret = os.system(cmd)
    if ret != 0:
        msg = 'execute cmd [%s] error' % cmd
        if exit:
            msg += ', exit!'
            logging.error(msg)
            sys.exit(msg)
        else:
            logging.warning(msg)
    return ret


def hadoop_remove(hadoop_path, exit=False):
    _assert_safe_path(hadoop_path)
    cmd = 'hadoop fs -rm -r %s' % hadoop_path
    exe_cmd_system(cmd, exit)


def hadoop_touch_success(hadoop_path):
    _assert_safe_path(hadoop_path)
    cmd = 'hadoop fs -touchz %s/_SUCCESS' % hadoop_path
    exe_cmd_system(cmd, True)


def check_hive_partition_by_date(table_name, hive_date, retry_times=5, interval_minutes=5):
    partition_name = "dt='%s'" % hive_date
    hive_cmd = 'show partitions %s partition (%s)' % (table_name, partition_name)
    cmd = 'hive -S -e "%s" 2> /dev/null' % hive_cmd
    for i in range(1, retry_times + 1):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
        if out.strip() != '':
            break
        if i == retry_times:
            msg = 'Hive table %s partition %s not exist, retry %d times, exit!' % (table_name, partition_name, i)
            logging.error(msg)
            sys.exit(msg)
        else:
            msg = 'Hive table %s partition %s not exist, will retry after sleep %d minute' % (table_name, partition_name, interval_minutes)
            logging.warning(msg)
            time.sleep(interval_minutes * 60)