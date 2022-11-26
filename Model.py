import tensorflow as tf
import numpy as np

class Model():
    def __init__(self):
        self.model = tf.keras.models.load_model("../ChessELOPrediction/model")

    def predict_scores(self, boards):
        print(boards)
        scores = self.model.predict(boards)
        print("move prediction", scores, np.shape(boards))
        return scores