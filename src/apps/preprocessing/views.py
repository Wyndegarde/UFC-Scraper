from django.http import HttpResponse

from src.lib.pipelines import DataCleaningPipeline


def preprocess_data(request):
    data_cleaning_pipeline = DataCleaningPipeline()
    data_cleaning_pipeline.run()

    return HttpResponse("Preprocessing data")
