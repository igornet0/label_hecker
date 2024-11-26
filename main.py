import subprocess, sys, os 
import contextlib

from Checker import Checker
from Dataset import *

# Функция для проверки и установки библиотеки
def check_and_install(package):
    try:
        __import__(package)
    except ImportError:
        # Перенаправляем стандартный вывод и стандартный поток ошибок в devnull
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                if package == "cv2":
                    package = "opencv-python"
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_labelme(label_file=None):
    command = ['labelme', '--autosave']
    if label_file:
        command.append(label_file)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return result.stderr

    return result.stdout

def main(dataset_path, args) -> None:
    from check_label import check_label_polygon

    labels = LabelsPolygon(dataset_path, round=False)
    dataset = DatasetImage(dataset_path, labels, extension="all", rotate=False)

    if len(args) >= 1:
        def filter_polyhon(polygons_dict: dict) -> str:
            if len(polygons_dict.values()) != 23:
                return "Неправильное количество полигонов"
        
        dbscan_path = args[0]

        checker = Checker(dataset, filter_polyhon, dbscan_path)
    else:
        checker = Checker(dataset, check_label_polygon)

    try:
        for path in checker.searh_error():
            run_labelme(path)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    check_and_install('matplotlib')
    check_and_install('cv2')
    check_and_install('labelme')

    skript, *args = sys.argv

    dataset_path = input("Введите путь к датасету: ")
    main(dataset_path, args)
    # main(dataset_path, args)
    # exit()
    # # Проверяем и устанавливаем библиотеку requests
    # proceses = {"labelme":  Process(target=run_labelme), "main": Process(target=main, args=(dataset_path, args, queue, queue_output))}

    # for name, process in proceses.items():
    #     process.start()

    # while True:
    #     data = queue.get()
    #     if data:
    #         data = input(">>>")
    #         if data == "exit":
    #             queue.put("exit")
    #             break
    #         queue_output.put(data)

    # for name, process in proceses.items():
    #     process.close()