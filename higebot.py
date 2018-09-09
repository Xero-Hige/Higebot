import json
import time

from slackclient import SlackClient

from commands import *
from parse_class import *

DEBUG = False

AT_BOT = "<@" + os.environ.get('BOT_ID', "").upper() + ">"
slack_client = SlackClient(os.environ.get('BOT_TOKEN', ""))

CLASSES = {}
string_responses = {"che": lambda: "Au?",
                    "que hay que dar hoy?": lambda: "Eh... da lo que quieras, hoy no hay clases",
                    "que hay que dar hoy": lambda: "Eh... da lo que quieras, hoy no hay clases",
                    }

commands = {"\\casillas": get_mailbox_data}

asignaciones = {}

people = {
    AT_BOT: "General"
}


def store_assignments():
    with open("asignment.json", "w") as output:
        output.write(json.dumps(asignaciones))


def load_assignments():
    with open("asignment.json") as input_file:
        global asignaciones
        asignaciones = json.loads(input_file.read())


def delete_from_plan(command):
    if len(command) < 5:
        return "ERROR"

    print(asignaciones)
    name = command[0].lstrip().rstrip()
    data_a = command[1:3]
    data_b = command[3:5]

    if data_a[0] == "clase" and data_b[0] == "tema":
        class_number = str(int(data_a[1]))
        topic_number = str(int(data_b[1]))
    elif data_b[0] == "clase" and data_a[0] == "tema":
        class_number = str(int(data_a[1]))
        topic_number = str(int(data_b[1]))
    else:
        return "ERROR"

    practica = command[5]

    class_assigns = asignaciones[practica].get(class_number, {})
    asignaciones[practica][class_number] = class_assigns

    old = class_assigns.get(topic_number)
    if old == name:
        class_assigns.pop(topic_number)
        store_assignments()
        return "OK"
    elif old:
        return "Deja de querer robar temas. Ese lo tiene " + old.upper() + " no " + name
    else:
        return "Nadie nunca jamas quiso dar eso"


def add_to_plan(command):
    if len(command) < 5:
        return "ERROR"

    name = command[0].lstrip().rstrip()
    data_a = command[1:3]
    data_b = command[3:5]

    if data_a[0] == "clase" and data_b[0] == "tema":
        class_number = str(int(data_a[1]))
        topic_number = str(int(data_b[1]))
    elif data_b[0] == "clase" and data_a[0] == "tema":
        class_number = str(int(data_a[1]))
        topic_number = str(int(data_b[1]))
    else:
        return "ERROR"

    practica = command[5]

    class_assigns = asignaciones[practica].get(class_number, {})
    asignaciones[practica][class_number] = class_assigns

    old = class_assigns.get(topic_number)
    if not old:
        class_assigns[topic_number] = name
        store_assignments()
        return "OK"
    else:
        return old.upper() + "ya tomo ese tema"


def show(command):
    if not command:
        return "No se que esperas que pase si no pasas nada"

    if command[0].lower() == "clase":
        return render_plan(command[1:])

    else:
        return "No se que queres que muestre... ¬¬"


complex = {
    "agrega": add_to_plan,
    "mostrame": show,
    "saca": delete_from_plan
}


def render_plan(command):
    if not command or len(command) < 2:
        return "ERROR"

    if command[0].lower() == "numero":
        class_number = int(command[1])
        if len(command) > 2 and command[2] in ["alan", "barbara", "grace"]:
            print(CLASSES)
            return render_class(CLASSES.get(class_number), asignaciones.get(command[2], {}).get(str(class_number)))
        return render_class(CLASSES.get(class_number, {}))


def react_response(reaction_name, channel, ts):
    response = slack_client.api_call("reactions.add", channel=channel, name=reaction_name, timestamp=ts)
    if DEBUG:
        print(response)


def send_response(response, channel):
    response = slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if DEBUG:
        print(response)


def execute_complex_commad(command_list):
    for commad_slice in command_list:
        if "anime" == commad_slice.lower():
            return "OK"

    return complex.get(command_list[0].lower(), lambda x: "ERROR")(command_list[1:])


connectors = set(["a", "de", "la", "del", "al", ""])


def is_connector(string):
    return string.lower() in connectors


def is_someone(name):
    return name.lower() in people


def handle_mention(command, channel, ts):
    if not has_someone(" ".join(command)):
        return

    command_list = [x.lower() for x in command if x != AT_BOT and not is_connector(x)]
    command_string = " ".join(
            [x for x in command_list if not is_someone(x) and AT_BOT not in x]).lower().rstrip().lstrip()

    response = string_responses.get(command_string, lambda: "")()
    if response:
        send_response(response, channel)
        return

    response = execute_complex_commad([x for x in command_list if x not in people])

    if response not in ("OK", "ERROR", ""):
        send_response(response, channel)
        return

    if response == "OK":
        react_response("thumbsup", channel, ts)
        return

    if AT_BOT in command:
        send_response("Paso 1: Aprende a escribir\n Paso 2: Profit\n(Posta no se que queres)", channel)
        if response == "ERROR":
            react_response("thumbsdown", channel, ts)


def handle_command(command, channel):
    response = commands.get(command.lower(), lambda: "")()

    if response:
        send_response(response, channel)
        return


def has_someone(text):
    text = text.lower().split(" ")
    for person in people:
        if person.lower() in text:
            return people[person]
    return ""


def is_command(text):
    return text.startswith("\\")


def parse_slack_output(slack_rtm_output):
    if DEBUG:
        print("DEBUG: " + slack_rtm_output)
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                if DEBUG:
                    print(f"DEBUG: " + output['text'])
                if has_someone(output['text']):
                    return "mention", output['text'].split(' '), output['channel'], output['event_ts']
                elif is_command(output['text']):
                    return "command", output['text'], output['channel'], output['event_ts']
                elif output['text'].lower() in string_responses:
                    return "mention", output['text'].split(' '), output['channel'], output['event_ts']
    return None, None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    # 1 second delay between reading from firehose
    load_assignments()
    CLASSES = load_classes()
    if slack_client.rtm_connect():
        print("HigeBot connected and running!")
        while True:
            try:
                type, command, channel, ts = parse_slack_output(slack_client.rtm_read())
            except Exception as e:
                print(e)
                # Hasta encontrar una mejor solución, queda esto.
                time.sleep(READ_WEBSOCKET_DELAY)
                slack_client.rtm_connect()
            try:
                if not type:
                    time.sleep(READ_WEBSOCKET_DELAY)
                    continue
                if type == "mention":
                    handle_mention(command, channel, ts)
                    continue
                handle_command(command, channel)
            except Exception as e:
                react_response("skull_and_crossbones", channel, ts)
                print("Exception : ", e)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
