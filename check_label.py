from Dataset import *

def check_label_polygon(labelP: LabelP):

    label_buffer = []
    message_error = ""

    for label_name, polygon in labelP.get().items():
        label_buffer.append(label_name)

        if len(polygon) != 8:
            message_error += f"\terror POLYGON label: {label_name}\n"

        if not label_name.isdigit():
            message_error += f"\terror NAME label: {label_name}\n"
    
    if not "object" in label_buffer:
        message_error += "\terror NOT label: object\n"

    return message_error

