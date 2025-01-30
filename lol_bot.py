import os
import random
import pandas as pd
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import streamlit as st
from langchain_community.chat_models import ChatOpenAI  # correct import for chatopenai

# load environment variables
load_dotenv(".env")

# apply custom css to enhance ui
st.markdown(
    """
    <style>
        body {
            background-color: #0A74DA;
            color: white;
        }
        .stApp {
            text-align: center;
        }
        h1 {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# display league of legends logo
st.image("https://logos-world.net/wp-content/uploads/2020/11/League-of-Legends-Logo.png", width=800)

# load excel data
file_path = "League_of_legend_Champions_2024.xlsx"  # ensure this path is correct
try:
    data = pd.read_excel(file_path, sheet_name='League of legend Champions 2024')
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# remove unnecessary columns
data.drop(columns=['Nick Name', 'Release Date', 'Last Changed', 'Blue Essence', 'RP', 'Difficulty', 'Base HP', 'Base mana'], inplace=True, errors='ignore')
champions = data[['Name', 'Classes', 'Role', 'Range type', 'Resourse type']]
champion_names = set(champions['Name'].values)

# function to suggest a champion based on team composition
def suggest_champion(current_team: list) -> str:
    if not 1 <= len(current_team) <= 4:
        return "Please provide between 1 and 4 champions in your team."

    current_roles = set()
    for champ in current_team:
        champ_data = champions[champions['Name'] == champ.strip()]
        if not champ_data.empty:
            current_roles.add(champ_data['Role'].values[0])
    
    required_roles = {'Top', 'Jungle', 'Mid', 'AD Carry', 'Support'}
    missing_roles = required_roles - current_roles
    
    for role in missing_roles:
        available_champions = champions[champions['Role'] == role]
        if not available_champions.empty:
            return random.choice(available_champions['Name'].values)
    
    available_champions = champions[~champions['Name'].isin(current_team)]
    if not available_champions.empty:
        return random.choice(available_champions['Name'].values)
    
    return "No suitable champion found!"

# prompt template for item recommendation
template = """
You are a League of Legends expert. For the champion {champion}, list the best six items for them this season. Provide only a comma-separated list of items.

Answer:
"""

# initialize the language model
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.6)

# create llm chain
prompt = PromptTemplate(input_variables=['champion'], template=template)
chain = LLMChain(prompt=prompt, llm=llm)

# streamlit app setup
st.title("League of Legends Champion Suggestion Bot")

# text input for user to enter their team
current_team_input = st.text_input("Enter 1-4 champions from your team (comma-separated):")

# button to get champion suggestion
if st.button("Get Champion Suggestion"):
    current_team = [champ.strip() for champ in current_team_input.split(",") if champ.strip()]
    
    # validate champions
    if not all(champ in champion_names for champ in current_team):
        st.write("Invalid champion name(s) detected. Please enter valid League of Legends champion names.")
    elif 1 <= len(current_team) <= 4:
        suggested_champion = suggest_champion(current_team)
        st.write(f"Suggested Champion: {suggested_champion}")
        
        if suggested_champion and suggested_champion != "No suitable champion found!":
            champion_image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{suggested_champion}_0.jpg"
            st.image(champion_image_url, caption=suggested_champion, width=400)
            
            try:
                out = chain.invoke({'champion': suggested_champion})
                if isinstance(out, dict):
                    out_text = out.get('text', '')  # Extract text if it's a dictionary
                else:
                    out_text = str(out)
                st.write(f"Suggested Items: {out_text}")
            except Exception as e:
                st.write("An error occurred while getting suggestions from the model.")
                st.write(f"Error details: {e}")
    else:
        st.write("Please provide a valid input of 1 to 4 champions.")