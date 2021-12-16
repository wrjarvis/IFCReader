from PySimpleGUI import Window, WIN_CLOSED, Input, FileBrowse, Button, Output, Text, FileSaveAs, TabGroup, Tab, Combo
from IFCReader import IfcFile
from IFCPropertyReader import create_property_dict
from IFCPropertiesToExcel import property_out_dict
import json


class SetTab:
    def __init__(self, categories_list, checks_dict):

        self.InputOptions = 4
        self.DataDict = {}
        self.CatList = categories_list

        layout = [
            [
                Text("Set Name:", size=(15, 1)),
                Combo(list(checks_dict['Sets'].keys()), size=(33, 10), enable_events=True, key='_INSET_'),
                Button('Save Set', size=(15, 1)),
                Button('Delete Set', size=(15, 1))
            ],
            [
                Text("")
            ],
            [
                Text('Category                         '),
                Text('Property                          '),
                Text('Condition       '),
                Text('Value')
            ]
        ]

        self.ValueArray = self.create_value_array()
        for value_line in self.ValueArray:
            selection_line = [
                [
                    Combo(self.CatList, size=(20, 10), enable_events=True, key=value_line[0]),
                    Combo([''], size=(20, 10), enable_events=True, key=value_line[1]),
                    Combo([''], size=(10, 10), enable_events=True, key=value_line[2]),
                    Combo([''], size=(30, 10), enable_events=True, key=value_line[3])
                ]
            ]
            layout += selection_line

        layout += [
            [
                Text("")
            ]
        ]
        self.Layout = layout

    def create_value_array(self):
        value_array = []
        for i in range(0, self.InputOptions):
            i = str(i)
            value_array.append(['_CAT' + i + '_', '_PRO' + i + '_', '_CON' + i + '_', '_VAL' + i + '_'])
            for key in ['_CAT' + i + '_', '_PRO' + i + '_', '_CON' + i + '_', '_VAL' + i + '_']:
                self.DataDict[key] = ['', ['']]
                if 'CAT' in key:
                    self.DataDict[key][1] = self.CatList
        return value_array

    def tab_functions(self, event, values, checks_dict, window, out_dict):

        if event == 'Save Set':
            if values['_INSET_'] != '':
                set_name = values['_INSET_']
                set_values = [[values[x] for x in value_line] for value_line in self.ValueArray]
                if set_name in checks_dict['Sets'].keys():
                    print('Overwriting Set: ' + set_name)
                else:
                    print('Creating new set: ' + set_name)
                checks_dict['Sets'][set_name] = set_values
                window['_INSET_'].update(values=list(checks_dict['Sets'].keys()))
                window['_CHE_SET_'].update(value='', values=list(checks_dict['Sets'].keys()))
            else:
                print('Please enter set name to save')

        elif event == 'Delete Set':
            if values['_INSET_'] in checks_dict['Sets'].keys():
                print('Deleting set: ' + values['_INSET_'])
                checks_dict['Sets'].pop(values['_INSET_'])
                window['_INSET_'].update(value='', values=list(checks_dict['Sets'].keys()))
                window['_CHE_SET_'].update(value='', values=list(checks_dict['Sets'].keys()))

        for i in range(len(self.ValueArray)):

            cat = self.ValueArray[i][0]
            pro = self.ValueArray[i][1]
            con = self.ValueArray[i][2]
            val = self.ValueArray[i][3]

            if event == '_INSET_':
                self.DataDict[cat] = [checks_dict['Sets'][values['_INSET_']][i][0],
                                      self.CatList]
                self.DataDict[pro] = [checks_dict['Sets'][values['_INSET_']][i][1],
                                      create_property_list(checks_dict['Sets'][values['_INSET_']][i][0], out_dict)]
                self.DataDict[con] = [checks_dict['Sets'][values['_INSET_']][i][2],
                                      get_conditions(get_value_list(values, cat, out_dict, pro))]
                self.DataDict[val] = [checks_dict['Sets'][values['_INSET_']][i][3],
                                      get_value_list(values, cat, out_dict, pro)]

            elif event == cat:
                self.DataDict[cat] = [values[cat], self.DataDict[cat][1]]
                self.DataDict[pro] = ['', create_property_list(values[cat], out_dict)]
                self.DataDict[con] = ['', ['']]
                self.DataDict[val] = ['', ['']]

            elif event == pro:
                self.DataDict[pro] = [values[pro], self.DataDict[pro][1]]
                value_list = get_value_list(values, cat, out_dict, pro)
                self.DataDict[con] = ['=', get_conditions(value_list)]
                self.DataDict[val] = ['', value_list]

            elif event == con:
                self.DataDict[con] = [values[con], self.DataDict[con][1]]
                if values[con] in ['Defined', 'Not Defined']:
                    self.DataDict[val] = ['N/A', ['N/A']]
                else:
                    value_list = get_value_list(values, cat, out_dict, pro)
                    self.DataDict[val] = ['', value_list]

            elif event == val:
                self.DataDict[val] = [values[val], self.DataDict[val][1]]

        self.update_values(window)
        return checks_dict

    def update_values(self, window):
        for key in self.DataDict.keys():
            window[key].update(value=self.DataDict[key][0], values=self.DataDict[key][1])


