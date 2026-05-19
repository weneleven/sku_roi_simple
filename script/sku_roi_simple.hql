set hive.session.id="sku_roi_simple@chenke188";
set mapreduce.map.memory.mb=4096;
set mapreduce.reduce.memory.mb=4096;

insert overwrite directory '${output_path}/dt=${hive_date}'
row format delimited
fields terminated by '\t'

select
    range.sku_id,
    range.sku_name,
    (perf.gmv / perf.cost) as roi
from
(
    select sku_id, sku_name
    from ad.ad_recommend_sku_feature
    where dt = '${hive_date}'
) range
join
(
    select
        cast(sku_id as bigint)  as sku_id,
        sum(impressions_ad)     as impressions,
        sum(clicks_ad)          as clicks,
        sum(cost_ad)            as cost,
        sum(case when adv_deal_order_price < 100000 then adv_deal_order_price else 0 end) as gmv
    from ad.ad_r_olap_full_site_report
    where dt >= '${start_date}'
      and dt <= '${hive_date}'
      and campaign_type = '101'
      and (period_order_track = '0' or period_order_track is null or period_order_track = '')
      and periods in ('0', '1')
    group by cast(sku_id as bigint)
) perf
on range.sku_id = perf.sku_id
where perf.cost > 0
;