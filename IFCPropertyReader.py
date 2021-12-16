from IFCReader import IfcFile
from collections import OrderedDict


def create_property_dict(ifc_file):
    print('Finding IFC Properties')
    property_dict = {}
    for defines_by_properties in ifc_file.EntitiesByType['IFCRELDEFINESBYPROPERTIES'].values():
        property_set = ifc_file.Entities[defines_by_properties.Values['RelatingPropertyDefinition']]
        set_name = 'Unknown'
        property_values = OrderedDict()
        if property_set.EntityName == 'IFCPROPERTYSET':
            for property_id in property_set.Values['HasProperties']:
                property_value = ifc_file.Entities[property_id].Values['NominalValue']
                if property_value is not None:
                    property_value_array = property_value.split('(', 1)
                    property_value = ifc_file.Schema.convert_type(property_value_array[0],
                                                                  property_value_array[1][: -1])
                    property_values[ifc_file.Entities[property_id].Values['Name']] = property_value
                set_name = property_set.Values['Name']
        elif property_set.EntityName == 'IFCELEMENTQUANTITY':
            set_name = 'Quantity'
            for quantity_id in property_set.Values['Quantities']:
                quantity = ifc_file.Entities[quantity_id]
                property_values[quantity.Values['Name']] = quantity.ListData[3]
        for object_id in defines_by_properties.Values['RelatedObjects']:
            object_guid = ifc_file.Entities[object_id].Values['GlobalId']
            if object_guid not in property_dict.keys():
                property_dict[object_guid] = OrderedDict()
            property_dict[object_guid][set_name] = property_values
    return property_dict


if __name__ == '__main__':
    IfcFile = IfcFile("test_data/AC9R1-Haus-G-H-Ver2-2x3.ifc", "Schema/IFC2X3_TC1.exp")
    PropertyDict = create_property_dict(IfcFile)
