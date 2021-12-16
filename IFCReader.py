from collections import OrderedDict


def read_file(filename):
    file = open(filename, 'r')
    data = []
    for line in file:
        line = line.replace('\n', '')
#        line = line.replace(';', '')
        data.append(line.strip())
    return data


class IfcType:
    def __init__(self, name, base, data):
        self.Name = name
        self.Base = base
        self.Data = data
        self.Where = {}
        self.BaseList = []
        if len(self.Data) > 1:
            self.process_type()

    def process_type(self):
        type_sub = ''
        for line in self.Data[1:]:
            line = line.replace(';', '')
            if line == 'WHERE':
                type_sub = 'WHERE'
            elif type_sub == 'WHERE':
                self.add_where(line)
            elif type_sub == '':
                base_list = line.replace('(', '')
                base_list = base_list.replace(')', '')
                base_list = base_list.replace(',', '')
                self.add_base_list(base_list)

    def add_where(self, line):
        line_split = line.split(':', 1)
        self.Where[line_split[0].strip()] = line_split[1].strip()

    def add_base_list(self, base):
        self.BaseList.append(base)


class IfcEntity:
    def __init__(self, name, data):
        self.Name = name
        self.Data = data
        self.Values = OrderedDict()
        self.Subtype = None
        self.process_entity()

    def process_entity(self):
        entity_sub = ''
        for line in self.Data[1:]:
            line = line.replace(';', '')
            if line[0] == '(' or line[0] == ',':
                pass
            elif line[:11] == 'SUBTYPE OF ':
                self.Subtype = line.split('(')[1][:-1].upper()
                entity_sub = ''
            elif line[:13] == 'SUPERTYPE OF ':
                entity_sub = ''
            elif line[:22] == 'ABSTRACT SUPERTYPE OF ':
                entity_sub = ''
            elif line == 'WHERE':
                entity_sub = 'WHERE'
            elif line == 'INVERSE':
                entity_sub = 'INVERSE'
            elif line == 'UNIQUE':
                entity_sub = 'UNIQUE'
            elif line == 'DERIVE':
                entity_sub = 'DERIVE'
            elif entity_sub == '':
                self.add_value(line)

    def add_value(self, line):
        line_split = line.split(':', 1)
        self.Values[line_split[0].strip()] = line_split[1].strip()


def create_line(input_list):
    out_list = []
    for i in input_list:
        if isinstance(i, list):
            out_list.append(create_line(i))
        else:
            out_list.append(i)
    return '(' + ','.join(out_list) + ')'


def process_list(line):
    out_list = []
    value_type = ''
    value = ''
    list_count = 0
    for char in line:
        if char == "'":
            if value_type == 'STRING':
                value_type = ''
            else:
                value_type = 'STRING'
        elif value_type == 'STRING':
            value = value + char
        elif value == 'IFC':
            value_type = 'IFC_LABEL'
            value = value + char
        elif value_type == 'IFC_LABEL':
            value = value + char
            if char == ')':
                value_type = ''
        elif char == '(' and list_count == 0:
            value_type = 'LIST'
            list_count = 1
        elif char == ')' and list_count == 1:
            value = process_list(value)
            value_type = ''
            list_count = 0
        elif value_type == 'LIST':
            value = value + char
            if char == '(':
                list_count = list_count + 1
            elif char == ')':
                list_count = list_count - 1
        elif char == ',':
            out_list.append(value)
            value = ''
        elif char == ' ':
            pass
        else:
            value = value + char
    out_list.append(value)
    return out_list


def process_data(data):
    if data == '$':
        return None
    else:
        return data


