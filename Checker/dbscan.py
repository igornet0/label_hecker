import numpy as np
from sklearn.cluster import DBSCAN
from joblib import dump, load
import matplotlib.pyplot as plt
from Dataset import *

def calculate_center(polygon):
    x_coords = polygon[::2]  # x-координаты
    y_coords = polygon[1::2]  # y-координаты
    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)
    return center_x, center_y

def calculate_area(polygon):
    x_coords = polygon[::2]
    y_coords = polygon[1::2]
    # Формула площади многоугольника через координаты
    area = 0.5 * abs(
        sum(x_coords[i] * y_coords[(i + 1) % len(y_coords)] for i in range(len(x_coords)))
        - sum(y_coords[i] * x_coords[(i + 1) % len(x_coords)] for i in range(len(y_coords)))
    )
    return area

def fit_dbscan_clustering(polygons, dbscan=None, save=False, show=False):
    if not isinstance(polygons, np.ndarray):
        polygons = np.array(polygons)

    # Преобразование данных в формат (количество точек * количество координат)
    # Мы будем использовать только координаты для кластеризации
    X = polygons.copy()

    # Параметры DBSCAN
    eps = 5  # Максимальное расстояние между двумя образцами для того, чтобы они считались в одном кластере.
    min_samples = 1  # Минимальное количество образцов (точек) в окрестности точки для того, чтобы она считалась ядром кластера.

    if dbscan is None:
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
        # Обучение модели и получение меток кластеров
    
    labels = dbscan.fit_predict(X)

    if show:
        # Визуализация кластеров
        plt.figure(figsize=(8, 6))
        for label in set(labels):
            cluster_points = polygons[labels == label]

            if label == -1:
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], c='red', label='Noise', marker='x')
            else:
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {label}')

        plt.title("Кластеры полигонов (DBSCAN)")
        plt.xlabel("X (Центр)")
        plt.ylabel("Y (Центр)")
        plt.legend()
        plt.show()

    if save:
        print("Сохранение модели...")
        dump(dbscan, 'dbscan.joblib')

    return dbscan

def dbscan_load(path: str):
    return load(path)

def dbscan_clustering_polygon(X, dbscan) -> dict:

    labels = dbscan.fit_predict(X)

    polygons_dict = {labels[i]: polygon for i, polygon in enumerate(X)}

    return polygons_dict

def main(path_dataset: str):
    labels = LabelsPolygon(path_dataset, round=False)
    dataset = DatasetImage(path_dataset, labels, extension="all", rotate=False)
    
    polygons = []
    dbscan = None
    n = 20

    for _, labelP in dataset:

        for label, polygon in labelP.get().items():
            if len(polygon) != 8 or label == "object":
                continue
            
            center_x, center_y = calculate_center(polygon)
            area = calculate_area(polygon)

            polygons.append([center_x, center_y, area])

            if len(polygons) % 100 == 0:
                print(f"{abs(n-10) + 1} Обработано полигонов: ", len(polygons))
                dbscan = fit_dbscan_clustering(polygons, dbscan, 
                                           save=False, show=False)

                n -= 1

        if n == 0:
            break
     
    # print("Количество полигонов: ", len(polygons))
    fit_dbscan_clustering(polygons, save=True)

    for data, label in dataset:

        polygons = [x for x in label.get().values() if len(x) == 8 and x != "object"]
        polygons = np.array(polygons)

        labels = dbscan_clustering_polygon(polygons, data.get_image(), dbscan)
        if len(labels) != len(polygons):
            yield 

if __name__ == "__main__":
    dataset_path = input("Введите путь к датасету: ")
    main(dataset_path)