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
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Build ingredients string and show nutrition info
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get nutrition info from Fruityvice API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

# Submit order if data is valid
if ingredients_string.strip() and name_on_order:
    try:
        order_data = [(name_on_order, ingredients_string.strip())]

        order_df = session.create_dataframe(
            order_data,
            schema=["NAME_ON_ORDER", "INGREDIENTS"]
        )

        # Debug info (optional)
        # st.write("Order DataFrame preview:")
        # order_df.show()

        # Safely insert into existing table
        order_df.write.insert_into("smoothies.public.orders")

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

    except Exception as e:
        st.error(f"Error inserting order: {e}")
else:
    st.warning("Please enter a name and select at least one ingredient.")
