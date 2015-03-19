'''
The MIT License (MIT)

Copyright (c) 2013 SinnerSchrader Mobile GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


import sys
import re
from pystache import Renderer
from cStringIO import StringIO

from template_code_generator import *

class SourceCodeGenerator :

    def __init__(self):
        self.mustache_renderer = Renderer()

    def lambda_uppercase(self, text):
        process_text = Renderer().render(text, self.mustache_renderer.context)
        return process_text.upper()

    def lambda_lowercase(self, text):
        process_text = Renderer().render(text, self.mustache_renderer.context)
        return process_text.lower()

    def lambda_capitalize(self, text):
        process_text = Renderer().render(text, self.mustache_renderer.context)
        return process_text.capitalize()

    def lambda_camelcase(self, text):
        process_text = Renderer().render(text, self.mustache_renderer.context)
        words = process_text.split('_')
        return ''.join(word.title() if i else word for i, word in enumerate(words))

    def lambda_upper_camelcase(self, text):
        camelcased_text = self.lambda_camelcase(text)
        return camelcased_text[:1].upper() + camelcased_text[1:]

    def lambda_snakecase(self, text):
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()

    def lambda_upper_snakecase(self, text):
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).upper()

    def makeVarName(self,schemeObj) :
        returnName = schemeObj.type_name
        if str(schemeObj.type_name) == "id" or str(schemeObj.type_name) == "description" :
            titleName = schemeObj.type_name.upper()
            titleName = titleName[:1] + schemeObj.type_name[1:]
            prefix = schemeObj.projectPrefix.lower() if schemeObj.projectPrefix else 'meta'
            returnName = prefix + titleName
        else :
            prefixes = ["new", "alloc", "copy"]
            for prefix in prefixes:
                if schemeObj.type_name.startswith(prefix):
                    titleName = schemeObj.type_name.upper()
                    titleName = titleName[:1] + schemeObj.type_name[1:]
                    returnName = schemeObj.projectPrefix.lower() + titleName

                    break
        return returnName

    def meta_property(self, schemeObj):
        meta_hash = {}
        meta_hash['name'] = schemeObj.type_name
        if schemeObj.base_type_list:
            meta_hash['base-type'] = schemeObj.base_type_list
        else:
            meta_hash['base-type'] = schemeObj.base_type
        meta_hash['description'] = schemeObj.type_description
        meta_hash['subType'] = schemeObj.sub_type
        if schemeObj.rootBaseType() == "string":
            hasRegex, regex = schemeObj.getRegex()
            if hasRegex:
                meta_hash['regex'] = regex

            hasMax, maxLength = schemeObj.getMaxLength()
            if hasMax:
                meta_hash['maxLength'] = maxLength

            hasMin, minLength = schemeObj.getMinLength()
            if hasMin:
                meta_hash['minLength'] = minLength

        if schemeObj.rootBaseType() == "number":
            hasMax, maxValue = schemeObj.getMaxValue()
            if hasMax:
                meta_hash['maxValue'] = str(maxValue)

            hasMin, minValue = schemeObj.getMinValue()
            if hasMin:
                meta_hash['minValue'] = str(minValue)

        if schemeObj.rootBaseType() == "array":
            hasMax, maxLength = schemeObj.getMaxCount()
            if hasMax:
                meta_hash['maxCount'] = maxLength

            hasMin, minLength = schemeObj.getMinCount()
            if hasMin:
                meta_hash['minCount'] = minLength

        return meta_hash


    def process_basetypes(self, propObj, propertyHash) :
        # dealing with array property
        if len(propObj.getBaseTypes()) == 1:
            propertyHash['hasOneBasetype'] = True
        elif len(propObj.getBaseTypes()) > 1:
            propertyHash['hasMultipleBasetypes'] = True
        else:
            propertyHash['hasNoBasetypes'] = True

        for subtype in propObj.getBaseTypes():
            key = 'hasCustomType'
            if subtype in propObj.naturalTypeList:
                key = 'has'+ subtype.capitalize() + 'Type'
                if key not in propertyHash:
                  propertyHash[key] = {"types": [{"type": subtype}]}
                else:
                  propertyHash[key]["types"].append({"type": subtype})
            elif subtype == "any":
                propertyHash['hasAnyType'] = {"type": "object"}
            else:
                # derivate baseType
                if propObj.getScheme(subtype).base_type in propObj.naturalTypeList:
                    key = 'has'+ propObj.getScheme(subtype).base_type.capitalize() + 'Type'
                    subtype_infos = {"type": subtype}
                    # nothing, subtype_definition = self.process_properties(propObj.getScheme(subtype))
                    subtype_definition = self.meta_property(propObj.getScheme(subtype))
                    subtype_infos =  {"type": subtype, "_type": subtype_definition}
                    if key not in propertyHash:
                      propertyHash[key] = {"types": [subtype_infos]}
                    else:
                      propertyHash[key]["types"].append(subtype_infos)

                else:
                  if key in propertyHash:
                    propertyHash[key]["subtypes"].append({"type": subtype, "className": propObj.getScheme(subtype).getClassName()})
                    classes.append(propObj.getScheme(subtype).getClassName())
                  else:
                    propertyHash[key] = { "subtypes": [{"type": subtype, "className": propObj.getScheme(subtype).getClassName()}]}
                    classes.append(propObj.getScheme(subtype).getClassName())

    def process_subtypes(self, propObj, propertyHash) :
        classes = []
        # dealing with array property
        if len(propObj.getSubType()) == 1:
            propertyHash['hasOneSubtype'] = True
        elif len(propObj.getSubType()) > 1:
            propertyHash['hasMultipleSubtypes'] = True
        else:
            propertyHash['hasNoSubtypes'] = True

        for subtype in propObj.getSubType():
            key = 'hasCustomType'
            if subtype in propObj.naturalTypeList:
                key = 'has'+ subtype.capitalize() + 'Type'
                if key not in propertyHash:
                  propertyHash[key] = {"subtypes": [{"subtype": subtype}]}
                else:
                  propertyHash[key]["subtypes"].append({"subtype": subtype})
            elif subtype == "any":
                propertyHash['hasAnyType'] = {"subtype": "object"}
            else:
                # derivate baseType
                if propObj.getScheme(subtype).base_type in propObj.naturalTypeList:
                    key = 'has'+ propObj.getScheme(subtype).base_type.capitalize() + 'Type'
                    subtype_infos = {"subtype": subtype}
                    # nothing, subtype_definition = self.process_properties(propObj.getScheme(subtype))
                    subtype_definition = self.meta_property(propObj.getScheme(subtype))
                    subtype_infos =  {"subtype": subtype, "_subtype": subtype_definition}
                    if key not in propertyHash:
                      propertyHash[key] = {"subtypes": [subtype_infos]}
                    else:
                      propertyHash[key]["subtypes"].append(subtype_infos)

                else:
                  if key in propertyHash:
                    propertyHash[key]["subtypes"].append({"subtype": subtype, "className": propObj.getScheme(subtype).getClassName()})
                    classes.append(propObj.getScheme(subtype).getClassName())
                  else:
                    propertyHash[key] = { "subtypes": [{"subtype": subtype, "className": propObj.getScheme(subtype).getClassName()}]}
                    classes.append(propObj.getScheme(subtype).getClassName())

        return classes

    def process_properties(self, propObj, undefined = False) :
        propertyHash = {'name' : propObj.type_name, 'varName' : self.makeVarName(propObj)}
        if propObj.type_description and len(propObj.type_description) :
            propertyHash["description"] = propObj.type_description
        if propObj.required == 1:
            propertyHash['required'] = True

        if propObj.rootBaseType() == "object":
            propertyHash['className'] = propObj.getClassName()
            return [propertyHash['className']], propertyHash

        if propObj.rootBaseType() == "string":
            hasRegex, regex = propObj.getRegex()
            if hasRegex:
                propertyHash['regex'] = regex

            hasMax, maxLength = propObj.getMaxLength()
            if hasMax:
                propertyHash['maxLength'] = maxLength

            hasMin, minLength = propObj.getMinLength()
            if hasMin:
                propertyHash['minLength'] = minLength

        if propObj.rootBaseType() == "number":
            hasMax, maxValue = propObj.getMaxValue()
            if hasMax:
                propertyHash['maxValue'] = str(maxValue)

            hasMin, minValue = propObj.getMinValue()
            if hasMin:
                propertyHash['minValue'] = str(minValue)

        if propObj.rootBaseType() == "array":
            hasMax, maxLength = propObj.getMaxCount()
            if hasMax:
                propertyHash['maxCount'] = maxLength

            hasMin, minLength = propObj.getMinCount()
            if hasMin:
                propertyHash['minCount'] = minLength

        # dealing with array property
        if propObj.rootBaseType() == "multi":
            self.process_basetypes(propObj, propertyHash)

        classes = self.process_subtypes(propObj, propertyHash)
        return classes, propertyHash


    def render(self, schemeObj, template_content) :
        today = datetime.date.fromtimestamp(time.time())

        numberProps = []
        stringProps = []
        booleanProps = []
        dataProps = []
        dateProps = []
        arrayProps = []
        undefineProps = []
        objectProps = []
        custom_classes = []
        for prop in schemeObj.props:
            classes = []
            if prop.rootBaseType() == "object":
                classes, prop_hash = self.process_properties(prop)
                objectProps.append(prop_hash)
            elif prop.rootBaseType() == "string":
                classes, prop_hash = self.process_properties(prop)
                stringProps.append(prop_hash)
            elif prop.rootBaseType() == "number":
                classes, prop_hash = self.process_properties(prop)
                numberProps.append(prop_hash)
            elif prop.rootBaseType() == "boolean":
                classes, prop_hash = self.process_properties(prop)
                booleanProps.append(prop_hash)
            elif prop.rootBaseType() == "data":
                classes, prop_hash = self.process_properties(prop)
                dataProps.append(prop_hash)
            elif prop.rootBaseType() == "date":
                classes, prop_hash = self.process_properties(prop)
                dateProps.append(prop_hash)
            elif prop.rootBaseType() == "array":
                classes, prop_hash = self.process_properties(prop)
                arrayProps.append(prop_hash)
            elif prop.rootBaseType() == "multi":
                classes, prop_hash = self.process_properties(prop, True)
                undefineProps.append(prop_hash)
            else:
                classes, prop_hash = self.process_properties(prop, True)
                undefineProps.append(prop_hash)
            if(len(classes) > 0):
              custom_classes.extend(classes)

        hashParams = {"date": str(today.year), "suffix": schemeObj.objectSuffix, "prefix": schemeObj.projectPrefix, "package": schemeObj.packageName, "name": schemeObj.type_name, "varName": self.makeVarName(schemeObj), "stringProperties": stringProps, "numberProperties": numberProps, "booleanProperties": booleanProps, "dataProperties": dataProps, "dateProperties": dateProps, "arrayProperties": arrayProps, "undefinedProperties": undefineProps, "objectProperties": objectProps}
        hashParams["custom_classes"] = []
        for classname in custom_classes:
          if classname not in hashParams["custom_classes"]:
            hashParams["custom_classes"].append(classname)
        hashParams["_uppercase"] =  self.lambda_uppercase
        hashParams["_lowercase"] =  self.lambda_lowercase
        hashParams["_capitalize"] =  self.lambda_capitalize
        hashParams["_upper_camelcase"] =  self.lambda_upper_camelcase
        hashParams["_camelcase"] =  self.lambda_camelcase
        hashParams["_snakecase"] =  self.lambda_snakecase
        hashParams["_upper_snakecase"] =  self.lambda_upper_snakecase
        if schemeObj.getScheme(schemeObj.base_type):
            hashParams['baseClassName'] = schemeObj.getScheme(schemeObj.base_type).getClassName()

        if schemeObj.base_type == 'object':
            hashParams['baseTypeIsObject'] = True

        # render
        sourceString = self.mustache_renderer.render(template_content, hashParams)
        return sourceString
