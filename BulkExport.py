from IFCPropertiesToExcel import create_excel_dict
from IFCReader import IfcFile
import os


def bulk_read(read_file_list, excel_folder):
    for file in read_file_list:
        print(f'Reading IFC File: {file[1]}')
        ifc_file = IfcFile(file[0] + '\\' + file[1], "Schema/IFC2X3_TC1.exp")
        excel_filename = excel_folder + r'\\' + file[1][:-4] + '.xlsx'
        print(f'Creating Excel File: {file[1][:-4]}.xlsx')
        create_excel_dict(ifc_file, excel_filename)


def create_file_list(file_path, file_type):
    filename_list = []
    files = os.listdir(file_path)
    for f in files:
        if f[-3:] == file_type:
            print(f'File Found: {f}')
            filename_list.append((file_path, f))
        elif os.path.isdir(file_path + '\\' + f):
            filename_list += create_file_list(file_path + '\\' + f, file_type)
    return filename_list


def file_list(file_path, file_type='ifc'):
    print(f'Finding File List: {file_path}')
    print(f'Finding File Type: {file_type}')
    found_file_list = create_file_list(file_path, file_type)
    print(f'File List Complete. Total Files: {len(found_file_list)}')
    return found_file_list


if __name__ == '__main__':
    FilePath = r'Y:\01 - Client'
    print()
    FileList = file_list(FilePath)
    bulk_read(FileList, r'.\\ExcelOutput')

