# -*- coding: utf-8 -*-
"""Лабораторная работа №3: Анализ социального графа и эмбеддинг узлов
   Версия для Google Colab (без karateclub и sklearn_extra)
"""

# Установка gensim (легко устанавливается)

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
from gensim.models import Word2Vec
from sklearn.cluster import DBSCAN, AffinityPropagation, KMeans
from sklearn.metrics import silhouette_score, adjusted_mutual_info_score, adjusted_rand_score
from sklearn.metrics.pairwise import cosine_distances
from sklearn.decomposition import PCA
from networkx.algorithms.community import greedy_modularity_communities, modularity

print("✅ Библиотеки загружены.")

# ===========================================================================
# 1. ЗАГРУЗКА ГРАФА
# ===========================================================================
file_path = 'facebook_combined.txt'
try:
    G = nx.read_edgelist(file_path, nodetype=int)
    print(f"Граф загружен: {G.number_of_nodes()} узлов, {G.number_of_edges()} рёбер")
except FileNotFoundError:
    print("Ошибка: файл 'facebook_combined.txt' не найден. Загрузите его в текущую папку Colab.")
    exit()

# ===========================================================================
# 4.1 Базовый анализ графа
# ===========================================================================
print("\n" + "="*60)
print("4.1 БАЗОВЫЙ АНАЛИЗ ГРАФА")
print("="*60)

num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
density = nx.density(G)
avg_degree = 2 * num_edges / num_nodes
print(f"Количество узлов: {num_nodes}")
print(f"Количество рёбер: {num_edges}")
print(f"Плотность графа: {density:.4f}")
print(f"Средняя степень вершины: {avg_degree:.2f}")

# Диаметр наибольшей связной компоненты
largest_cc = max(nx.connected_components(G), key=len)
print(f"Наибольшая связная компонента содержит {len(largest_cc)} узлов.")
if len(largest_cc) < 2000:
    diam = nx.diameter(G.subgraph(largest_cc))
    print(f"Диаметр наибольшей связной компоненты: {diam}")
else:
    print("Диаметр не вычислен (компонента слишком большая).")

# Метрики центральности и PageRank
print("Вычисление метрик центральности... (может занять время)")
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
pagerank = nx.pagerank(G, alpha=0.85)

top5_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
print("Топ-5 узлов по PageRank:")
for i, (node, pr) in enumerate(top5_pr, 1):
    print(f"  {i}. Узел {node}: {pr:.6f}")

# ===========================================================================
# 4.2 Выявление сообществ
# ===========================================================================
print("\n" + "="*60)
print("4.2 ВЫЯВЛЕНИЕ СООБЩЕСТВ")
print("="*60)

communities = list(greedy_modularity_communities(G))
mod_score = modularity(G, communities)
print(f"Количество сообществ: {len(communities)}")
print(f"Значение модульности: {mod_score:.4f}")

# Визуализация графа с раскраской по сообществам (упрощённая)
plt.figure(figsize=(12, 12))
node_to_com = {node: i for i, com in enumerate(communities) for node in com}
pos = nx.spring_layout(G, k=0.05, iterations=20)
nx.draw_networkx_nodes(G, pos, node_color=list(node_to_com.values()), cmap=plt.cm.Set3, node_size=10)
nx.draw_networkx_edges(G, pos, alpha=0.05)
plt.title("Граф Facebook с раскраской по сообществам")
plt.axis('off')
plt.show()

# ===========================================================================
# 4.3 Эмбеддинг узлов графа (DeepWalk, ручная реализация)
# ===========================================================================
print("\n" + "="*60)
print("4.3 ЭМБЕДДИНГ УЗЛОВ ГРАФА (DeepWalk)")
print("="*60)

def generate_random_walks(G, num_walks=10, walk_length=80):
    walks = []
    nodes = list(G.nodes())
    for _ in range(num_walks):
        random.shuffle(nodes)
        for node in nodes:
            walk = [node]
            cur = node
            for _ in range(walk_length - 1):
                neighbors = list(G.neighbors(cur))
                if not neighbors:
                    break
                cur = random.choice(neighbors)
                walk.append(cur)
            walks.append([str(w) for w in walk])
    return walks

print("Генерация случайных блужданий...")
walks = generate_random_walks(G, num_walks=10, walk_length=80)
print("Обучение Word2Vec...")
model_w2v = Word2Vec(walks, vector_size=128, window=10, min_count=1, workers=4, epochs=10)
nodes = list(G.nodes())
embeddings = np.array([model_w2v.wv[str(node)] for node in nodes])
print(f"Размерность вектора: {embeddings.shape[1]}")
print(f"Форма матрицы эмбеддингов: {embeddings.shape}")

# ===========================================================================
# 4.4 Визуализация эмбеддингов (PCA)
# ===========================================================================
print("\n" + "="*60)
print("4.4 ВИЗУАЛИЗАЦИЯ ЭМБЕДДИНГОВ С ПОМОЩЬЮ PCA")
print("="*60)

pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)
plt.figure(figsize=(10, 8))
plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], s=5, alpha=0.6)
plt.title("Визуализация эмбеддингов узлов (PCA, 2 компоненты)")
plt.xlabel("Первая главная компонента")
plt.ylabel("Вторая главная компонента")
plt.show()

