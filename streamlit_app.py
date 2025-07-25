# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Get list of available fruits
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
# Multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', pd_df["FRUIT_NAME"].tolist(),max_selections=5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
            st.subheader(fruit_chosen + ' Nutrition Information')
            #fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + str(search_on))
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        
    # Create SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
