from IFCReader import IfcFile


class IfcUnit:
    def __init__(self, reference, components):
        self.Reference = reference
        self.Components = components


def process_si_unit(ifc_unit):
    if ifc_unit.Values['Prefix'] is None:
        unit_prefix = None
    else:
        unit_prefix = ifc_unit.Values['Prefix'].replace('.', '')
    unit_name = ifc_unit.Values['Name'].replace('.', '')
    prefix = get_prefix(unit_prefix)
    unit = get_dimensional_components(unit_name)
    reference = prefix[1] + unit[1]
    components = unit[0]
    return IfcUnit(reference, components)


def process_conversion_unit(ifc_unit, ifc_component):
    reference = ifc_unit.Values['Name']
    components = [int(x) for x in ifc_component.ListData]
    return IfcUnit(reference, components)


def process_user_unit(ifc_unit, ifc_file):
    reference = ''
    components = [0, 0, 0, 0, 0, 0]
    for element_id in ifc_unit.Values['Elements']:
        exponent = int(ifc_file.Entities[element_id].Values['Exponent'])
        si_unit = process_si_unit(ifc_file.Entities[ifc_file.Entities[element_id].Values['Unit']])
        if exponent == 1:
            reference += si_unit.Reference
        else:
            reference += si_unit.Reference + str(exponent)
    components = merge_components(components, si_unit.Components, exponent)
    return IfcUnit(reference, components)


def merge_components(components, si_components, exponent):
    for i in range(0, 6):
        components[i] = components[i] + si_components[i] * exponent
    return components


def get_units(ifc_file):
    unit_dict = {}
    ifc_project = list(ifc_file.EntitiesByType['IFCPROJECT'].values())[0]
    for unit_id in ifc_file.Entities[ifc_project.Values['UnitsInContext']].Values['Units']:
        ifc_unit = ifc_file.Entities[unit_id]
        if ifc_unit.EntityName == 'IFCSIUNIT':
            unit_dict[ifc_unit.Values['UnitType'].replace('.', '')] = process_si_unit(ifc_unit)
        elif ifc_unit.EntityName == 'IFCDERIVEDUNIT':
            unit_dict[ifc_unit.Values['UnitType'].replace('.', '')] = process_user_unit(ifc_unit, ifc_file)
        elif ifc_unit.EntityName == 'IFCCONVERSIONBASEDUNIT':
            unit_dict[ifc_unit.Values['UnitType'].replace('.', '')] =\
                process_conversion_unit(ifc_unit, ifc_file.Entities[ifc_unit.Values['Dimensions']])
        else:
            print('Unit Entity Unknown: ' + str(ifc_unit.EntityName))
    return unit_dict


