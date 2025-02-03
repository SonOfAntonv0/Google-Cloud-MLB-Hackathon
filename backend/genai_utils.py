import google.generativeai as genai
import json
import re

genai.configure(api_key='AIzaSyAxlDjY7RTAfjWrzlEdnpuEFUiOUj9Pe54')

def is_convo_done(conversation_history_strs):

    conversation_history = '\n\n'.join(conversation_history_strs)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Construct a conversation prompt with session data
    prompt = f"""
    You are validating whether the following **conversation history** contains all required information for scheduling MLB highlight content.
    Each of the following details **must be present in some form**, even if paraphrased:

    1. **Selecting a team or player** (e.g., Shohei Ohtani, Yankees).
    - **If a player is selected**, a **specific highlight type** (e.g., home runs, strikeouts) must be provided.
    - **If a team is selected, highlight type is NOT required** (full-season highlights are assumed).
    2. **Selecting on-demand or scheduled delivery** (e.g., "Scheduled" or "On-demand").
    - **If on-demand is selected, frequency, time of day, and timezone are NOT required**.
    - Any user response confirming "on-demand" in a natural way (e.g., "on-demand is fine, confirm") should be accepted.
    3. **If scheduled**, confirming:
    - Frequency: **Daily, Hourly, or Weekly**.
    - **Time of day** (if applicable).
    - **Day of the week** (if applicable).
    - **Timezone** (e.g., CST, EST, GMT).
    4. **Preferred language**.
    5. **User's name and email**.

    ### **Instructions**
    - If **ALL required details** are present, return: **"yes <on-demand or scheduled>"**.
    - If **any detail is COMPLETELY MISSING**, return: **"no <with details>"**.
    - If a detail is phrased differently but is **logically present**, count it as valid.
    - If the user selects **on-demand**, ignore missing frequency, time of day, or timezone.
    - If any detail is ambigous but present in some form, count it as valid

    ### **Conversation History**
    {conversation_history}
    """

    response = model.generate_content([prompt])
    response.resolve()  
    text = response.candidates[0].content.parts[0].text
    clean_text = re.sub(r"[\n\t\r]", "", text)

    return clean_text


def get_params(conversation_history_strs):
    conversation_history = '\n\n'.join(conversation_history_strs)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Construct a conversation prompt with session data
    prompt = f"""
Based on the conversational history, return the following information as a JSON:

### **Required Fields**
1. **User's name** → Use `name` as the key.
2. **User's email** → Use `email` as the key.
3. **Selecting a team or player**:
   - **If a player is selected**, use `"player"` as the key and format the **last name only**, with the **first letter capitalized**.
   - **If a team is selected**, use `"team"` as the key (full team name in lowercase and snake-case).
4. **Choosing highlight types**:
   - Only required **if a player is chosen**.
   - Use `"play"` as the key.
   - Convert highlight types to **lowercase and snake-case** (e.g., `"home_runs"` instead of `"Home Runs"`).
5. **Selecting on-demand or scheduled delivery**:
   - Use `"delivery_type"` as the key.
   - If `"delivery_type"` is `"scheduled"`, also return:
     - `"frequency"` → Specify if it's `"daily"`, `"hourly"`, or `"weekly"`.
     - Also include `"time"` and `"day of week."` if applicable.  
     - `"timezone"` → **Must be in UTC format**.
6. **Preferred language**:
   - Use `"language"` as the key.
   - The value should be in **lowercase and snake-case**.

### **Strictly Mandatory Keys**
- Always include: `"name"`, `"email"`, `"delivery_type"`, `"language"`.
- If **player** is chosen: **Must include `"player"` and `"play"`**.
- If **team** is chosen: **Must include `"team"`**.
- If **delivery_type** is `"scheduled"`: **Must include `"frequency"` and `"timezone"`**.
- The `"time"` should be in 24 h format. for instance, 8 pm should be 20:00. 8 am should be 08:00
- The `"day of week"` should be an integer from 0-7, where 0 or 7 is Sunday, 1 is Monday, and so on.

### **IMPORTANT INSTRUCTION**
🚨 **Do NOT prefix with 'json' or enclose in triple backticks (` ``` `).**
🚨 **Ensure strict adherence to key requirements based on selection criteria.**

### **Conversation History**
{conversation_history}
"""
    response = model.generate_content([prompt])
    response.resolve()  
    json_response = json.loads(response.candidates[0].content.parts[0].text)

    print(f'json response is {json_response}')
    if 'play' in json_response.keys():
        if 'home' in json_response['play']:
            json_response['play'] = 'homeruns'
        elif 'strike' in json_response['play']:
           json_response['play'] = 'strikeout' 
        elif 'stolen' in json_response['play']:
           json_response['play'] = 'stolen_bases'  
        elif 'defensive' in json_response['play']:  
            json_response['play'] = 'defensive_plays'   
        

    else:
        if 'dodgers' in json_response['team'].lower():
            json_response['team'] = 'Dodgers'
        elif 'cubs' in json_response['team'].lower():
            json_response['team'] = 'Cubs'
        elif 'yankees' in json_response['team'].lower():
            json_response['team'] = 'Yankees'

    return json_response



def get_llm_response(conversation_history_strs):

    model = genai.GenerativeModel("gemini-1.5-flash")
    conversation_history = '\n\n'.join(conversation_history_strs)

    # Construct a conversation prompt with session data
    prompt = f"""
You are a conversational chatbot helping users subscribe to MLB content. 
Guide them through:
- Asking for the user's name and email first
- Selecting a team or player
- Choosing highlight types (if a player is selected) OR full-season highlights (if a team is selected)
- Selecting on-demand or scheduled delivery
- Setting frequency for scheduled content
- Picking a preferred language

**Handling Team vs. Player Selection:**
- **If the user selects a player**, ask them to choose a specific play highlight (e.g., home runs, strikeouts).
- **If the user selects a team**, assume they want **full-season highlights** for that team and do not ask for specific play highlights.

Maintain a friendly and engaging tone. Also, consider the previous responses from the user. Instruct the user to say that they confirm after having all the details

Ensure every single one of the above mentioned details have been asked and that user has responded. 

Previous Responses:
{conversation_history}
"""
    response = model.generate_content([prompt])
    response.resolve()  
    return response.candidates[0].content.parts[0].text