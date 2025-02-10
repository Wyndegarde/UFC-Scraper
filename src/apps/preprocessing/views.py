from django.http import HttpResponse

from src.config.config import PathSettings
from src.lib.data_cleaning.data_cleaning import DataCleaner


def preprocess_data(request):

    data_cleaner = DataCleaner(PathSettings.RAW_DATA_CSV)
    data_cleaner.clean_raw_data()

    return HttpResponse("Preprocessing data")
