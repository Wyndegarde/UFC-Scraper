from django.http import HttpResponse
from src.config import PathSettings
from src.lib.modelling.inference import Inference


def predictor(request):
    inference = Inference(PathSettings.MODEL_WEIGHTS, PathSettings.NEXT_EVENT_CSV)
    predictions = inference.predict()
    return HttpResponse(predictions)
