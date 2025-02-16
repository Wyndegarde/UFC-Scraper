import pandas as pd

from django.http import HttpResponse, JsonResponse
from src.config import PathSettings
from src.lib.modelling.inference import Inference


def predictor(request):
    inference = Inference(PathSettings.MODEL_WEIGHTS, PathSettings.NEXT_EVENT_CSV)
    predictions = inference.predict()
    return HttpResponse(predictions)


def show_next_event(request):
    df = pd.read_csv(PathSettings.NEXT_EVENT_CSV)
    # get red and blue fighters for event and store in json
    fighters = df[["red_fighter", "blue_fighter"]].to_dict(orient="records")
    return JsonResponse({"data": fighters})
