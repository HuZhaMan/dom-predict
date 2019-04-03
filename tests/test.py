from IPython import display
import docs.conf as conf
import dom.query_data as query
import dom.dh.pre_process as ppd
import dom.dh.deep_learning as dl
import pandas as pd

dir_path = conf.training_model_dir

if __name__ == "__main__":
   test = pd.DataFrame()
   test['abc'] = []
   display.display(test.get('bbb'))
   # display.display(test.keys().has_key('abc'))