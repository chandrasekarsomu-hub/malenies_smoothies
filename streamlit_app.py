# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Get list of available fruits
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", pd_df["FRUIT_NAME"].tolist(), max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        
        if response.status_code == 200:
            fruityvice_data = response.json()
            st.json(fruityvice_data)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}.")
