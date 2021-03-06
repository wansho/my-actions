# -*- coding:utf-8 -*-
import json
import logging
import datetime

import requests
import pandas as pd

pd.set_option('display.max_colwidth', -1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 经纬度 - 东南大学
latitude = 118.82
longitude = 31.89

token = "DaO5SS5YytstuBJd"
STATUS_OK = "ok"


def get_weather():
    weather = {}
    # https://api.caiyunapp.com/v2.5/DaO5SS5YytstuBJd/118.82,31.89/weather.json
    url = "https://api.caiyunapp.com/v2.5/{token}/{latitude},{longitude}/weather.json".format(
        latitude=latitude,
        longitude=longitude,
        token=token
    )
    results = dict(requests.get(url).json())
    response_dump(results)
    # 判断 api 是否返回数据
    status = results.get("status")
    if not status == STATUS_OK:
        logger.error("api 失效，status == {status}".format(
            status=status,
        ))
        return weather

    # 获取预测数据
    forecast_keypoint = results["result"]["forecast_keypoint"]
    column_weather = ["Location", "forecast_keypoint", "hourly_desc"]
    weather.update({"forecast_keypoint": forecast_keypoint, "Location": "南京九龙湖"})

    # 获取 daily 数据 pandas
    daily_data = dict(results["result"]["daily"])
    pd_daily_weather = pd.DataFrame(columns=["date", "temp_min", "temp_max",
                                             "precipitation_desc", "skycon", "precipitation_max"])
    pd_daily_precipitation = pd.DataFrame(daily_data["precipitation"])
    pd_daily_weather["date"] = pd_daily_precipitation["date"].apply(
        lambda x: datetime.datetime.strptime(str(x)[: 10], "%Y-%m-%d")
    )
    pd_daily_temperature = pd.DataFrame(daily_data["temperature"])
    pd_daily_weather["temp_max"] = pd_daily_temperature["max"]
    pd_daily_weather["temp_min"] = pd_daily_temperature["min"]
    pd_daily_weather["precipitation_max"] = pd_daily_precipitation["max"]
    pd_daily_weather["precipitation_desc"] = pd_daily_weather["precipitation_max"].apply(
        lambda x: precipitation_2_desc(x)
    )
    pd_daily_weather["skycon"] = pd.DataFrame(daily_data["skycon"])["value"]

    # 获取实时数据
    realtime_data = dict(results["result"]["realtime"])
    realtime_precipitation = realtime_data["precipitation"]["local"]["intensity"]
    realtime_dict = {"temperature": realtime_data["temperature"],
                     "skycon": realtime_data["skycon"],
                     "precipitation": realtime_precipitation,
                     "precipitation_desc": precipitation_2_desc_radar(realtime_precipitation),
                     "life_index": realtime_data["life_index"]["comfort"]["desc"]
                     }
    pd_realtime_weather = pd.DataFrame(columns=["temperature", "skycon", "precipitation",
                                                "life_index", "precipitation_desc" ])
    pd_realtime_weather = pd_realtime_weather.append(realtime_dict, ignore_index=True)

    # 获取 hourly 数据 pandas
    hourly_data = dict(results["result"]["hourly"])
    hourly_desc = hourly_data["description"]
    weather.update({"hourly_desc": hourly_desc})
    pd_hourly_weather = pd.DataFrame(columns=["datetime", "temperature",
                                              "precipitation_desc", "skycon", "precipitation"])
    pd_hourly_precipitation = pd.DataFrame(hourly_data["precipitation"])
    pd_hourly_weather["datetime"] = pd_hourly_precipitation["datetime"].apply(
        lambda x: datetime.datetime.strptime(str(x)[: 10] + " " + str(x)[11: 16], "%Y-%m-%d %H:%M")
    )
    pd_hourly_temperature = pd.DataFrame(hourly_data["temperature"])
    pd_hourly_weather["temperature"] = pd_hourly_temperature["value"]
    pd_hourly_weather["precipitation"] = pd_hourly_precipitation["value"]
    pd_hourly_weather["precipitation_desc"] = pd_hourly_weather["precipitation"].apply(
        lambda x: precipitation_2_desc_radar(x)
    )
    pd_hourly_weather["skycon"] = pd.DataFrame(hourly_data["skycon"])["value"]
    pd_hourly_weather = pd_hourly_weather[: 12] # 只选取未来 12 小时的数据

    # 天气概况
    pd_weather = pd.DataFrame(columns=column_weather)
    pd_weather = pd_weather.append(weather, ignore_index=True)

    print(pd_hourly_weather)
    print(pd_daily_weather)
    print(pd_weather)
    print(pd_realtime_weather)
    # plot_daily_weather(pd_daily_weather)

    return {"weather": pd_weather,
            "daily_weather": pd_daily_weather,
            "realtime_weather": pd_realtime_weather,
            "hourly_weather": pd_hourly_weather
            }


# def plot_daily_weather(pd_daily_weather):
#     """绘制图表"""
#     x_labels = [str(date)[: 10] for date in pd_daily_weather["date"].tolist()]
#     temperature_max_lst = pd_daily_weather["temperature_max"].tolist()
#     temperature_min_lst = pd_daily_weather["temperature_min"].tolist()
#     life_desc = (pd_daily_weather["precipitation_desc"] + pd_daily_weather["skycon"]).tolist()
#     fig = plt.figure()
#     x = list(range(1, len(x_labels) + 1))
#     y = temperature_max_lst
#     plt.xticks(x, x_labels)
#     plt.ylim(-5, 40)
#     plt.plot(x, y, "-o")
#     plt.savefig('test.png')
#
#     pass


def response_dump(response_dict):
    """将响应结果存储"""
    with open("response-data-backup-weather.json", "w") as fw:
        json.dump(response_dict, fw)
    logger.info("Response backup success.")


def render(dict_pd_data):
    """渲染 html
    将天气数据渲染到 html 模板中
    """
    # 渲染天气数据
    html_weather = dict_pd_data["weather"].to_html()
    html_daily_weather = dict_pd_data["daily_weather"].to_html()
    html_realtime_weather = dict_pd_data["realtime_weather"].to_html()
    html_hourly_weather = dict_pd_data["hourly_weather"].to_html()
    with open('markdown-template.html', 'r', encoding="utf-8") as fr:
        html_source = fr.read()
    html = html_source.replace("abstract-weather-table", html_weather)
    html = html.replace("daily-weather-table", html_daily_weather)
    html = html.replace("realtime-weather-table", html_realtime_weather)
    html = html.replace("hourly-weather-table", html_hourly_weather)
    return html


def precipitation_2_desc(precipitation):
    """描述降水量"""
    if precipitation < 0.08:
        desc = "无雨／雪"
    elif precipitation < 3.44:
        desc = "小雨／雪"
    elif precipitation < 11.33:
        desc = "中雨／雪"
    elif precipitation < 51.30:
        desc = "小雨／雪"
    else:
        desc = "暴雨／雪"
    return desc


def precipitation_2_desc_radar(precipitation):
    """描述雷达降水强度"""
    if precipitation < 0.031:
        desc = "无雨／雪"
    elif precipitation < 0.25:
        desc = "小雨／雪"
    elif precipitation < 0.35:
        desc = "中雨／雪"
    elif precipitation < 0.48:
        desc = "小雨／雪"
    else:
        desc = "暴雨／雪"
    return desc


if __name__ == '__main__':
    dict_pd_data = get_weather()
    html = render(dict_pd_data)
    # 存储结果，结果是存储在 Github 提供的虚拟环境中的，还可以再次使用
    with open('report.html', 'w', encoding="utf-8") as fw:
        fw.write(html)
