import os
import random
import pandas as pd
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import streamlit as st
from langchain_community.chat_models import ChatOpenAI  # Correct import for ChatOpenAI


load_dotenv(".env")


file_path = "League_of_legend_Champions_2024.xlsx"  # Update this path as needed
try:
    data = pd.read_excel(file_path, sheet_name='League of legend Champions 2024')
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()


data.drop(columns=['Nick Name', 'Release Date', 'Last Changed', 'Blue Essence', 'RP', 'Difficulty', 'Base HP', 'Base mana'], inplace=True, errors='ignore')
champions = data[['Name', 'Classes', 'Role', 'Range type', 'Resourse type']]


valid_items = [
    # none rn while testing
]

def filter_invalid_items(item_list):
    return [item.strip() for item in item_list if any(valid_item.lower() in item.lower() for valid_item in valid_items)]


def process_output(output_text):
    suggested_items = [item.strip() for item in output_text.split(',')]
    filtered_items = filter_invalid_items(suggested_items)
    return ', '.join(filtered_items) if filtered_items else "The model suggested invalid items. Please try again."


def suggest_champion(current_team: list) -> str:
    if not 1 <= len(current_team) <= 4:
        return "Please provide between 1 and 4 champions in your team."

    current_roles = set()
    current_classes = {'AD': 0, 'MD': 0}
    current_range_types = {'Melee': 0, 'Ranged': 0}
    current_resource_types = set()

    for champ in current_team:
        champ_data = champions[champions['Name'] == champ.strip()]
        if not champ_data.empty:
            current_roles.add(champ_data['Role'].values[0])
            classes = champ_data['Classes'].values[0].split(', ')
            for c in classes:
                if 'AD' in c:
                    current_classes['AD'] += 1
                if 'MD' in c:
                    current_classes['MD'] += 1
            current_range_types[champ_data['Range type'].values[0]] += 1
            current_resource_types.add(champ_data['Resourse type'].values[0])

    required_roles = {'Top', 'Jungle', 'Mid', 'AD Carry', 'Support'}
    for role in required_roles:
        if role not in current_roles:
            available_champions = champions[champions['Role'] == role]
            if not available_champions.empty:
                if current_classes['AD'] < 3:
                    available_champions = available_champions[available_champions['Classes'].str.contains('AD')]
                elif current_classes['MD'] < 3:
                    available_champions = available_champions[available_champions['Classes'].str.contains('MD')]

                if not available_champions.empty:
                    return random.choice(available_champions['Name'].values)

    available_champions = champions[~champions['Name'].isin(current_team)]
    if not available_champions.empty:
        return random.choice(available_champions['Name'].values)
    
    return "No suitable champion found!"


template = """
You are a League of Legends expert. For the champion {champion}, think about the best six items they should use in the most recent season. Consider the following for each item:

1. The item name.
2. Why this item is a good fit for the champion based on their role and playstyle.
3. How this item helps against different types of opponents or team compositions.

Please only provide a comma-separated list of all 6 items. No justifications are needed.

Answer:
"""

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.6)  # Updated LLM initialization

prompt = PromptTemplate(input_variables=['champion'], template=template)
chain = LLMChain(prompt=prompt, llm=llm)

# Streamlit app
st.title("League of Legends Champion Suggestion Bot")

# User input
current_team_input = st.text_input("Enter 1-4 champions from your team (comma-separated):")

if st.button("Get Champion Suggestion"):
    # Split the input string into a list, strip whitespace, and filter out empty strings
    current_team = [champ.strip() for champ in current_team_input.split(",") if champ.strip()]

    if 1 <= len(current_team) <= 4:
        suggested_champion = suggest_champion(current_team)
        st.write(f"Suggested Champion: {suggested_champion}")

        if suggested_champion and suggested_champion != "No suitable champion found!":
            question = f"What would be good items for {suggested_champion} in League of Legends most recent season?"
            st.write(f"Sending question to LLM: {question}")

            try:
                # Invoke the LLMChain with the correct input variable
                out = chain.invoke({'champion': suggested_champion})

                # Process the output to filter invalid items
                processed_items = process_output(out)
                st.write(f"Suggested Items: {processed_items}")

            except Exception as e:
                st.write("An error occurred while getting suggestions from the model.")
                st.write(f"Error details: {e}")
        else:
            st.write("No suitable champion found!")
    else:
        st.write("Please provide a valid input of 1 to 4 champions.")
