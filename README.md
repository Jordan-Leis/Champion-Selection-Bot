# League of Legends Champion Suggestion Bot

This bot suggests a champion for your League of Legends team based on the champions already selected and provides a recommended six-item build for that champion using OpenAI's GPT-3.5. The bot ensures balanced team composition and item suggestions tailored to the champion's playstyle and the current meta.

## Features

- **Champion Suggestion**: Enter 1-4 champions already on your team, and the bot will suggest a champion to complement the team's roles, classes, and resource types.
- **Item Build Recommendation**: After suggesting a champion, the bot will generate a list of six items recommended for that champion based on their role and playstyle.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Required Python libraries: 
  - `pandas`
  - `openai`
  - `langchain`
  - `streamlit`
  - `python-dotenv`

### Installation

1. Clone the repository and navigate to the project directory:

   ```bash
   git clone https://github.com/your-repo-url.git
   cd your-repo-directory

2. Install the required dependencies:

  ```bash
     Copy code
     pip install pandas openai langchain streamlit python-dotenv

3. Set up your environment variables:

Create a .env file in the project directory, add your OpenAI API key to the .env file


4. Ensure the League_of_legend_Champions_2024.xlsx file is available in the project directory, or update the file_path in the script accordingly.

### Running the Bot
Use streamlit run your_script_name.py


### How to Use
Input: Enter 1-4 champions currently on your team in the text box. Ensure each champion is comma-separated.

Champion Suggestion: Click the "Get Champion Suggestion" button to receive a recommended champion based on the current team composition.

Item Build: The bot will provide a six-item build for the recommended champion, including only valid items that fit the champion's role.
