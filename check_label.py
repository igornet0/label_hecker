from Dataset import *
from typing import Union

def check_label_polygon(labelP: Union[Image, LabelP]):

    label_buffer = []
    message_error = ""

    if isinstance(labelP, Image):
        message_error += f"\terror NOT POLYGONS\n"
        return message_error

    for label_name, polygon in labelP.get().items():
        label_buffer.append(label_name)

        if len(polygon) != 8:
            message_error += f"\terror POLYGON label: {label_name}\n"

        if not label_name.isdigit() and label_name != "object":
            message_error += f"\terror NAME label: {label_name}\n"
    
    if not "object" in label_buffer:
        message_error += "\terror NOT label: object\n"

    return message_error

