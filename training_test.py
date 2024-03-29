from ufc_scraper.modelling import Training, Inference
from ufc_scraper.config import PathSettings


def main():
    training = Training(PathSettings.TRAINING_DATA_CSV)
    training.train_model()
    inference = Inference(PathSettings.MODEL_WEIGHTS, PathSettings.NEXT_EVENT_CSV)
    predictions = inference.predict()
    print(predictions)


if __name__ == "__main__":
    main()
