import numpy as np
import multiprocessing as mp

from .model import Dataset as ds_db
from Dataset import DatasetImage, Image, LabelP
from Checker.dbscan import dbscan_load, dbscan_clustering_polygon


class Checker:

    def __init__(self, dataset: DatasetImage, filter, path_dbscan=None) -> None:
        self.dataset = dataset
        self.filter = filter
        
        self.error_count, self.files_count = self.count_error_multi()
        ds_db(dataset.data_path, self.files_count, self.error_count)

        self.dbscan = dbscan_load(path_dbscan) if path_dbscan else None

    @property
    def use_dbscan(self, path):
        self.dbscan = dbscan_load(path)

    def check_dbscan(self, show=False):
        print("Checking model DBSCAN...")
        try:
            for data, labelP in self.dataset:
                if labelP is None:
                    continue

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

                while True:
                    yield f"{labelP.path_data}\{labelP.name_file}.json"
                    
                    labelP_new = LabelP(f"{labelP.path_data}\{labelP.name_file}.json")

                    result = self.filter(labelP_new)
                    if result:
                        print("Error in new file")
                        self.print_error(result)
                    else:
                        break

                self.error_count -= 1
        except KeyboardInterrupt:
            pass

        ds_db(self.dataset.data_path, self.files_count, self.error_count)

        print("Checking model DBSCAN finished")
                

    def print_error(self, message):
        print(message)
        print()

    def count_error(self, path=None):
        if path:
            dataset = self.dataset.get_data_label(path)
        else:
            dataset = self.dataset

        count = 0
        count_file = 0
        for image, labelP in dataset:
            count_file += 1
            if labelP is None:
                labelP = image
            result = self.filter(labelP)
            if result:
                count += 1
        return count, count_file


    def count_error_multi(self):
        count = 0
        count_file = 0
        paths = list(self.dataset.get_path_images())
        
        results = self.dataset.create_process(count_process=len(paths), func=self.count_error, args=paths)

        for result in results:
            count_file += result[1]
            count += result[0]

        return count, count_file

    def searh_error(self):
        
        if self.dbscan:
            yield from self.check_dbscan()
        
        print("Search errors...")
        try:
            for image, labelP in self.dataset:
                if labelP is None:
                    labelP = image
                result = self.filter(labelP)

                if result:
                    self.print_error(result)
                else:
                    continue

                while True:
                    if isinstance(labelP, Image):
                        yield f"{labelP.path_data}\{labelP.name_file}.png"
                    if isinstance(labelP, LabelP):
                        yield f"{labelP.path_data}\{labelP.name_file}.json"
                    
                    labelP_new = LabelP(f"{labelP.path_data}\{labelP.name_file}.json")

                    result = self.filter(labelP_new)
                    if result:
                        print("Error in new file")
                        self.print_error(result)
                    else:
                        break

                self.error_count -= 1

        except KeyboardInterrupt:
            pass

        ds_db(self.dataset.data_path, self.files_count, self.error_count)

        print("Search errors finished")