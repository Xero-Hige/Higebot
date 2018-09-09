from datetime import datetime


def render_class(class_data, practica=None):
    if not class_data:
        return "ERROR"

    output = f"# Clase Numero {class_data['number']}\n\n"
    for i, topic in enumerate(class_data["topics"]):
        if practica:
            output += "[{}]\n".format(practica.get(str(i), "no asignado")).upper()
        topic = topic.replace("\t*", "\t\t\t\t\t\t*")
        output += "(Tema {:02d}) {}".format(i, topic)
    if class_data["homework"]:
        output += f"\n### Tarea ###\n\t" + class_data['homework']
    if class_data["notes"]:
        output += f"\n###Notas:###\n\t" + class_data['notes']

    return output


def load_classes():
    file = open("practicas.list")

    classes = {}

    line = file.readline()

    while line:
        while not line.rstrip().lstrip():
            line = file.readline()

        print(line)
        class_number = int(line.split("# ")[-1])

        line = file.readline()
        day, month, year = [int(x) for x in line.split("## ")[-1].split("/")]
        date = datetime(day=day, month=month, year=year)

        topics = []

        line = file.readline()
        while line[0] == "*":
            topic = line
            line = file.readline()
            while line.startswith("\t"):
                topic += line
                line = file.readline()
            topics.append(topic)

        homework = line.split("+ Tarea: ")[-1]

        line = file.readline()
        note = line.split("+ Nota de clase:")[-1].lstrip().rstrip()
        line = file.readline()
        while line and line[0] == "\t":
            note += line
            line = file.readline()

        classes[class_number] = {"number": class_number,
                                 "date": date,
                                 "topics": topics,
                                 "homework": homework,
                                 "notes": note}

    return classes
