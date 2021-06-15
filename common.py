# #!/usr/bin/env python
import json
import requests
import pandas as pd

# Common variables
api_base_url = 'https://api.spoonacular.com/'
api_key = 'cbc25debd8d94b1080be2a2fb6a39dcc'

# json_path = '/Users/nitinvig/Scripting/Projects/aahar/RnD/Nutrition/misc/8-May/'
# csv_path = '/Users/nitinvig/aahar/foodDB/mohan-Jan2021/'
# testing github actions workflows

json_path = './'
csv_path = './'
measure_json_file = 'measures.json'
url_csv_file = 'food_urls.csv'
food_json_file = 'food.json'
ing_json_file = 'ingredient.json'

# Fetch data from given API URL
def fetch_api_data(url):
    # print("Fetching data from %s" % url)
    response = requests.request("GET", url)
    return json.loads(response.text)

# Read from or Write to a JSON file
def read_write_json(filename, mode, data=None):
    with open(filename, mode=mode, encoding='utf-8') as file:
        if mode == 'w' or mode == 'w+':
            file.write(json.dumps(data, indent=2))
        elif mode == 'r':
            return json.load(file)

# Calculate total nutrients for a food item
def get_total_nutrients(food):
    ing_df = pd.read_json(json_path+ing_json_file)
    total_nutrients_df = pd.DataFrame(columns = ['amount', 'unit'])
    # look at each ingredient in the food item
    for food_ing in food['extendedIngredients']:
        # look for the ingredient in ingredient dataframe
        ing_row = ing_df.loc[ing_df['id'] == food_ing['id']]
        if ing_row.empty:
            # Do we need to handle this better?
            print(food_ing['name'],food_ing['id'])
            print('Something is wrong, food not found in ingredients JSON')
        else:
            food_qty_value = food_ing['measures']['metric']['amount']
            food_qty_unit = food_ing['measures']['metric']['unitShort']
            # pick the nutrition data from ingredient
            for key,value in ing_row['nutrition'].to_dict().items():
                ing_qty_value = value['weightPerServing']['amount']
                ing_qty_unit = value['weightPerServing']['unit']
                if ing_qty_value == 0:
                    continue
                else:
                    # if no unit provided, just take the qty value
                    if food_qty_unit == "":
                        recipe_convert = food_qty_value
                    # if unit is provided, convert it to the unit in ingredient JSON file
                    else:
                        recipe_measure = Measure(food_qty_unit,food_qty_value)
                        recipe_convert = recipe_measure.convert(ing_qty_unit,ing_qty_value)
                    # multiply the nutrient amount with recipe quantity and total it up
                    for nutrient in value['nutrients']:
                        nutrient_qty = nutrient['amount']*recipe_convert
                        # add the first nutrient to the total
                        if nutrient['title'] not in total_nutrients_df.index:
                            total_nutrients_df.loc[nutrient['title']] = [nutrient_qty,nutrient['unit']]
                        else:
                            total_nutrients_df.loc[nutrient['title'],'amount'] += nutrient_qty
    return total_nutrients_df.to_dict('index')





# This program converts between different measures (Tbps to gms, Ounces to litres etc..)
# It uses measures.json for the conversion
class Measure(object):
    measures_dict = read_write_json(json_path+measure_json_file,'r')

    def __init__(self, unit, val):
        self.val = val
        self.unit = unit
        self._parseAmount()
        
    def _parseAmount(self):
        unit = self.unit.lower()

        try:
            self.unit = self._getStandardUnit(unit)              
            if self.unit == 'not_found':
                raise ValueError()
                # return 0
        except ValueError:
            raise ValueError('%s is not a known type of measurement' % unit)

        try:
            self.count = float(self.val)
        except ValueError:
            raise ValueError('%s is not a valid number' % self.val)

    # Converts to a standard unit: Eg: tablespoon to tbsp; 
    def _getStandardUnit(self, unit):
        std_unit = 'not_found'
        for key,value in self.measures_dict.items():
            if unit in value['aka']:
                std_unit = key
        return std_unit

    # Converts from one unit to another: Eg: 1 tbps to 2 grams
    def convert(self, convert_to_unit, convert_to_value=1):
        self.convert_to_value = convert_to_value       
        convert_to_unit = convert_to_unit.lower()
            
        try:    
            self.convert_to_unit = self._getStandardUnit(convert_to_unit)
            if self.convert_to_unit == 'not_found':
                raise ValueError()
        except ValueError:
            raise ValueError("%s is not a valid unit I know how to convert %s to." % (convert_to_unit, self.unit))

        try:
            self.convert_to_count = float(self.convert_to_value)
        except ValueError:
            raise ValueError('%s is not a valid number' % self.convert_to_value)

        # are we already using the right unit
        if self.convert_to_unit == self.unit:
            self.converted = self.count/self.convert_to_count
            return self.converted
        else:
            try:
                if self.convert_to_unit in self.measures_dict[self.unit]['convert']:
                    self.convert_value = self.measures_dict[self.unit]['convert'][self.convert_to_unit]
                    self.converted = (self.convert_value * self.count)/self.convert_to_count
                    return self.converted
                else:
                    raise ValueError()
            except ValueError:
                raise ValueError("I don't know how to convert %s to %s " % (self.unit, convert_to_unit))


    def __unicode__(self):
        return "%s %s" % (self.count, self.unit)
        
    def __str__(self):
        return self.__unicode__()
        
    def __repr__(self):
        return self.__unicode__()


### Test Measure class
# p1 = Measure('tbs',1)
# print(p1)
# p2 = p1.convert('grams',2)
# print(p2)