class VariableTab:
    def __init__(self, checks_dict, categories_list):
        self.FunctionList = ['=', 'Max', 'Min', 'Count', 'Sum']
        self.Layout = [
            [
                Text("Variable Name:", size=(15, 1)),
                Combo(list(checks_dict['Variables'].keys()), size=(33, 10), enable_events=True, key='_INVAR_'),
                Button('Save Variable', size=(15, 1)),
                Button('Delete Variable', size=(15, 1))
            ],
            [
                Text("")
            ],
            [
                Text('Function', size=(26, 1)),
                Text('Category', size=(26, 1)),
                Text('Property')
            ],
            [
                Combo(self.FunctionList, size=(28, 10), enable_events=True, key='_VAR_FUN_'),
                Combo(categories_list, size=(28, 10), enable_events=True, key='_VAR_CAT1_'),
                Combo([''], size=(28, 10), enable_events=True, key='_VAR_PRO1_')
            ],
            [
                Text('Option', size=(26, 1)),
                Text('Category', size=(26, 1)),
                Text('Property')
            ],
            [
                Combo([''], size=(28, 10), enable_events=True, key='_VAR_OPT_'),
                Combo(categories_list, size=(28, 10), enable_events=True, key='_VAR_CAT2_'),
                Combo([''], size=(28, 10), enable_events=True, key='_VAR_PRO2_')
            ]
        ]
        self.ArrayOptions = ['', 'GROUP BY']
        self.SingleOptions = ['', '+', '-', 'x', '/']

    def tab_functions(self, event, values, checks_dict, window, out_dict):

        if event == 'Save Variable':
            if values['_INVAR_'] != '':
                var_name = values['_INVAR_']
                var_values = [values['_VAR_FUN_'], values['_VAR_CAT1_'], values['_VAR_PRO1_'], values['_VAR_OPT_'],
                              values['_VAR_CAT2_'], values['_VAR_PRO2_']]
                if var_name in checks_dict['Variables'].keys():
                    print('Overwriting variable: ' + var_name)
                else:
                    print('Creating new variable: ' + var_name)
                checks_dict['Variables'][var_name] = var_values
                window['_INVAR_'].update(values=list(checks_dict['Variables'].keys()))
                window['_CHE_VAR_'].update(value='', values=list(checks_dict['Variables'].keys()))
            else:
                print('Please enter variable name to save')

        elif event == 'Delete Variable':
            if values['_INVAR_'] in checks_dict['Variables'].keys():
                print('Deleting variable: ' + values['_INVAR_'])
                checks_dict['Variables'].pop(values['_INVAR_'])
                window['_INVAR_'].update(value='', values=list(checks_dict['Variables'].keys()))
                window['_CHE_VAR_'].update(value='', values=list(checks_dict['Variables'].keys()))

        elif event == '_INVAR_':
            if values['_INVAR_'] in checks_dict['Variables'].keys():
                populate_data = checks_dict['Variables'][values['_INVAR_']]
                window['_VAR_FUN_'].update(value=populate_data[0])
                window['_VAR_CAT1_'].update(value=populate_data[1])
                window['_VAR_PRO1_'].update(value=populate_data[2])
                window['_VAR_OPT_'].update(value=populate_data[3])
                window['_VAR_CAT2_'].update(value=populate_data[4])
                window['_VAR_PRO2_'].update(value=populate_data[5])

        elif event == '_VAR_FUN_':
            if values['_VAR_FUN_'] == '=':
                window['_VAR_OPT_'].update(value='', values=self.SingleOptions)
            else:
                window['_VAR_OPT_'].update(value='', values=self.ArrayOptions)

        elif event == '_VAR_CAT1_':
            if values['_VAR_CAT1_'] in out_dict.keys():
                property_list = out_dict[values['_VAR_CAT1_']][0][1:]
                property_list.sort()
                window['_VAR_PRO1_'].update(value='', values=property_list)
            else:
                window['_VAR_PRO1_'].update(value='', values=[''])

        elif event == '_VAR_CAT2_':
            if values['_VAR_CAT2_'] in out_dict.keys():
                property_list = out_dict[values['_VAR_CAT2_']][0][1:]
                property_list.sort()
                window['_VAR_PRO2_'].update(value='', values=property_list)
            else:
                window['_VAR_PRO2_'].update(value='', values=[''])



        elif event == '_VAR_OPT_':
            if values['_VAR_OPT_'] == '':
                window['_VAR_CAT2_'].update(value='NA', values=['NA'])
                window['_VAR_PRO2_'].update(value='NA', values=['NA'])
            else:
                if values['_VAR_CAT2_'] in out_dict.keys():+
                    property_list = out_dict[values['_VAR_CAT2_']][0][1:]
                    property_list.sort()
                    window['_VAR_PRO2_'].update(value='', values=['property_list'])
                else:
                    window['_VAR_PRO2_'].update(value='', values=[''])

        return checks_dict







