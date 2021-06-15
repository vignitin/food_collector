# TBD:
# - assign unique id to each new food

import time
import os
from common import *

def update_food(new_food,index,row):
    print('Recipe %s: %s' % (index,new_food['title']))
    new_food['tags'] = row['Tags']
    new_food['categories'] = row['Category']
    new_food['total_nutrients'] = get_total_nutrients(new_food)
    if len(new_food['total_nutrients']) == 0:
        new_food['cals_per_serving'] = 0        
    elif 'servings' in new_food.keys():
        new_food['cals_per_serving'] = new_food['total_nutrients']['Calories']['amount']/new_food['servings']
    else:
        new_food['cals_per_serving'] = new_food['total_nutrients']['Calories']['amount']        
    new_food_df = pd.DataFrame.from_dict(new_food, orient='index')
    return new_food_df.transpose()

def update_food_data():
    newfood_json_file = 'food_v3.json'
    # Read food JSON file as a dataframe
    try:
        food_dict = read_write_json(json_path+food_json_file,'r')
    except FileNotFoundError:
        raise FileNotFoundError("%s file does not exist" % json_path+food_json_file)

    if ('tags' and 'categories' and 'cals_per_serving') not in food_dict[0].keys():
        # food_df = pd.DataFrame()
        food_df = pd.read_json(json_path+newfood_json_file)

        try:
            url_df = pd.read_csv(csv_path+url_csv_file,converters={'Tags': eval,'Category': eval})
        except FileNotFoundError:
            raise FileNotFoundError("%s file does not exist" % csv_path+url_csv_file)

        recipe_cols = [ 'RecipeURL','Category', 'Tags']

        # Iterate through the CSV rows
        for index,row in url_df[recipe_cols].iterrows():
            print(index)
            # Make sure that the recipe URL has www in it
            if 'www' not in url_df.loc[index,'RecipeURL']:
                row['RecipeURL'] = '//www.'.join(url_df['RecipeURL'][index].split('//'))

            for item in food_dict:
                if food_df.empty:
                    if (item['sourceUrl'] == row['RecipeURL']):
                        item.pop('total_nutrients')
                        new_food_df = update_food(item,index,row)
                        food_df = food_df.append(new_food_df, ignore_index=True)
                else:
                    food_row = food_df.loc[food_df['sourceUrl'] == item['sourceUrl']]
                    if ((item['sourceUrl'] == row['RecipeURL']) and (food_row.empty)):
                        item.pop('total_nutrients')
                        new_food_df = update_food(item,index,row)
                        food_df = food_df.append(new_food_df, ignore_index=True)
                        # print('Adding %s' % new_food_df['title'][0])
                # else:
                #     print(row['RecipeURL'], 'not found in food DB')
                #     continue
    food_df.to_json(json_path+newfood_json_file,orient='records',indent=4,double_precision=2,force_ascii=False)
    print('Writing to %s' % newfood_json_file)

def main():
    update_food_data()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))