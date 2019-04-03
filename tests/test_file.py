from typing import List
# from saninco_docs import conf as conf
import docs.conf as conf

dir_path = conf.training_model_dir

if __name__ == "__main__":
    test_array = ['"a":1', '"c":2', '"d":4', '"f":[5]']
    a = '{' + ','.join(test_array) + '}'
    z = {}
    print(a)
    with open(dir_path + '/a_test.feature.columns', 'w+') as f:
        f.writelines(a)
        f.close()

    with open(dir_path + '/a_test.feature.columns', 'r') as f:
        z = eval(f.read())
    print(z)
    print(type(z))
    print(z['f'][0])
