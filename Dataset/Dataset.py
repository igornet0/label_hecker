import random
from os import listdir, walk
from os.path import join, isdir
from typing import Union, Iterable
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from .Label import *
from .Labels import *
from .Data import *

class Dataset:

    def __init__(self, data: Union[str, Iterable], labels: Labels = None, output_shape: int = None, 
                 test_size: float = 0.2):

        """
        :param data: Path to the folder containing the data or a list of data
        :param labels: Path to the folder containing the labels or a list of labels
        :param output_shape: Shape of the output data
        :param test_size: float indicating the proportion of the data to be used for testing
        """
        
        if not isinstance(labels, Labels):
            labels = Labels(labels, output_shape=output_shape)

        self.data = Data(data)
        self.labels = labels
        self.test_size = test_size

    
    def get_data(self) -> iter:
        return self.data


    def get_label(self, data: Data) -> Label:
        return self.labels[data]


    def get_data_label(self) -> iter:
        if self.labels.get_labels() is None:
            raise ValueError("Labels not found")

        for data in self.get_data():

            label = self.get_label(data)

            if not label.get():
                continue

            yield data, label
            

    def get_bath(self, batch_size: int = 32, shuffle: bool = True) -> iter:
        bath = []
        
        for data in self:
            bath.append(data)
            if len(bath) == batch_size:
                if shuffle:
                    random.shuffle(bath)
                yield bath
                bath = []

        return bath if not shuffle else random.shuffle(bath)
    
    def get_loader(self):
        if self.labels.get_labels() is not None:
            dataset = self.get_data_label()
        else:
            dataset = self.get_data()
        
        for data in dataset:
            yield data

    def __iter__(self) -> iter:
        yield from self.get_loader()

    def __len__(self):
        return len(self.data)
    

    @property
    def shape(self):
        return self.data.shape


class DatasetImage(Dataset):

    def __init__(self, data_path: str, labels: Labels = None, 
                 extension: Union[str, set] = ".png", 
                 desired_size: tuple = (), rotate: bool = False,
                 shuffle_path: bool = False, test_size: float = 0.2):

        if not os.path.exists(data_path):
            raise ValueError("Path data not found")
        
        super().__init__(data=None, labels=labels, output_shape=desired_size, test_size=test_size)

        self.data_path = data_path

        self.set_desired_size(desired_size)
        self.set_extension(extension)
        self.set_rotate(rotate)
        self.set_shuffle_path(shuffle_path)

    def set_desired_size(self, desired_size: tuple):
        if not isinstance(desired_size, tuple):
            raise ValueError("desired_size must be a tuple")
        
        self.desired_size = desired_size
    
    def set_extension(self, extension):
        if extension == 'all':
            extension = {".jpg", ".png", ".jpeg"}

        self.extension = {extension} if isinstance(extension, str) else set(extension)

    def set_rotate(self, rotate: bool):
        if not isinstance(rotate, bool):
            raise ValueError("rotate must be a boolean")
        
        self.rotate = rotate
    
    def set_shuffle_path(self, shuffle_path: bool):
        if not isinstance(shuffle_path, bool):
            raise ValueError("shuffle_path must be a boolean")
        
        self.shuffle_path = shuffle_path

    def get_shuffle_path(self):
        return self.shuffle_path
    
    def get_images(self, path: str = None) -> iter:

        if path is not None:
            if not isdir(path):
                raise ValueError(f"Path {path} is not a directory")
            path = path
        else:
            path = self.data_path

        for root, _, files in walk(path):
            for file in files:
                if not any(file.endswith(ext) for ext in self.extension):
                    continue

                yield Image(join(root, file), desired_size=self.desired_size)

    def get_path_images(self):
        for path_data in listdir(self.data_path):
            
            yield join(self.data_path, path_data)

    def get_data_from_path_shuffle(self) -> iter:
        buffer_path = {path_file: self.get_images(path_file) for path_file in self.get_path_images()}
        while buffer_path:
            for path_file, images in buffer_path.items():
                try:
                    image = next(images)
                except StopIteration:
                    buffer_path.pop(path_file)
                    break

                yield image

    def get_data(self):
        if self.get_shuffle_path():
            dataset = self.get_data_from_path_shuffle()
        else:
            dataset = self.get_images()

        for data in dataset:
            if self.rotate:
                for _ in range(4):
                    data.rotate()
                    yield data
            else:
                yield data

    def get_output_shape(self):
        return self.desired_size
    
    def get_col_files(self):
        if not self.labels is None and isinstance(self.labels, LabelsFile):
            return sum([len(list(filter(lambda file: file.endswith(self.labels.get_extension()), files))) for _, _, files in walk(self.data_path)])
        
        return sum([len(list(filter(lambda file: any(file.endswith(ext) for ext in self.extension), files))) for _, _, files in walk(self.data_path)])
        
    def __len__(self):
        col  = self.get_col_files()
        if self.rotate:
            col *= 4
        
        return col
    
    @staticmethod
    def show_img(image, label=None, polygons_dict = None):
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(image)
        
        # Случайные цвета для каждого полигона
        random.seed(42)
        colors = [
            (random.random(), random.random(), random.random())
            for _ in range(len(polygons_dict))
        ]
        
        # Рисуем полигоны
        for i, (polygon_name, coordinates) in enumerate(polygons_dict.items()):
            # Получаем координаты вершин полигона
            x_coords = coordinates[::2]
            y_coords = coordinates[1::2]
            
            # Добавляем полигон на график
            polygon = patches.Polygon(
                xy=list(zip(x_coords, y_coords)),
                closed=True,
                edgecolor='black',
                facecolor=colors[i],
                alpha=0.5
            )
            ax.add_patch(polygon)
            
            # Выводим номер полигона
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            ax.text(
                center_x, center_y, f"{polygon_name}",
                color="black", fontsize=12, ha="center", va="center",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
            )
        
        # Настраиваем отображение
        ax.set_title("Визуализация полигонов")
        ax.axis("off")
        plt.show()
        
    @property
    def shape(self):
        return self.desired_size