from app.cliGui import GUI
from app.gui import App
from app.helpers.input_helpers import determine_from_ls

# opt = determine_from_ls(['cli','dash'],labels=['command-line-gui','dash-gui'])

run_cli=False
# if opt == 'cli':
#     run_cli=True

if run_cli:
    gui = GUI()
else:
    gui = App()

print('Thanks for using BudgetTool.py')