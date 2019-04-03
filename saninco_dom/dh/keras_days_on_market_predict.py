# -*- coding: UTF-8 -*-
from sklearn import metrics
from IPython import display
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
import os as os
import saninco_docs.conf as conf
import saninco_dom.query_data as query
from saninco_dom.dh.custom_label_encoder import TolerantLabelEncoder
import pandas as pd

# load dataset
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
training_properties_path = conf.root_path + "saninco_dom/dh/training.properties"


class DeepLearning:
    training_data = None
    predict_data = None
    le_city = None
    le_province = None
    le_postal_code = None
    le_owner_ship_type = None
    le_listing_date = None
    le_dictionary_code = None
    model_dir = conf.training_model_dir
    dictionary = None

    def __init__(self, training_data=None, predict_data=None, is_load_label_encoder=True):

        if training_data is not None:
            self.pre_process_training_data(training_data)
        if predict_data is not None:
            self.predict_data = predict_data
        if is_load_label_encoder:
            self.load_features_label_encoder()

    def pre_process_training_data(self, data):

        data = data.dropna(axis=0)
        data = data[data['longitude'] != 0]
        data = data[data['latitude'] != 0]
        data = data[data['tradeTypeId'] != 2]
        data = data[data['longitude'] >= -145]
        data = data[data['longitude'] <= -45]
        data = data[data['latitude'] >= 40]
        data = data[data['latitude'] <= 90]
        data = data[data['daysOnMarket'] > 0]
        data = data[data['price'] > 1]
        self.training_data = data

        return self

    def load_features_label_encoder(self):

        with open(training_properties_path, 'r', encoding='utf-8') as f:
            self.dictionary = eval(f.read())
            f.close()
        if self.dictionary.get("city_dictionary") is not None:
            self.le_city = TolerantLabelEncoder(ignore_unknown=True).fit(self.dictionary.get("city_dictionary"))

        if self.dictionary.get("province_dictionary") is not None:
            self.le_province = TolerantLabelEncoder(ignore_unknown=True).fit(self.dictionary.get("province_dictionary"))

        if self.dictionary.get("ownership_dictionary") is not None:
            self.le_owner_ship_type = TolerantLabelEncoder(ignore_unknown=True).fit(
                self.dictionary.get("ownership_dictionary"))

        if self.dictionary.get("postcode_first_three_list") is not None:
            self.le_postal_code = TolerantLabelEncoder(ignore_unknown=True).fit(
                self.dictionary.get("postcode_first_three_list"))

        if self.dictionary.get("district_dictionary") is not None:
            self.le_dictionary_code = TolerantLabelEncoder(ignore_unknown=True).fit(
                self.dictionary.get("district_dictionary"))

        self.le_listing_date = TolerantLabelEncoder(ignore_unknown=True).fit(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        return self

    def write_features_dictionary(self):

        city_dictionary = list(filter(None, query.get_city_dictionary()))
        postcode_first_three_dictionary = list(filter(None, query.get_postcode_dictionary()))
        province_dictionary = list(filter(None, query.get_province_dictionary()))
        ownership_dictionary = list(filter(None, query.get_ownership_dictionary()))
        district_dictionary = list(filter(None, query.get_district_dictionary()))
        content = {"city_dictionary": city_dictionary,
                   "province_dictionary": province_dictionary,
                   "postcode_first_three_list": postcode_first_three_dictionary,
                   "ownership_dictionary": ownership_dictionary,
                   "district_dictionary": district_dictionary}
        with open(training_properties_path, 'w+', encoding='utf-8') as f:
            f.writelines(str(content))
            f.close()
        return self

    def pre_process_features(self, data):

        #
        # data["bedrooms"] = data["bedrooms"].fillna("1")
        # data["bathroomTotal"] = data["bathroomTotal"].fillna("1")
        # data["ownerShipType"] = data["ownerShipType"].fillna("none")
        data = data.dropna(axis=0)
        if len(data) == 0:
            return None
        bedrooms_list = []
        for bedrooms in data["bedrooms"]:
            # display.display(bedrooms)
            bedrooms_list.append(int(eval(str(bedrooms))))
        data["bedrooms"] = bedrooms_list
        bathroom_total_list = []
        for bathroom_total in data["bathroomTotal"]:
            bathroom_total_list.append(int(bathroom_total))
        data["bathroomTotal"] = bathroom_total_list
        # postcode_list = []
        # for item in data["postalCode"]:
        #     postcode_list.append(str(item.split(' ')[0]))
        # data["postalCode"] = postcode_list
        listing_date_month = []
        for item in data["listingDate"]:
            listing_date_month.append(int(item.split('-')[1]))
        data["listingDate"] = listing_date_month
        result_data = data[
            ["longitude",
             "latitude",
             "price",
             "city",
             "postalCode",
             "district",
             "province",
             "tradeTypeId",
             "buildingTypeId",
             "listingDate",
             "bedrooms",
             "bathroomTotal",
             "ownerShipType",
             ]]

        if data.get('daysOnMarket') is not None:
            result_data['daysOnMarket'] = data['daysOnMarket']
        if data.get('realtorDataId') is not None:
            result_data['realtorDataId'] = data['realtorDataId']
        if data.get('realtorSearchId') is not None:
            result_data['realtorSearchId'] = data['realtorSearchId']
        if data.get('realtorDataPredictId') is not None:
            result_data['realtorDataPredictId'] = data['realtorDataPredictId']

        result_data["city"] = self.le_city.transform(result_data["city"])
        result_data["province"] = self.le_province.transform(result_data["province"])
        result_data["postalCode"] = self.le_postal_code.transform(result_data["postalCode"])
        result_data["district"] = self.le_dictionary_code.transform(result_data["district"])
        result_data["listingDate"] = self.le_listing_date.transform(result_data["listingDate"])
        result_data["ownerShipType"] = self.le_owner_ship_type.transform(result_data["ownerShipType"])

        return result_data

    def baseline_model(self, model_name=None):
        # create model
        model = Sequential()
        model.add(Dense(1024, input_dim=13, kernel_initializer='normal', activation='relu'))
        model.add(Dense(512, activation='relu'))
        model.add(Dense(256, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, kernel_initializer='normal'))
        # Compile model
        model.compile(loss='mean_absolute_error', optimizer='Adagrad')

        if model_name is None:
            model_name = 'my_model_weights.h5'

        model_path = self.model_dir + model_name
        if os.path.exists(model_path):
            model.load_weights(model_path)
        return model

    def training(self, training_data=None, batch_size=128, epochs=10, model_name=None,
                 is_save_model=True):

        if training_data is None:
            training_data = self.training_data
        model = self.baseline_model(model_name=model_name)

        data_set = self.pre_process_features(data=training_data).values
        # split into input (X) and output (Y) variables
        x = data_set[:, 0:13]
        display.display(x)
        y = data_set[:, 13]
        display.display(y)

        model.fit(x=x, y=y, batch_size=batch_size, epochs=epochs)
        if is_save_model:
            if model_name is None:
                model_name = 'my_model_weights.h5'

            model_path = self.model_dir + model_name
            model.save_weights(model_path)

        return self

    def predict(self, predict_data=predict_data, batch_size=128, model_name=None):

        if predict_data is None:
            predict_data = self.predict_data
        model = self.baseline_model(model_name=model_name)
        predict_data = self.pre_process_features(data=predict_data)

        if predict_data is not None:
            data_set = predict_data.values
            # split into input (X) and output (Y) variables
            x = data_set[:, 0:13]
            predict_result = model.predict(x=x, batch_size=batch_size)

            predict_data['predict'] = predict_result
            predict_data[predict_data['predict'] < 1] = 1

            result_data = predict_data[["predict"]]
            if predict_data.get('realtorSearchId') is not None:
                result_data["realtorSearchId"] = predict_data['realtorSearchId']
            if predict_data.get('realtorDataId') is not None:
                result_data["realtorDataId"] = predict_data['realtorDataId']
            if predict_data.get('realtorDataPredictId') is not None:
                result_data["realtorDataPredictId"] = predict_data['realtorDataPredictId']

            self.predict_data = predict_data
        else:
            self.predict_data = []


if __name__ == "__main__":

    # deep_learn = DeepLearning(is_load_label_encoder=False)
    # deep_learn.write_features_dictionary()
    # with open(training_properties_path, 'r', encoding='utf-8') as f:
    #     dictionary = eval(f.read())
    #     print(dictionary)
    #     f.close()

    # try:
    t_data = pd.read_csv(conf.root_path + "saninco_docs/housing_data_training_09.csv", sep=",")
    p_data = pd.read_csv(conf.root_path + "saninco_docs/housing_data_predict_09.csv", sep=",")
    deep_learn = DeepLearning(training_data=t_data, predict_data=p_data)
    # deep_learn.training(epochs=32, model_name='my_model_weights_new.h5', batch_size=128)
    deep_learn.predict(model_name='my_model_weights.h5')
    r_predict_data = deep_learn.predict_data
    root_mean_absolute_error = metrics.mean_absolute_error(r_predict_data['daysOnMarket'], r_predict_data['predict'])
    print(root_mean_absolute_error)
    deff10 = 0
    deff20 = 0
    deff30 = 0
    deff30more = 0
    result = []
    P_Y = r_predict_data['predict'].values
    R_Y = r_predict_data['daysOnMarket'].values
    for index in range(len(P_Y)):
        # display.display(item)
        result.append(int(P_Y[index]))
        deff = abs(int(R_Y[index]) - int(P_Y[index]))
        # display.display(deff)
        if deff <= 10:
            deff10 = deff10 + 1
        elif 10 < deff <= 20:
            deff20 = deff20 + 1
        elif 20 < deff <= 30:
            deff30 = deff30 + 1
        else:
            deff30more = deff30more + 1

    print(deff10 / len(R_Y))
    print(deff20 / len(R_Y))
    print(deff30 / len(R_Y))
    print(deff30more / len(R_Y))
    # except ZeroDivisionError as e:
    #     print(e.args)