# ===========================================================================
# 4.5 Поиск наиболее схожих узлов
# ===========================================================================
print("\n" + "="*60)
print("4.5 ПОИСК НАИБОЛЕЕ СХОЖИХ УЗЛОВ")
print("="*60)

target_node = max(pagerank, key=pagerank.get)
target_idx = nodes.index(target_node)
distances = cosine_distances(embeddings[target_idx].reshape(1, -1), embeddings)[0]
sorted_idx = np.argsort(distances)[1:4]  # пропускаем сам узел
similar_nodes = [nodes[i] for i in sorted_idx]
print(f"Узел с максимальным PageRank: {target_node}")
print(f"3 наиболее схожих узла: {similar_nodes}")

# ===========================================================================
# 4.6 Кластеризация эмбеддингов
# ===========================================================================
print("\n" + "="*60)
print("4.6 КЛАСТЕРИЗАЦИЯ ЭМБЕДДИНГОВ")
print("="*60)

clustering_results = {}

# DBSCAN
print("\n--- DBSCAN ---")
dbscan = DBSCAN(eps=0.5, min_samples=5, metric='cosine')
labels_db = dbscan.fit_predict(embeddings)
n_clusters_db = len(set(labels_db)) - (1 if -1 in labels_db else 0)
n_noise = list(labels_db).count(-1)
print(f"Количество кластеров: {n_clusters_db}")
print(f"Количество шумовых точек: {n_noise}")
if n_clusters_db > 1:
    sil_db = silhouette_score(embeddings, labels_db, metric='cosine')
    print(f"Коэффициент силуэта: {sil_db:.4f}")
else:
    sil_db = -1
clustering_results['DBSCAN'] = {'labels': labels_db, 'n_clusters': n_clusters_db, 'silhouette': sil_db}

# Affinity Propagation
print("\n--- Affinity Propagation ---")
ap = AffinityPropagation(random_state=42)
labels_ap = ap.fit_predict(embeddings)
n_clusters_ap = len(set(labels_ap))
print(f"Количество кластеров: {n_clusters_ap}")
if n_clusters_ap > 1:
    sil_ap = silhouette_score(embeddings, labels_ap, metric='cosine')
    print(f"Коэффициент силуэта: {sil_ap:.4f}")
else:
    sil_ap = -1
clustering_results['Affinity Propagation'] = {'labels': labels_ap, 'n_clusters': n_clusters_ap, 'silhouette': sil_ap}

# K-Means (вместо KMedoids)
print("\n--- K-Means ---")
best_k = 2
best_sil = -1
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels_km = km.fit_predict(embeddings)
    if len(set(labels_km)) > 1:
        sil = silhouette_score(embeddings, labels_km, metric='cosine')
        print(f"k = {k}: силуэт = {sil:.4f}")
        if sil > best_sil:
            best_sil = sil
            best_k = k
    else:
        print(f"k = {k}: только один кластер")
print(f"Оптимальное число кластеров: k = {best_k} (силуэт = {best_sil:.4f})")
km_final = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
labels_km = km_final.fit_predict(embeddings)
clustering_results['K-Means'] = {'labels': labels_km, 'n_clusters': best_k, 'silhouette': best_sil}

# ===========================================================================
# 4.7 Сравнение методов кластеризации (AMI, ARI)
# ===========================================================================
print("\n" + "="*60)
print("4.7 СРАВНЕНИЕ МЕТОДОВ КЛАСТЕРИЗАЦИИ (AMI, ARI)")
print("="*60)

labels_db = clustering_results['DBSCAN']['labels']
labels_ap = clustering_results['Affinity Propagation']['labels']
labels_km = clustering_results['K-Means']['labels']

ami_db_ap = adjusted_mutual_info_score(labels_db, labels_ap)
ari_db_ap = adjusted_rand_score(labels_db, labels_ap)
ami_db_km = adjusted_mutual_info_score(labels_db, labels_km)
ari_db_km = adjusted_rand_score(labels_db, labels_km)
ami_ap_km = adjusted_mutual_info_score(labels_ap, labels_km)
ari_ap_km = adjusted_rand_score(labels_ap, labels_km)

print("Сравнение DBSCAN и Affinity Propagation:")
print(f"  AMI = {ami_db_ap:.4f}, ARI = {ari_db_ap:.4f}")
print("Сравнение DBSCAN и K-Means:")
print(f"  AMI = {ami_db_km:.4f}, ARI = {ari_db_km:.4f}")
print("Сравнение Affinity Propagation и K-Means:")
print(f"  AMI = {ami_ap_km:.4f}, ARI = {ari_ap_km:.4f}")

# Определение наиболее схожих методов
pairs = {
    "DBSCAN & Affinity Propagation": (ami_db_ap, ari_db_ap),
    "DBSCAN & K-Means": (ami_db_km, ari_db_km),
    "Affinity Propagation & K-Means": (ami_ap_km, ari_ap_km)
}
best_ami = max(pairs, key=lambda x: pairs[x][0])
best_ari = max(pairs, key=lambda x: pairs[x][1])
print(f"\nНаиболее схожи по AMI: {best_ami} (значение: {pairs[best_ami][0]:.4f})")
print(f"Наиболее схожи по ARI: {best_ari} (значение: {pairs[best_ari][1]:.4f})")

print("\n✅ Лабораторная работа №3 успешно выполнена.")