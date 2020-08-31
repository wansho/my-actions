# -*- coding:utf-8 -*-
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 经纬度 - 东南大学
latitude = 118.82
longitude = 31.89

token = "DaO5SS5YytstuBJd"
STATUS_OK = "ok"
API_STATUS_OK = "active"


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
    api_status = results.get("api_status")
    if not (status == STATUS_OK and api_status == API_STATUS_OK):
        logger.error("api 失效，status == {status}, api_status == {apt_status}".format(
            status=status,
            api_status=api_status
        ))
        return weather
    # 获取预测数据
    forecast_keypoint = results["result"]["forecast_keypoint"]
    # 获取 daily 数据
    daily_data = dict(results["result"]["daily"])
    if daily_data.get("status", "failed") != STATUS_OK:
        return weather
    weather.update({"Location": "南京九龙湖"})
    temperature = str(daily_data["temperature"][0])
    skycon = str(daily_data["skycon"][0])
    weather.update({"daily": {"temperature": temperature, "skycon": skycon},
                    "forecast_keypoint": forecast_keypoint})
    return weather


def response_dump(response_dict):
    """将响应结果存储"""
    with open("response-data-backup.json", "w") as fw:
        json.dump(response_dict, fw)
    logger.info("Response backup success.")


if __name__ == '__main__':
    weather = str(get_weather())
    with open('weather.html', 'w', encoding="utf-8") as fw:
        fw.write(str(weather))
