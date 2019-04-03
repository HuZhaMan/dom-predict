# dom-predict

#### 项目介绍
本项目为内部项目，禁止转载
本项目是saninco公司用来预测加拿大房产交易的 Days om Market.
通过远程数据库读取需要预测的数据进行预测后，再将数据存入到远程数据库中

#### 软件架构
需要技术：
    Python3
    Keras
    Postgresql


#### 使用说明

修改saninco_docs下的
    jdbc_conf.py
    conf.py
    mail_conf.py
运行scripts下的main.py
如果遇到包路径问题 需要提供系统目录参数
例如 python3 /data/tensorflow-dom/dom-predict/scripts/main.py /data/tensorflow-dom/dom-predict

#### 参与贡献

donghao.guo

