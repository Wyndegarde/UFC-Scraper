from django.http import HttpResponse
from rest_framework_swagger.views import get_swagger_view

from src.config.config import PathSettings
from src.lib.data_cleaning.data_cleaning import DataCleaner
from src.lib.pipelines import DataCleaningPipeline
from src.lib.processing.handlers import CSVProcessingHandler


def preprocess_data(request):
    data_cleaning_pipeline = DataCleaningPipeline(
        DataCleaner(PathSettings.RAW_DATA_CSV),
        CSVProcessingHandler(PathSettings.CLEANED_DATA_CSV, allow_creation=True),
    )
    data_cleaning_pipeline.run()
    return HttpResponse("Preprocessing data")
