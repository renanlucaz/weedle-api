import numpy as np
import pickle
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KNNClusterPredictor:
    def __init__(self, k: int = 5, dataset_path: str = "data_exports/cliente_cluster.parquet"):
        self.k = k
        self.dataset_path = dataset_path
        self.model = None
        self.scaler = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.cluster_mapping = {}
        self.is_trained = False

    def load_model(self, filepath: str = "models/knn_model.pkl"):
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            required_keys = ['model', 'scaler', 'cluster_mapping', 'k', 'is_trained']
            for key in required_keys:
                if key not in model_data:
                    raise ValueError(f"Chave '{key}' não encontrada no arquivo do modelo")

            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.cluster_mapping = model_data['cluster_mapping']
            self.k = model_data['k']
            self.is_trained = model_data['is_trained']

            if self.model is None:
                raise ValueError("Modelo carregado é None")
            if self.scaler is None:
                raise ValueError("Scaler carregado é None")

            logger.info(f"Modelo carregado de: {filepath}")
            logger.info(f"Modelo treinado: {self.is_trained}, K: {self.k}")

        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise

    def predict(self, valor_total_contratado: float, model_path: str = "models/knn_model.pkl") -> Dict[str, Any]:
        try:
            if not self.is_trained or self.model is None:
                self.load_model(model_path)

            if not self.is_trained or self.model is None or self.scaler is None:
                raise ValueError("Modelo não foi carregado corretamente")

            X_input = np.array([[valor_total_contratado]])
            X_input_scaled = self.scaler.transform(X_input)

            predicted_cluster = self.model.predict(X_input_scaled)[0]

            probabilities = self.model.predict_proba(X_input_scaled)[0]
            cluster_probs = {}

            for i, prob in enumerate(probabilities):
                cluster_id = self.model.classes_[i]
                cluster_probs[int(cluster_id)] = float(prob)

            result = {
                'predicted_cluster_id': int(predicted_cluster),
                'confidence': float(max(probabilities)),
                'cluster_probabilities': cluster_probs,
                'input_value': valor_total_contratado,
                'model_info': {
                    'k_neighbors': self.k,
                    'model_loaded': True
                }
            }

            logger.info(f"Predição realizada: Cluster {predicted_cluster} para valor R$ {valor_total_contratado:,.2f}")

            return result

        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise
