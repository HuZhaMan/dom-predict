# -*- coding: UTF-8 -*-
import sys
import psycopg2
import sshtunnel
import pandas as pd


def do_predict(error_times=0):
    import saninco_dom.query_data as query
    import saninco_dom.dh.keras_days_on_market_predict as kp
    import saninco_dom.mail_sender as mail_sender
    try:
        query.do_predict_fn()
        data = query.get_predict_data()
        deep_learn = kp.DeepLearning(predict_data=data)
        deep_learn.predict()
        predict_data = deep_learn.predict_data
        if predict_data is not None and len(predict_data) > 0:
            query.update_predict_data(predict_data)
        count = query.do_predict_finish()
    except psycopg2.Error as e:
        error_times = error_times + 1
        if error_times < 5:
            do_predict(error_times)
        mail_sender.send_email('失败', repr(e))
    except sshtunnel.BaseSSHTunnelForwarderError as e:
        error_times = error_times + 1
        if error_times < 5:
            do_predict(error_times)
        mail_sender.send_email('失败', repr(e))
    except Exception as e:
        print(e)
        mail_sender.send_email('失败', repr(e))
    else:
        mail_sender.send_email('成功', 'AI成功预测' + str(len(predict_data)) + '条, 总共预测' + str(count) + '条')


def main(argv):
    if type(argv) is list and len(argv) > 1:
        if argv is not None and argv[1] is not None:
            sys.path.append(argv[1])
    do_predict()


if __name__ == "__main__":
    main(sys.argv)

    # try:
    # data = pd.read_csv(conf.root_path + "saninco_docs/house_info_all_tarining.csv", sep=",")
    # p_data = pd.read_csv(conf.root_path + "saninco_docs/house_info_201808_predict.csv", sep=",")
    # deep_learn = kp.DeepLearning(training_data=data, predict_data=p_data)
    # # deep_learn.training(epochs=32)
    # deep_learn.predict()
    # predict_data = deep_learn.predict_data
    # root_mean_absolute_error = metrics.mean_absolute_error(predict_data['daysOnMarket'], predict_data['predict'])
    # print(root_mean_absolute_error)
    # deff10 = 0
    # deff20 = 0
    # deff30 = 0
    # deff30more = 0
    # result = []
    # P_Y = predict_data['predict'].values
    # R_Y = predict_data['daysOnMarket'].values
    # for index in range(len(P_Y)):
    #     # display.display(item)
    #     result.append(int(P_Y[index]))
    #     deff = abs(int(R_Y[index]) - int(P_Y[index]))
    #     # display.display(deff)
    #     if deff <= 10:
    #         deff10 = deff10 + 1
    #     elif 10 < deff <= 20:
    #         deff20 = deff20 + 1
    #     elif 20 < deff <= 30:
    #         deff30 = deff30 + 1
    #     else:
    #         deff30more = deff30more + 1
    #
    # print(deff10 / len(R_Y))
    # print(deff20 / len(R_Y))
    # print(deff30 / len(R_Y))
    # print(deff30more / len(R_Y))
    # except ZeroDivisionError as e:
    #     print(e.args)
