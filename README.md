# 12306-force-transfer

用于增强12306同站换乘班次搜索的功能

### 依赖库
+ requests
+ pandas
+ tabulate

### 用法

#### 获取库

```
git clone https://github.com/jimrueaster/12306-smart-transfer.git
```

#### 切换到代码根目录

```
cd 12306-smart-transfer
```

#### 获取 JRUtils 工具库

```
git clone https://github.com/jimrueaster/JRUtils.git
```

### 修改提示语句为“你的实际始发和终到站”

```
# main.py
print(u'广州南->香港西九龙', end='\n\n')

print(u'香港西九龙->广州南', end='\n\n')
```

### 修改参数
> [站点缩写参考](https://kyfw.12306.cn/otn/resources/js/framework/station_name.js)

```
# from_station      出发站
# transfer_station  换乘站
# to_station        到达站
# from_time         最早出发时间
# no_more_than      整体行程耗时限制(分钟)
# to_time           最晚到达时间

smart_transfer(set_off_date=date, from_station='IZQ', transfer_station='IOQ',
               to_station='XJA', from_time=10, no_more_than=90, to_time=12)

smart_transfer(set_off_date=date, from_station='XJA', transfer_station='IOQ',
               to_station='IZQ', from_time=20, no_more_than=90, to_time=22)
```

### 运行脚本即可输出可视化结果

```
Done!
```
