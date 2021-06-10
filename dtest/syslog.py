import logging
logging.basicConfig()
log=logging.getLogger()
#设置日期等级
log.setLevel(logging.DEBUG)
#设置日志格式
formatter=logging.Formatter("%(asctime)s %(levelname)s %(pathname)s %(message)s ")
fileHandler=logging.FileHandler("log.log",encoding="utf-8")
fileHandler.setFormatter(formatter)
# consoleHandler=logging.StreamHandler()
# consoleHandler.setFormatter(formatter)
#添加fileHandler，输出日志到文件
log.addHandler(fileHandler)
#添加consoleHandler,输出日志到控制台
# log.addHandler(consoleHandler)