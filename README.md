# Telegram-DDoS-Bot

需要安装的依赖有：

- flask
- python-telegram-bot
- pywget
- requests
- psutils
- python-telegram-bot[job-queue]

用法：修改`api.py`内的方法为你自己的，放到你的后端服务器上并开放端口。

修改`config.yaml.example`内的配置并将其重命名为`config.yaml`。

使用`Navicat`等程序修改`Ayachi.db`内的API信息，启动机器人即可。

本程序采用`MIT`协议进行分发，在未经过我允许的情况下，禁止商用、禁止修改作者版权信息。