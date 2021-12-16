from IFCReader import IfcFile
from IFCPropertyReader import create_property_dict
import xlsxwriter


def property_out_dict(property_dict):
    output_dict = {}
    for entity_guid in property_dict.keys():
        for property_set in property_dict[entity_guid].keys():
            if property_set not in output_dict.keys():
                output_dict[property_set] = [['IFC GUID']]
            empty_list = [None for x in output_dict[property_set][0]]
            empty_list[0] = entity_guid
            for property_name in property_dict[entity_guid][property_set].keys():
                if property_name not in output_dict[property_set][0]:
                    output_dict[property_set][0].append(property_name)
                    empty_list.append(None)
                empty_list[output_dict[property_set][0].index(property_name)] =\
                    property_dict[entity_guid][property_set][property_name]
            output_dict[property_set].append(empty_list)
    output_dict = square_list(output_dict)
    return output_dict


def square_list(out_dict):
    for set_name in out_dict.keys():
        req_length = len(out_dict[set_name][0])
        for i in range(1, len(out_dict[set_name])):
            out_dict[set_name][i] = out_dict[set_name][i] + [None] * (req_length - len(out_dict[set_name][i]))
    return out_dict


def create_excel_dict(ifc_file, excel_output):
    property_dict = create_property_dict(ifc_file)
    print('Creating Excel data')
    output_dict = property_out_dict(property_dict)
    print('Writing Excel file')
    workbook = xlsxwriter.Workbook(excel_output)
    for sheet_name in output_dict.keys():
        if len(sheet_name) <= 30:
            worksheet = workbook.add_worksheet(sheet_name[:31])
        else:
            worksheet = workbook.add_worksheet(sheet_name[:30])
            print('Property class ' + str(sheet_name) + ' renamed to ' + str(sheet_name[:30]) +
                  ' to meet length requirement for Excel sheet names')
        row_count = 0
        for sheet_row in output_dict[sheet_name]:
            worksheet.write_row(row_count, 0, sheet_row)
            row_count = row_count + 1
    workbook.close()


if __name__ == '__main__':
    IfcFile = IfcFile("test_data/AC9R1-Haus-G-H-Ver2-2x3.ifc", "Schema/IFC2X3_TC1.exp")
    ExcelOutput = 'PropertyResults.xlsx'
    create_excel_dict(IfcFile, ExcelOutput)