class IfcSchema:
    def __init__(self, filename):
        self.FileName = filename
        print('Reading file schema')
        self.File = read_file(filename)
        print('Processing schema types')
        self.Types = self.read_types()
        print('Processing schema entities')
        self.Entities = self.read_entities()
        self.entities_subtype()


    def entities_subtype(self):
        for entity in self.Entities.values():
            if entity.Subtype is not None:
                entity.Values = self.combine_dicts(entity.Values, entity.Subtype)



    def combine_dicts(self, values, sub_type):
        combine_entity = self.Entities[sub_type]
        if combine_entity.Subtype is not None:
            new_dict = self.combine_dicts(combine_entity.Values, combine_entity.Subtype).copy()
        else:
            new_dict = combine_entity.Values.copy()
        for key in values.keys():
            new_dict[key] = values[key]
        return new_dict

    def read_types(self):
        types = {}
        i = 0
        while i < len(self.File):
            line = self.File[i].replace(';', '')
            if line[:5] == 'TYPE ':
                line_split = line.split(' ', 3)
                type_name = line_split[1]
                type_base = line_split[3]
                type_data = []
                while 'END_TYPE' not in line:
                    type_data.append(line)
                    i = i + 1
                    line = self.File[i]
                types[type_name.upper()] = IfcType(type_name, type_base, type_data)
            i = i + 1
        return types

    def read_entities(self):
        entities = {}
        i = 0
        while i < len(self.File):
            line = self.File[i].replace(';', '')
            if line[:7] == 'ENTITY ':
                line_split = line.split(' ')
                entity_name = line_split[1]
                entity_data = []
                while 'END_ENTITY' not in line:
                    entity_data.append(line)
                    i = i + 1
                    line = self.File[i]
                entities[entity_name.upper()] = IfcEntity(entity_name, entity_data)
            i = i + 1
        return entities

    def convert_type(self, ifc_type, value):
        base = self.Types[ifc_type.upper()].Base.upper()
        out_value = None
        if 'IFC' in base:
            out_value = self.convert_type(self.Types[base].Name, value)
        else:
            if base in ['STRING', 'STRING(22) FIXED']:
                out_value = str(value)
            elif base in ['BOOLEAN', 'LOGICAL']:
                if value == '.T.':
                    out_value = True
                elif value == '.F.':
                    out_value = False
                else:
                    out_value = None
            elif base in ['REAL', 'NUMBER']:
                out_value = float(value)
            elif base in ['INTEGER']:
                out_value = int(value)
            else:
                print('UNABLE TO PROCESS: ' + str(base))
        return out_value


class IFCEntityData:
    def __init__(self, ifc_id, line, schema):
        self.Id = ifc_id
        self.Line = line
        self.EntityName = line[: line.find('(')]
        self.Entity = schema.Entities[self.EntityName]
        self.ListData = process_list(line[line.find('(') + 1: -2])
        self.Values = self.match_values()
        self.Tree = []

    def match_values(self):
        value_dict = OrderedDict()
        new_list = [i for i in self.ListData]
        for i in range(0, len(new_list)):
            value_key = list(self.Entity.Values.keys())[i]
            value_dict[value_key] = process_data(new_list[i])
        return value_dict

    def add_tree(self, item):
        if item not in self.Tree:
            self.Tree.append(item)

    def output_line(self):
        return self.EntityName + create_line(self.ListData)


class IfcFile:
    def __init__(self, file_name, schema_name):
        self.FileName = file_name
        self.Schema = IfcSchema(schema_name)
        print('Reading IFC file')
        self.File = read_file(file_name)
        print('Processing IFC entities')
        self.Entities = self.read_data()
        print('Categorising entities')
        self.EntitiesByType = self.group_entities()
        self.GlobalID = self.get_guid()

    def get_guid(self):
        guid_dict = {}
        for ifc_entity in self.Entities.values():
            if 'GlobalId' in ifc_entity.Values.keys():
                guid_dict[ifc_entity.Values['GlobalId']] = ifc_entity.Id
        return guid_dict

    def read_data(self):
        data = {}
        for line in self.File:
            if len(line) > 1:
                if line[0] == '#':
                    line_split = line.split('=', 1)
                    ifc_id = line_split[0].strip()
                    data[ifc_id] = IFCEntityData(line_split[0].strip(), line_split[1].strip(), self.Schema)
        return data

    def replace_hash_links(self):
        for entities_key in self.Entities.keys():
            for value_key in self.Entities[entities_key].Values.keys():
                value_line = self.Entities[entities_key].Values[value_key]
                if isinstance(value_line, list):
                    self.Entities[entities_key].Values[value_key] = []
                    for j in range(0, len(value_line)):
                        value = value_line[j]
                        self.Entities[entities_key].Values[value_key].append(self.replace_hash(value, entities_key))
                else:
                    self.Entities[entities_key].Values[value_key] = self.replace_hash(value_line, entities_key)

    def replace_hash(self, data, entities_key):
        if data is not None:
            if isinstance(data, str) and len(data) > 1:
                if data[0] == '#':
                    data_id = data
                    data = self.Entities[data_id]
                    self.Entities[data_id].add_tree(self.Entities[entities_key])
        return data

    def group_entities(self):
        entities_dict = {}
        for ifc_entity in self.Entities.values():
            if ifc_entity.EntityName not in entities_dict.keys():
                entities_dict[ifc_entity.EntityName] = {}
            entities_dict[ifc_entity.EntityName][ifc_entity.Id] = ifc_entity
        return OrderedDict(sorted(entities_dict.items()))


if __name__ == "__main__":

    IfcFile = IfcFile("test_data/AC9R1-Haus-G-H-Ver2-2x3.ifc", "Schema/IFC2X3_TC1.exp")