def get_dimensional_components(unit_name):
    if unit_name == 'METRE':
        return [[1, 0, 0, 0, 0, 0, 0], 'm']
    elif unit_name == 'SQUARE_METRE':
        return [[2, 0, 0, 0, 0, 0, 0], 'm2']
    elif unit_name == 'CUBIC_METRE':
        return [[3, 0, 0, 0, 0, 0, 0], 'm3']
    elif unit_name == 'GRAM':
        return [[0, 1, 0, 0, 0, 0, 0], 'g']
    elif unit_name == 'SECOND':
        return [[0, 0, 1, 0, 0, 0, 0], 's']
    elif unit_name == 'AMPERE':
        return [[0, 0, 0, 1, 0, 0, 0], 'A']
    elif unit_name == 'KELVIN':
        return [[0, 0, 0, 0, 1, 0, 0], 'K']
    elif unit_name == 'MOLE':
        return [[0, 0, 0, 0, 0, 1, 0], 'mol']
    elif unit_name == 'CANDELA':
        return [[0, 0, 0, 0, 0, 0, 1], 'cd']
    elif unit_name == 'RADIAN':
        return [[0, 0, 0, 0, 0, 0, 0], 'rad']
    elif unit_name == 'STERADIAN':
        return [[0, 0, 0, 0, 0, 0, 0], 'sr']
    elif unit_name == 'HERTZ':
        return [[0, 0, -1, 0, 0, 0, 0], 'Hz']
    elif unit_name == 'NEWTON':
        return [[1, 1, -2, 0, 0, 0, 0], 'N']
    elif unit_name == 'PASCAL':
        return [[-1, 1, -2, 0, 0, 0, 0], 'Pa']
    elif unit_name == 'JOULE':
        return [[2, 1, -2, 0, 0, 0, 0], 'J']
    elif unit_name == 'WATT':
        return [[2, 1, -3, 0, 0, 0, 0], 'W']
    elif unit_name == 'COULOMB':
        return [[0, 0, 1, 1, 0, 0, 0], 'C']
    elif unit_name == 'VOLT':
        return [[2, 1, -3, -1, 0, 0, 0], 'V']
    elif unit_name == 'FARAD':
        return [[-2, -1, 4, 2, 0, 0, 0], 'F']
    elif unit_name == 'OHM':
        return [[2, 1, -3, -2, 0, 0, 0], 'Ω']
    elif unit_name == 'SIEMENS':
        return [[-2, -1, 3, 2, 0, 0, 0], 'S']
    elif unit_name == 'WEBER':
        return [[2, 1, -2, -1, 0, 0, 0], 'Wb']
    elif unit_name == 'TESLA':
        return [[0, 1, -2, -1, 0, 0, 0], 'T']
    elif unit_name == 'HENRY':
        return [[2, 1, -2, -2, 0, 0, 0], 'H']
    elif unit_name == 'DEGREE_CELSIUS':
        return [[0, 0, 0, 0, 1, 0, 0], '°C']
    elif unit_name == 'LUMEN':
        return [[0, 0, 0, 0, 0, 0, 1], 'lm']
    elif unit_name == 'LUX':
        return [[-2, 0, 0, 0, 0, 0, 1], 'lx']
    elif unit_name == 'BECQUEREL':
        return [[0, 0, -1, 0, 0, 0, 0], 'Bq']
    elif unit_name == 'GRAY':
        return [[2, 0, -2, 0, 0, 0, 0], 'Gy']
    elif unit_name == 'SIEVERT':
        return [[2, 0, -2, 0, 0, 0, 0], 'Sv']
    else:
        return [[0, 0, 0, 0, 0, 0, 0], '(N/A)']


def get_prefix(prefix):
    if prefix is None:
        return [1, '']
    else:
        if prefix == 'EXA':
            return [10 ** 18, 'E']
        elif prefix == 'PETA':
            return [10 ** 15, 'P']
        elif prefix == 'TERA':
            return [10 ** 12, 'T']
        elif prefix == 'GIGA':
            return [10 ** 9, 'G']
        elif prefix == 'MEGA':
            return [10 ** 6, 'M']
        elif prefix == 'KILO':
            return [10 ** 3, 'k']
        elif prefix == 'HECTO':
            return [10 ** 2, 'h']
        elif prefix == 'DECA':
            return [10, 'da']
        elif prefix == 'DECI':
            return [10 ** -1, 'd']
        elif prefix == 'CENTI':
            return [10 ** -2, 'c']
        elif prefix == 'MILLI':
            return [10 ** -3, 'm']
        elif prefix == 'MICRO':
            return [10 ** -6, 'μ']
        elif prefix == 'NANO':
            return [10 ** -9, 'n']
        elif prefix == 'PICO':
            return [10 ** -12, 'p']
        elif prefix == 'FEMTO':
            return [10 ** -15, 'f']
        elif prefix == 'ATTO':
            return [10 ** -18, 'a']
        else:
            return [1, '']


if __name__ == '__main__':
    IfcFile = IfcFile("test_data/AC9R1-Haus-G-H-Ver2-2x3.ifc", "Schema/IFC2X3_TC1.exp")
    ProjectUnits = get_units(IfcFile)

    for Unit in ProjectUnits.items():
        print(Unit[0])
        print(Unit[1].Reference)

    for SingleProperty in IfcFile.EntitiesByType['IFCPROPERTYSINGLEVALUE'].values():
        line = SingleProperty.Values['NominalValue']
        type = line.split('(')[0]
        if type not in ['IFCINTEGER', 'IFCREAL', 'IFCBOOLEAN', 'IFCIDENTIFIER', 'IFCTEXT', 'IFCLABEL', 'IFCLOGICAL']:
            unit = type[3:-7] + 'UNIT'
            keys = list(ProjectUnits.keys())
            if unit in keys:
                pass
            else:
                if "LEN" in unit:
                    print(unit)
                    print(keys[0])
                    compare = unit == keys[0]
                    print(compare)
                    for i in range(0, len(unit)):
                        print(str(i) + ': ' + unit[i] + ':' + keys[0][i])

                    print('NOT FOUND')
