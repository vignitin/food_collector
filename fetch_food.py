# import time
import os
from common import *

def add_new_food(api_recipe_url,index,row,food_id):
    new_food = fetch_api_data(api_recipe_url)
    print('Recipe %s: %s' % (index,new_food['title']))
    fetch_ing_data(new_food['extendedIngredients'])
    new_food['id'] = food_id
    new_food['tags'] = row['Tags']
    new_food['categories'] = row['Category']
    new_food['total_nutrients'] = get_total_nutrients(new_food)
    new_food['cals_per_serving'] = new_food['total_nutrients']['Calories']['amount']/new_food['servings']
    new_food_df = pd.DataFrame.from_dict(new_food, orient='index')
    return new_food_df.transpose()

def fetch_ing_data(all_ing):
    # Read ingredient JSON file as a dataframe or create a new dataframe 
    if os.path.isfile(json_path+ing_json_file):
        ing_df = pd.read_json(json_path+ing_json_file)
    else:
        ing_df = pd.DataFrame()

    for ing in all_ing:
        api_ing_url= api_base_url+'food/ingredients/'+str(ing['id'])+'/information?amount=1&apiKey='+api_key
        # If ingredient DB is empty
        if ing_df.empty:
            new_ing = fetch_api_data(api_ing_url)
            new_ing_df = pd.DataFrame.from_dict(new_ing, orient='index')
            new_ing_df = new_ing_df.transpose()
            # print(new_ing_df, new_ing_df.columns)
            ing_df = ing_df.append(new_ing_df, ignore_index=True)
            print('\tAdding %s' % new_ing_df['name'][0])
        else:
            ing_row = ing_df.loc[ing_df['id'] == ing['id']]
            # If ingredient is not in ingredient DB
            if ing_row.empty:
                new_ing = fetch_api_data(api_ing_url)
                new_ing_df = pd.DataFrame.from_dict(new_ing, orient='index')
                new_ing_df = new_ing_df.transpose()
                # print(new_ing_df, new_ing_df.columns)
                ing_df = ing_df.append(new_ing_df, ignore_index=True)
                print('\tAdding %s' % new_ing_df['name'][0])
            else:
                print('\tIngredient %s already in %s, continuing' % (ing['name'],ing_json_file))
                continue
    ing_df.to_json(json_path+ing_json_file,orient='records',indent=4,double_precision=2,force_ascii=False)
    print('Writing to %s' % ing_json_file)

def fetch_food_data():
    try:
        url_df = pd.read_csv(csv_path+url_csv_file,converters={'Tags': eval,'Category': eval})
    except FileNotFoundError:
        raise FileNotFoundError("%s file does not exist" % csv_path+url_csv_file)

    # Read food JSON file as a dataframe or create a new dataframe 
    if os.path.isfile(json_path+food_json_file):
        food_df = pd.read_json(json_path+food_json_file)
    else:
        food_df = pd.DataFrame()

    recipe_cols = [ 'RecipeURL','Category', 'Tags']

    # Iterate through the CSV rows
    for index,row in url_df[recipe_cols].iterrows():
        api_recipe_url = api_base_url+'recipes/extract?apiKey='+api_key+'&url='+row['RecipeURL']
        # Make sure that the recipe URL has www in it
        if 'www' not in url_df.loc[index,'RecipeURL']:
            row['RecipeURL'] = '//www.'.join(url_df['RecipeURL'][index].split('//'))
        # If food DB is empty
        if food_df.empty:
            food_id = 0
            new_food_df = add_new_food(api_recipe_url,index,row,food_id)
            food_df = food_df.append(new_food_df, ignore_index=True)
            print('\tAdding %s' % new_food_df['title'][0])
        else:
            food_row = food_df.loc[food_df['sourceUrl'] == row['RecipeURL']]
            # If recipe URL is not in food DB
            if food_row.empty:
                food_id = food_df.index[-1] + 1
                new_food_df = add_new_food(api_recipe_url,index,row,food_id)
                food_df = food_df.append(new_food_df, ignore_index=True)
                print('\tAdding %s' % new_food_df['title'][0])
            else:
                print('Recipe %s already in %s, continuing' % (row['RecipeURL'],food_json_file))
                continue
    food_df.to_json(json_path+food_json_file,orient='records',indent=4,double_precision=2,force_ascii=False)
    print('Writing to %s' % food_json_file)

def main():
    fetch_food_data()

if __name__ == '__main__':
    # start_time = time.time()
    main()
    # print("--- %s seconds ---" % (time.time() - start_time))