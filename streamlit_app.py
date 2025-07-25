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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", my_dataframe, max_selections=5
)

# Handle order submission
if ingredients_list:
    # Combine selected ingredients into a string
    ingredients_string = " ".join(ingredients_list)
    st.write("Selected ingredients:", ingredients_string)

    # Create SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

    # Display nutrition info for each selected fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            response.raise_for_status()  # Raise an error for bad status
            data = response.json()
            st.dataframe(data=data, use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")
        except ValueError:
            st.error("Could not parse API response as JSON.")
