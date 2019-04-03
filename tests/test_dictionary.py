import docs.conf as conf
import dom.query_data as query

def write_features_dictionary(self):
    city_dictionary = query.get_city_dictionary()
    postcode_dictionary = query.get_postcode_dictionary()
    province_dictionary = query.get_province_dictionary()
    postcode_first_three_list = []
    for item in province_dictionary:
        postcode_first_three_list.append(item.split(' ')[0])
        postcode_first_three_list = set(postcode_first_three_list)
    ownership_dictionary = query.get_ownership_dictionary()
    with open(conf.model_dictionary_path, 'w+') as f:
        f.writelines({"city_dictionary", city_dictionary})
        f.writelines({"postcode_dictionary", postcode_dictionary})
        f.writelines({"province_dictionary", province_dictionary})
        f.writelines({"postcode_first_three_list", postcode_first_three_list})
        f.writelines({"ownership_dictionary", ownership_dictionary})
        f.close()
    return self


if __name__ == "__main__":

    write_features_dictionary(None)