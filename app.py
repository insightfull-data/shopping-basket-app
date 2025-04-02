import streamlit as st
import pandas as pd
import random
from faker import Faker
from datetime import datetime

fake = Faker("en_CA")

# Define cities & regions
city_region_map = {
    "Toronto": "Ontario",
    "Vancouver": "British Columbia",
    "Montreal": "Quebec",
    "Calgary": "Alberta",
    "Halifax": "Nova Scotia",
    "Winnipeg": "Manitoba",
    "Regina": "Saskatchewan",
    "Ottawa": "Ontario",
    "Quebec City": "Quebec",
    "St. John's": "Newfoundland and Labrador",
}
cities = list(city_region_map.keys())

# Demographic bins
age_bins = [(18, 25), (26, 35), (36, 50), (51, 65), (66, 80)]
genders = ["Male", "Female", "Non-binary"]
income_brackets = ["<40K", "40K–70K", "70K–100K", "100K+"]

# Product catalog
products = [
    {"item": "Milk", "category": "Dairy", "price": 3.49},
    {"item": "Bread", "category": "Bakery", "price": 2.99},
    {"item": "Eggs", "category": "Dairy", "price": 4.99},
    {"item": "Apples", "category": "Produce", "price": 1.29},
    {"item": "Bananas", "category": "Produce", "price": 0.79},
    {"item": "Chicken Breast", "category": "Meat", "price": 6.49},
    {"item": "Toilet Paper", "category": "Household", "price": 5.99},
    {"item": "Shampoo", "category": "Personal Care", "price": 4.50},
    {"item": "Orange Juice", "category": "Beverages", "price": 3.99},
    {"item": "Chips", "category": "Snacks", "price": 2.49},
]

# Generate respondents
def generate_respondents(n):
    respondents = []
    for i in range(n):
        city = random.choice(cities)
        region = city_region_map[city]
        age_range = random.choice(age_bins)
        age = random.randint(*age_range)
        gender = random.choice(genders)
        income = random.choices(income_brackets, weights=[0.2, 0.4, 0.3, 0.1])[0]
        respondents.append({
            "respondent_id": i + 1,
            "age": age,
            "gender": gender,
            "income_bracket": income,
            "city": city,
            "region": region
        })
    return pd.DataFrame(respondents)

# Generate baskets with regional retailer logic
def generate_basket(row, max_items=10):
    region_retailer_map = {
        "Ontario": ["Loblaws", "No Frills", "FreshCo", "Shoppers Drug Mart"],
        "Quebec": ["Metro", "IGA", "Costco"],
        "British Columbia": ["Superstore", "Walmart", "Costco"],
        "Alberta": ["Superstore", "Walmart", "Sobeys"],
        "Nova Scotia": ["Sobeys", "Superstore"],
        "Manitoba": ["Superstore", "Walmart"],
        "Saskatchewan": ["Superstore", "Canadian Tire"],
        "Newfoundland and Labrador": ["Sobeys", "Walmart"]
    }

    age = row["age"]
    income = row["income_bracket"]
    region = row["region"]

    if income == "100K+":
        num_items = random.randint(5, max_items)
    elif income == "<40K":
        num_items = random.randint(1, 5)
    else:
        num_items = random.randint(3, 8)

    product_pool = products.copy()
    if region == "Quebec":
        product_pool += [{"item": "Cheese", "category": "Dairy", "price": 5.99}]
    if age < 30:
        product_pool += [{"item": "Energy Drink", "category": "Beverages", "price": 2.99}]

    basket = []
    selected = random.sample(product_pool, min(num_items, len(product_pool)))
    retailers = region_retailer_map.get(region, ["Walmart"])
    retailer = random.choice(retailers)
    transaction_id = fake.uuid4()
    timestamp = fake.date_time_between(start_date="-30d", end_date="now")

    for item in selected:
        quantity = random.randint(1, 3)
        total_price = round(quantity * item["price"], 2)
        basket.append({
            "transaction_id": transaction_id,
            "timestamp": timestamp,
            "respondent_id": row["respondent_id"],
            "retailer": retailer,
            "item": item["item"],
            "category": item["category"],
            "unit_price": item["price"],
            "quantity": quantity,
            "total_price": total_price
        })
    return basket

# Streamlit app
st.title("Synthetic Shopping Basket Generator 🇨🇦")
st.markdown("Generate realistic Canadian shopping basket data with demographics, region, and retailer logic.")

num_respondents = st.slider("Number of Respondents", 100, 2000, 500, step=50)

if st.button("Generate Data"):
    respondents_df = generate_respondents(num_respondents)
    basket_data = []

    for _, respondent in respondents_df.iterrows():
        basket_data.extend(generate_basket(respondent))

    basket_df = pd.DataFrame(basket_data)
    final_df = basket_df.merge(respondents_df, on="respondent_id")

    st.success("✅ Data Generated!")
    st.dataframe(final_df.head(20))

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "synthetic_baskets.csv", "text/csv")
