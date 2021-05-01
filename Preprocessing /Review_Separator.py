from pyspark.sql.functions import col
import pyspark

"""
This script take path and name of json file of data set and convert it into a CSV file which only contain reviews

"""


def data_loader(file_path, new_file_path):
    data_ori = sqlContext.read.format('json').option('header', False).option('multiline', True).load(file_path)
    data_pd = data_ori.select(col("review_detail")).toPandas()
    data_pd.to_csv(new_file_path, index=False)


if __name__ == '__main__':
    # Set the file_path of dataset file
    # Set the path for new CSV file
    file_path = ""
    new_file_path = ""
    data_loader(file_path, new_file_path)
