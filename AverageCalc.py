# -*- coding: utf-8 -*-

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [AverageIndices]


class AverageIndices(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "AverageIndices"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        input_fc = arcpy.Parameter(
            displayName="Proposed Locations",
            name="input_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        input_fc.filter.list = ["Point"]

        ridership_idx = arcpy.Parameter(
            displayName="New Field Name",
            name="rdi",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        fields = arcpy.Parameter(
            displayName="Fields",
            name="fields",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        weights = arcpy.Parameter(
            displayName="Weights",
            name="weights",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        output_fc = arcpy.Parameter(
            displayName="Output Features",
            name="output_features",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output")

        output_fc.parameterDependencies = [input_fc.name]
        output_fc.schema.clone = True

        params = [input_fc, ridership_idx, fields, weights, output_fc]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].altered:
            fields = self.getFieldNames(parameters[0].valueAsText)
            parameters[2].filter.list = fields
        return

    # Get a list of field names
    def getFieldNames(self, name):
        fields = arcpy.ListFields(name)
        text_fields = []
        for f in fields:
            text_fields.append(f.baseName)
        return text_fields

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def calculate_composite(self, output_fc, ride_index, field_inputs, weights):
        arcpy.AddField_management(output_fc, ride_index, 'DOUBLE')
        zexpression = '''
def zeroOut():
    return 0.0
'''
        arcpy.CalculateField_management(output_fc, ride_index, 'zeroOut()', 'PYTHON_9.3', zexpression)

        expression = '''
def calcRideAverage(field, weight, index):
        return index + field*weight
'''

        fs = field_inputs.split(';')
        ws = weights.split(';')
        i = 0
        for f in range(len(fs)):
            arcpy.CalculateField_management(output_fc, ride_index, 'calcRideAverage(!' + fs[f] + '!, ' + ws[f] + ', !' + ride_index + '!)', 'PYTHON_9.3', expression)
            i += 1

        dexpression = '''
def getAverage(index, i):
    return index / int(i)
'''
        arcpy.CalculateField_management(output_fc, ride_index, 'getAverage(!' + ride_index + '!, ' + str(i) + ')', 'PYTHON_9.3', dexpression)


    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_fc = parameters[0].valueAsText
        
        ride_index = parameters[1].valueAsText
        
        field_inputs = parameters[2].valueAsText
        weights = parameters[3].valueAsText

        self.calculate_composite(input_fc, ride_index, field_inputs, weights)
        return

