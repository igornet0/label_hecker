import numpy as np

from Dataset import DatasetImage
from dbscan import dbscan_load, dbscan_clustering_polygon


class Checker:

    def __init__(self, dataset, filter, path_dbscan=None) -> None:
        self.dataset = dataset

        self.filter = filter
        self.dbscan = dbscan_load(path_dbscan) if path_dbscan else None

    @property
    def use_dbscan(self, path):
        self.dbscan = dbscan_load(path)

    def check_dbscan(self, show=False):
        print("Проверка модели DBSCAN...")

        for data, labelP in self.dataset:

            polygons = [x for x in labelP.get().values() if len(x) == 8 and x != "object"]
            polygons = np.array(polygons)

            polygons_dict = dbscan_clustering_polygon(polygons, self.dbscan)

            result = self.filter(polygons_dict)

            if result:
                path_message = f"path: {labelP.path_data} \n\tname_file: {labelP.name_file}\n"
                self.print_error(path_message + result)
            else:
                continue

            if show:
                DatasetImage.show_img(data.get_image(), polygons_dict=polygons_dict)

            yield f"{labelP.path_data}\{labelP.name_file}.json"
        
        print("Проверка модели DBSCAN завершена")
                

    def print_error(self, message):
        print(message)
        print()

    def searh_error(self):
        
        if self.dbscan:
            yield from self.check_dbscan()
        
        print("Поиск ошибок...")
        for _, labelP in self.dataset:

            result = self.filter(labelP)

            if result:
                self.print_error(result)
            else:
                continue

            yield f"{labelP.path_data}\{labelP.name_file}.json"

        print("Поиск ошибок завершен")