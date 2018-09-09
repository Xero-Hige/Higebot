import os


def get_mailbox_data():
    return "Anotate bien esto:\n" + (
        "*Algoritmos 1* \n"
        "> • {} \n"
        "> • {} \n"
        "*Algoritmos 2* \n"
        "> • {} \n"
        "> • {} \n"
    ).format(
            os.environ.get('CASILLA_TPS_ALGO1', ''),
            os.environ.get('PASS_CASILLA_ALGO1', ''),
            os.environ.get('CASILLA_TPS_ALGO2', ''),
            os.environ.get('PASS_CASILLA_ALGO2', '')
    )
