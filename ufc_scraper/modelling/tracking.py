import mlflow


class ExperimentTracking:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.experiment_id = None
        self.run_id = None

    def create_experiment(self):
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment(self.experiment_name)
        self.experiment_id = mlflow.get_experiment_by_name(
            self.experiment_name
        ).experiment_id
        print(
            f"Experiment '{self.experiment_name}' created with ID {self.experiment_id}"
        )

    def connect_to_experiment(self):
        mlflow.set_tracking_uri("http://localhost:5000")
        self.experiment_id = mlflow.get_experiment_by_name(
            self.experiment_name
        ).experiment_id
        print(
            f"Connected to experiment '{self.experiment_name}' with ID {self.experiment_id}"
        )

    def start_run(self, run_name=None):
        with mlflow.start_run(
            run_name=run_name, experiment_id=self.experiment_id
        ) as run:
            self.run_id = run.info.run_id
            print(f"Run '{run_name}' started with ID {self.run_id}")
