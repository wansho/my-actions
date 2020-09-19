# -*- coding:utf-8 -*-
import json
import logging
import datetime
import os

import requests
import pandas as pd


pd.set_option('max_colwidth', 100)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


output_file = "report.html"


def get_hot_topics():
    """获取知乎，微博热搜
    """
    # 知乎
    url = "http://hotso.top/hotso/v1/hotso/zhihu/10"
    results = dict(requests.get(url).json())
    response_dump(results)
    zhihu_hot_list = []
    for item in results["data"]:
        zhihu_hot_list.append({"title": item["title"], "url": item["url"], "reading": item["reading"]})
    pd_zhihu_hot_list = pd.DataFrame(zhihu_hot_list, columns=["title", "url", "reading"])
    print(pd_zhihu_hot_list)

    # 微博
    url = "http://hotso.top/hotso/v1/hotso/weibo/10"
    results = dict(requests.get(url).json())
    response_dump(results)
    weibo_hot_list = []
    for item in results["data"]:
        weibo_hot_list.append({"title": item["title"], "reading": item["reading"]})
    pd_weibo_hot_list = pd.DataFrame(weibo_hot_list, columns=["title", "reading"])
    print(pd_weibo_hot_list)

    return {"zhihu": pd_zhihu_hot_list,
            "weibo": pd_weibo_hot_list,
            }


def response_dump(response_dict):
    """将响应结果存储"""
    with open("response-data-backup-hot-topics.json", "w") as fw:
        json.dump(response_dict, fw)
    logger.info("Response backup success.")


def render(dict_pd_data):
    """渲染 html
    将数据渲染到 html 模板中
    """
    html_zhihu = dict_pd_data["zhihu"].to_html(render_links=True)
    html_weibo = dict_pd_data["weibo"].to_html(render_links=True)
    if os.path.exists(output_file):
        open_path = output_file
    else: # report-weather 脚本运行失败，
        open_path = "markdown-template.html"
    with open(open_path, 'r', encoding="utf-8") as fr:
        html_source = fr.read()
    html = html_source.replace("hot-zhihu", html_zhihu)
    html = html.replace("hot-weibo", html_weibo)
    return html


if __name__ == '__main__':
    dict_pd_data = get_hot_topics()
    html = render(dict_pd_data)
    # 存储结果，结果是存储在 Github 提供的虚拟环境中的，还可以再次使用
    with open(output_file, 'w', encoding="utf-8") as fw:
        fw.write(html)
