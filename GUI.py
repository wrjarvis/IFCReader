from PySimpleGUI import Window, WIN_CLOSED, Input, FileBrowse, Button, Output, Text, FileSaveAs
from IFCReader import IfcFile
from IFCPropertiesToExcel import create_excel_dict


def create_readme_window():
    layout = [[Text("README", font='Any 25')],
              [Text("Program created by Will Jarvis(wr.jarvis@atkinsglobal.com)")],
              [Text("Version 0.1 - ALPHA")]]
    window = Window('IFC Editing Suite - README', layout, size=(450, 200))
    while True:
        event, values = window.read()
        if event == WIN_CLOSED or event == "Exit":
            break


def create_ede_read_window():
    layout = [[Text("Elastic Data Environment", font='Any 25')],
              [Text("The Elastic Data Environment (EDE) was created as an intuitive")],
              [Text("database solution to store all project data. By building links")],
              [Text("between data and deliverables, the project can be quickly")],
              [Text("navigated by users.")],
              [Text("The IFC editing suite was developed with the EDE being front and")],
              [Text("centre of tool. Linking to an EDE allows direct access into the")],
              [Text("database")],
              [Text("For more information please contact one of the following:")],
              [Text("    -Will Jarvis")],
              [Text("    -Sam Jamaa")],
              [Text("    -Steve Burton")],
              [Text("    -Rob McDougall")]]
    window = Window('IFC Editing Suite - EDE Guide', layout, size=(420, 380))
    while True:
        event, values = window.read()
        if event == WIN_CLOSED or event == "Exit":
            break


def create_ede_window():
    layout = [[Text("Link to EDE", font='Any 25')],
              [Text("Server:"), Input(key='Server')],
              [Text("Database:"), Input(key='Server')],
              [Button("Connect")]]
    window = Window('IFC Editing Suite - Link to EDE', layout, size=(320, 150))
    while True:
        event, values = window.read()
        if event == WIN_CLOSED or event == "Exit":
            break
        elif event == "Connect":
            print("ERROR: Unable to connect to database")
            print("Please contact an EDE contact to assist with setup")


def main_window():

    ifc_data = None

    layout = [[Text("IFC Editing Tool", font='Any 25')],
              [Text("Version 0.1 - ALPHA")],
              [Button("README")],
              [Text("")],
              [Text("Choose an IFC File: "), Input(), FileBrowse(key='Input IFC')],
              [Text("Choose a Output Excel File: "), FileSaveAs(key='Excel File', file_types=(('Excel', '.xlsx'),))],
              [Button("Read IFC"), Button("Save Properties")],
              [Output(size=(70, 15))],
              [Button("Link to EDE"), Button("Find Out More")]]

    window = Window('IFC Editing Tool', layout, size=(550, 500))

    while True:
        event, values = window.read()
        if event == WIN_CLOSED or event == 'Exit':
            break
        elif event == 'Read IFC':
            ifc_filename = values['Input IFC']
            print('Processing IFC: ' + ifc_filename)
            if ifc_filename[-4:] == '.ifc':
                ifc_data = IfcFile(ifc_filename, 'IFC2X3_TC1.exp')
                print('Read IFC COMPLETE')
            else:
                print('ERROR: Please Select an IFC File')
        elif event == 'README':
            create_readme_window()
        elif event == 'Link to EDE':
            create_ede_window()
        elif event == 'Find Out More':
            create_ede_read_window()
        elif event == 'Save Properties':
            if ifc_data is None:
                print('Please Read IFC File')
            elif values['Excel File'][-5:] != '.xlsx':
                print(values['Excel File'])
                print('Please Select an .xlsx File')
            else:
                create_excel_dict(ifc_data, values['Excel File'])
                print('Writing Excel File COMPLETE')


if __name__ == '__main__':
    main_window()
