
from Dataset import *

def check_label_polygon(label: LabelP):
    print(label.path_data)

def filer_polygon(label: LabelP):
    # if not label.get():
    #     return False
    
    for label_name, polygon in label.get().items():
        if len(polygon) > 8 or len(polygon) < 4:
            # print("error", label_name, polygon, label.path_data, label.name_file)
            return False
    return True

def inpuct_polygon(label: LabelP):

    return label

    for label_name, polygon in label.get().items():
        new_polygon = []
        for i in range(0, len(polygon), 2):
            new_polygon.append([polygon[i], polygon[i+1]])

        label.set_polygon(label_name, new_polygon)

    return label

def check_label_polygon(path_dataset: str):
    labels = LabelsPolygon(path_dataset, round=False)
    dataset = DatasetImage(path_dataset, labels, extension="all", rotate=False)
    print("Поиск ошибок")
    for _, labelP in dataset:
        flag = False
        for label_name, polygon in labelP.get().items():
            if len(polygon) != 8:
                if not flag:
                    print(f"path: {labelP.path_data} \n\tname_file: {labelP.name_file}")
                flag = True
                print(f"\t error POLYGON label: {label_name}")
            if not label_name.isdigit():
                if not flag:
                    print(f"path: {labelP.path_data} \n\tname_file: {labelP.name_file}")
                flag = True
                print(f"\t error NAME label: {label_name}")
        if not flag:
            continue
        print()
        yield f"{labelP.path_data}\{labelP.name_file}.json"