import os


def get_mailbox_data():
    return "Anotate bien esto:\n" + (
        "*Algoritmos 1* \n"
        f"> • {os.environ.get('CASILLA_TPS_ALGO1', '')} \n"
        f"> • {os.environ.get('PASS_CASILLA_ALGO1', '')} \n"
        "*Algoritmos 2* \n"
        f"> • {os.environ.get('CASILLA_TPS_ALGO2', '')} \n"
        f"> • {os.environ.get('PASS_CASILLA_ALGO2', '')} \n"
    )