def create_property_list(set_name, out_dict):
    if set_name == '':
        property_list = ['']
    else:
        if set_name in out_dict.keys():
            property_list = out_dict[set_name][0][1:]
            property_list.sort()
        else:
            property_list = ['']
    return property_list


def remove_duplicates(in_list):
    out_list = []
    for x in in_list:
        if x not in out_list:
            out_list.append(x)
    return out_list


def combine_checks(check_file, new_checks):
    for item_type in check_file.keys():
        for new_item in new_checks[item_type]:
            if new_item not in check_file[item_type].keys():
                check_file[item_type][new_item] = new_checks[item_type][new_item]
                print('Imported ' + item_type.lower() + ': ' + str(new_item))
            else:
                for i in range(1, 1000):
                    new_item_no = new_item + '(' + str(i) + ')'
                    if new_item_no not in check_file[item_type].keys():
                        check_file[item_type][new_item_no] = new_checks[item_type][new_item]
                        print('Imported ' + item_type.lower() + ': ' + str(new_item) + ' as ' + str(new_item_no) +
                              ' due to name duplication')
                        break
    return check_file


def create_template(property_dict):
    checks_dict = {'Sets': {}, 'Variables': {}, 'Checks': {}}
    out_dict = property_out_dict(property_dict)

    categories_list = [''] + list(out_dict.keys())

    set_tab = SetTab(categories_list, checks_dict)
    variable_tab = VariableTab(checks_dict, categories_list)
    check_layout = check_manager_tab(checks_dict)

    layout = [
        [
            Text("Create Template", font='Any 25')
        ],
        [
            Text("")
        ],
        [
            Text("Import Check Template:", size=(20, 1)),
            Input(size=(42, 1)),
            FileBrowse(key='Import JSON FileName', file_types=(('JSON', '.json'),), size=(10, 1)),
            Button('Import', size=(10, 1))
        ],
        [
            Text("Save Check Template:", size=(20, 1)),
            Input(size=(42, 1)),
            FileSaveAs(key='Save JSON FileName', file_types=(('JSON', '.json'),), size=(10, 1)),
            Button('Save', size=(10, 1))
        ],
        [
            Text("")
        ],
        [
            TabGroup([
                [Tab('Set Manager', set_tab.Layout, ),
                 Tab('Variable Manager', variable_tab.Layout, ),
                 Tab('Check Manager', check_layout, )]
            ], )],
        [
            Output(size=(92, 10))
        ]
    ]

    window = Window('IFC Editing Tool - Create Template', layout, size=(700, 620))

    checks_dict = window_functions(window, out_dict, checks_dict, set_tab, variable_tab)

    return checks_dict


def window_functions(window, out_dict, checks_dict, set_tab, variable_tab):

    while True:
        event, values = window.read()

        if event == WIN_CLOSED or event == 'Exit':
            break

        elif event == 'Save':
            if values['Save JSON FileName'][-5:] != '.json':
                print('Please select valid JSON file')
            else:
                with open(values['Save JSON FileName'], 'w') as out_json:
                    json.dump(checks_dict, out_json, indent=1)
                print('Template Saved')
        elif event == 'Import':
            if values['Import JSON FileName'][-5:] != '.json':
                print('Please select valid JSON file')
            else:
                with open(values['Import JSON FileName'], 'r') as in_json:
                    new_checks = json.loads(in_json.read())
                    print('Importing template file')
                    checks_dict = combine_checks(checks_dict, new_checks)
                    window['_INSET_'].update(value='', values=list(checks_dict['Sets'].keys()))
                    window['_INVAR_'].update(value='', values=list(checks_dict['Variables'].keys()))
                    window['_INCHE_'].update(value='', values=list(checks_dict['Checks'].keys()))
                    window['_CHE_SET_'].update(value='', values=list(checks_dict['Sets'].keys()))
                    window['_CHE_VAR_'].update(value='', values=list(checks_dict['Variables'].keys()))

        checks_dict = set_tab.tab_functions(event, values, checks_dict, window, out_dict)
        checks_dict = variable_tab.tab_functions(event, values, checks_dict, window, out_dict)
        checks_dict = check_functions(event, values, checks_dict, window)

    return checks_dict


