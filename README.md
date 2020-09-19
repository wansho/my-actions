# my-actions

[TOC]

My GitHub Actions

## Dependency

* Yandex wanshojs@yandex.com 
  利用其 SMTP 协议发送邮件，yandex 异地登陆不会报异常

## Actions

### Workflow-Daily-Report

#### Job-Weather

干掉我没事打开手机看天气预报的坏习惯

数据来源：[彩云天气 API](https://open.caiyunapp.com/%E5%BD%A9%E4%BA%91%E5%A4%A9%E6%B0%94_API_%E4%B8%80%E8%A7%88%E8%A1%A8)

ref: [定时发送天气邮件](https://www.ruanyifeng.com/blog/2019/12/github_actions.html)

#### Job-Hot-News

干掉我没事喜欢上摸鱼网站看新闻的坏习惯

* 知乎热搜 [[api1]](http://hotso.top/hotso/v1/hotso/zhihu/10)
* 微博热搜 [[api1]](http://hotso.top/hotso/v1/hotso/weibo/10)

## To do

- [x] 改用 Python 实现各种爬虫，用 shell 脚本不太适合

- [x] 用字符绘制图表 ——> 尝试使用 matplotlib 绘制图片，然后用 html 嵌入该图片(用 Typora 设计显示模板，然后转成 html)
- [x] 为天气信息加入折叠功能，for example: [how they test](https://github.com/abhivaikar/howtheytest)  
- [x] 每日提醒：健身 / 总结