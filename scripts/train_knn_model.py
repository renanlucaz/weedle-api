#!/usr/bin/env python3
"""
Script para treinar o modelo KNN e salvar em pickle
Este script treina o modelo com os dados disponíveis e salva o resultado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.knn import KNNClusterPredictor
import pandas as pd
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_and_save_model():
    """
    Treina o modelo KNN e salva em arquivo pickle
    """
    try:
        print("🚀 Iniciando treinamento do modelo KNN...")
        print("=" * 60)
        
        # Verificar se o arquivo de dados existe
        dataset_path = "data_exports/cliente_cluster.parquet"
        if not os.path.exists(dataset_path):
            print(f"❌ Arquivo de dados não encontrado: {dataset_path}")
            print("   Execute primeiro o script generate_training_data.py para gerar os dados")
            return False
        
        # Inicializar preditor
        print("📚 Inicializando preditor KNN...")
        predictor = KNNClusterPredictor(k=5, dataset_path=dataset_path)
        
        # Carregar e analisar dados
        print("📊 Carregando dados...")
        df = predictor.load_data()
        print(f"   ✅ Dados carregados: {len(df)} registros")
        print(f"   📋 Colunas: {list(df.columns)}")
        
        # Verificar se temos dados suficientes
        if len(df) < 10:
            print("❌ Dados insuficientes para treinamento (mínimo 10 registros)")
            return False
        
        # Preparar dados
        print("🔧 Preparando dados para treinamento...")
        X, y = predictor.prepare_data(df)
        print(f"   ✅ Features preparadas: {X.shape}")
        print(f"   ✅ Targets preparados: {y.shape}")
        
        # Verificar clusters únicos
        unique_clusters = sorted(y)
        print(f"   🏷️  Clusters encontrados: {unique_clusters}")
        
        if len(unique_clusters) < 2:
            print("❌ Necessário pelo menos 2 clusters diferentes para treinamento")
            return False
        
        # Treinar modelo
        print("🎯 Treinando modelo KNN...")
        print("   - Divisão: 80% treino, 20% teste")
        print("   - K vizinhos: 5")
        print("   - Pesos: por distância")
        
        metrics = predictor.train(test_size=0.2, random_state=42)
        
        print(f"✅ Modelo treinado com sucesso!")
        print(f"📊 Acurácia: {metrics['accuracy']:.4f}")
        print(f"📈 Tamanho do treino: {metrics['train_size']}")
        print(f"📈 Tamanho do teste: {metrics['test_size']}")
        
        # Mostrar relatório de classificação
        print("\n📈 Relatório de classificação:")
        print(metrics['classification_report'])
        
        # Criar diretório para modelos se não existir
        models_dir = "models"
        os.makedirs(models_dir, exist_ok=True)
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"knn_model_{timestamp}.pkl"
        model_path = os.path.join(models_dir, model_filename)
        
        # Salvar modelo
        print(f"💾 Salvando modelo em: {model_path}")
        predictor.save_model(model_path)
        
        # Também salvar como modelo padrão
        default_model_path = os.path.join(models_dir, "knn_model.pkl")
        predictor.save_model(default_model_path)
        print(f"💾 Modelo padrão salvo em: {default_model_path}")
        
        # Testar o modelo salvo
        print("\n🧪 Testando modelo salvo...")
        test_predictor = KNNClusterPredictor()
        test_predictor.load_model(model_path)
        
        # Fazer uma predição de teste
        test_value = 50000.0
        test_prediction = test_predictor.predict(test_value)
        
        print(f"   ✅ Teste de predição para R$ {test_value:,.2f}:")
        print(f"      - Cluster predito: {test_prediction['predicted_cluster_id']}")
        print(f"      - Confiança: {test_prediction['confidence']:.4f}")
        
        # Salvar informações do modelo
        model_info_path = os.path.join(models_dir, f"model_info_{timestamp}.txt")
        with open(model_info_path, 'w', encoding='utf-8') as f:
            f.write(f"Informações do Modelo KNN\n")
            f.write(f"=" * 40 + "\n")
            f.write(f"Data de treinamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Arquivo de dados: {dataset_path}\n")
            f.write(f"Total de registros: {len(df)}\n")
            f.write(f"K vizinhos: {predictor.k}\n")
            f.write(f"Acurácia: {metrics['accuracy']:.4f}\n")
            f.write(f"Tamanho treino: {metrics['train_size']}\n")
            f.write(f"Tamanho teste: {metrics['test_size']}\n")
            f.write(f"Clusters: {unique_clusters}\n")
            f.write(f"\nRelatório de classificação:\n")
            f.write(metrics['classification_report'])
        
        print(f"📄 Informações do modelo salvas em: {model_info_path}")
        
        print("\n" + "=" * 60)
        print("✅ Treinamento concluído com sucesso!")
        print(f"📁 Modelo salvo em: {model_path}")
        print(f"📁 Modelo padrão: {default_model_path}")
        print(f"📄 Informações: {model_info_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o treinamento: {str(e)}")
        return False

def main():
    """
    Função principal
    """
    print("🤖 Treinamento do Modelo KNN")
    print("=" * 60)
    
    success = train_and_save_model()
    
    if success:
        print("\n🎉 Modelo treinado e salvo com sucesso!")
        print("\n📋 Próximos passos:")
        print("   1. O modelo está pronto para uso via API")
        print("   2. Execute 'python scripts/test_knn.py' para testar")
        print("   3. Use os endpoints /knn/* na API")
        return 0
    else:
        print("\n💥 Falha no treinamento do modelo!")
        return 1

if __name__ == "__main__":
    exit(main())