def get_conditions(values):
    if all(isinstance(n, float) for n in values) or all(isinstance(n, int) for n in values):
        return ['=', 'Not equal', '>', '>=', '<', '<=', 'Defined', 'Not Defined']
    else:
        return ['=', 'Not equal', 'Defined', 'Not Defined', 'Contains']


def get_value_list(values, cat, out_dict, pro):
    value_list = ['']
    if values[cat] in out_dict.keys():
        if values[pro] in out_dict[values[cat]][0]:
            value_list = [x[out_dict[values[cat]][0].index(values[pro])] for x in out_dict[values[cat]][1:]]
            value_list = remove_duplicates(value_list)
            value_list = list(filter(lambda a: a is not None, value_list))
            value_list.sort()
            value_list = value_list
    return value_list




def check_functions(event, values, checks_dict, window):

    if event == 'Save Check':
        if values['_INCHE_'] != '':
            check_name = values['check_values']
            check_values = [values['_CHE_SET_'], values['_CHE_VAR_'], values['_CHE_LOG_'], values['_CHE_VAL_'],
                            values['_CHE_CAT_'], values['_CHE_PRO_']]
            if check_values in checks_dict['Variables'].keys():
                print('Overwriting variable: ' + check_name)
            else:
                print('Creating new variable: ' + check_name)
            checks_dict['Checks'][check_name] = check_values
            window['_INCHE_'].update(values=list(checks_dict['Checks'].keys()))
        else:
            print('Please enter check name to save')

    elif event == 'Delete Check':
        if values['_INCHE_'] in checks_dict['Checks'].keys():
            print('Deleting check: ' + values['_INCHE_'])
            checks_dict['Checks'].pop(values['_INCHE_'])
            window['_INCHE_'].update(value='', values=list(checks_dict['Checks'].keys()))

    elif event == '_INCHE_':
        if values['_INCHE_'] in checks_dict['Checks'].keys():
            populate_data = checks_dict['Checks'][values['_INCHE_']]
            window['_CHE_SET_'].update(value=populate_data[0])
            window['_CHE_VAR_'].update(value=populate_data[1])
            window['_CHE_LOG_'].update(value=populate_data[2])
            window['_CHE_VAL_'].update(value=populate_data[3])
            window['_CHE_VAR2_'].update(value=populate_data[4])

    elif event == '_CHE_LOG_':
        if values['_CHE_LOG_'] in ['Defined', 'Not Defined']:
            window['_CHE_VAL_'].update(value='N/A', values=['N/A'])
            window['_CHE_VAR2_'].update(value='N/A', values=['N/A'])
        else:
            window['_CHE_VAL_'].update(value='', values=['', 'Variable Value'])
            window['_CHE_VAR2_'].update(value='', values=[''])

    elif event == '_CHE_VAL_':
        if values['_CHE_VAL_'] == 'Variable Value':
            window['_CHE_VAR2_'].update(value='', values=list(checks_dict['Variables'].keys()))
        else:
            window['_CHE_VAR2_'].update(value='N/A', values=['N/A'])

    return checks_dict


def check_manager_tab(checks_dict):
    logic_list = ['=', 'Not equal', '>', '>=', '<', '<=', 'Defined', 'Not Defined', 'Contains']
    layout = [
        [
            Text("Check Name:", size=(15, 1)),
            Combo(list(checks_dict['Checks'].keys()), size=(33, 10), enable_events=True, key='_INCHE_'),
            Button('Save Check', size=(15, 1)),
            Button('Delete Check', size=(15, 1))
        ],
        [
            Text("")
        ],
        [
            Text('Set', size=(15, 1)),
            Text('Variable', size=(15, 1)),
            Text('Logic', size=(15, 1)),
            Text('Value', size=(15, 1)),
            Text('Variable', size=(15, 1))
        ],
        [
            Combo(list(checks_dict['Sets'].keys()), size=(15, 10), enable_events=True, key='_CHE_SET_'),
            Combo(list(checks_dict['Variables'].keys()), size=(15, 10), enable_events=True, key='_CHE_VAR_'),
            Combo(logic_list, size=(15, 10), enable_events=True, key='_CHE_LOG_'),
            Combo(['', 'Variable Value'], size=(15, 10), enable_events=True, key='_CHE_VAL_'),
            Combo(['N/A'], size=(15, 10), enable_events=True, key='_CHE_VAR2_')
        ]
    ]
    return layout


if __name__ == '__main__':
    IfcFile = IfcFile("test_data/HPC-OH1250-U1-HF7-MDL-304717.ifc", "Schema/IFC2X3_TC1.exp")
    PropertyDict = create_property_dict(IfcFile)
    ChecksDict = create_template(PropertyDict)
