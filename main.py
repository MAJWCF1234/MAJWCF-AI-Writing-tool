
# Importing necessary libraries
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import openai  # Make sure to install the OpenAI package
import re
import os
import json
import time

# Initialize story variables
story = ""
story_summary = ""
story_length = 0
game_story = ""


# Function to extract the last 20 sentences from the story
def extract_last_20_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    context = " ".join(sentences[-20:])
    return context

def rate_limited_request(interval):
    """Sleeps for 'interval' seconds between function calls."""
    time.sleep(interval)

# Function to generate story content
def generate_story_content(prompt, plot=None):
    global story, story_length

    api_key = api_key_var.get()
    openai.api_key = api_key

    context = extract_last_20_sentences(story)
    first_iteration = True

    word_goal = int(word_goal_var.get())  # Get the word goal from the Entry widget

    while story_length < word_goal:
        messages = [
            {"role": "system", "content": "Narrative Style: Limited third-person, following the character closely. Focus solely on character thoughts, feelings, and actions. Keep the story moving forward, and avoid restarting the story or changing points of view. The story should be open for continuation."},
        ]

        if first_iteration:
            messages.append({"role": "user", "content": f"Based on the plot '{plot}', {prompt}"})
        else:
            messages.append({"role": "user", "content": f"Continue the story based on the following context: {context}"})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000
        )

        generated_text = response['choices'][0]['message']['content'].strip()

        # Update story and word count
        story += generated_text + "\n"
        story_length += len(generated_text.split())
        update_word_count()

        # Update the context for the next iteration
        context = extract_last_20_sentences(story)
        first_iteration = False

        # Add a delay to avoid hitting rate limits
        rate_limited_request(1)  # 1 second delay

    scrolled_text.insert(tk.END, story)
    scrolled_text.update()
    return story, story_length


# Function to continue the story
def continue_story():
    global story, story_length  # Make sure you're using the global variables

    # Initialize a variable to keep track of the number of words generated in this session
    words_generated = 0

    while words_generated < 5000:  # Loop to generate approximately 5,000 more words
        # Extract the last 20 sentences as context
        context = extract_last_20_sentences(story)

        # Create the message structure for API call
        messages = [
            {"role": "system", "content": "You are a creative writing assistant."},
            {"role": "user", "content": "Continue the story where it leaves off. Focus on dialogue, thoughts, emotions, and actions."},
            {"role": "assistant", "content": context}
        ]

        api_key = api_key_var.get()  # Replace this with how you fetch the API key
        openai.api_key = api_key  # Set the API key

        # Make the API call to continue the story
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use other models as well
            messages=messages,
            max_tokens=1000  # Set the max tokens
        )

        generated_text = response['choices'][0]['message']['content'].strip()

        # Update story and word count
        story += "\n" + generated_text
        new_words = len(generated_text.split())
        story_length += new_words
        words_generated += new_words

        # Update the word count
        update_word_count()

        # Insert only the newly generated part into the scrolled text box
        scrolled_text.insert(tk.END, generated_text)

        # A delay to avoid rate limits (optional)
        time.sleep(1)

    print("Story continuation complete.")  # Debugging print



# Function to end the story
def end_story():
    global story, story_length  # Make sure you're using the global variables
    print("Starting to end the story...")  # Debugging print

    # Extract the last 20 sentences as context for a coherent ending
    context = extract_last_20_sentences(story)  # You need to define extract_last_20_sentences

    # Initialize a variable to keep track of the number of words generated in this session
    words_generated = 0

    # Prepare the message for the AI model
    messages = [
        {"role": "system", "content": "Narrative Style: Limited third-person, following the character closely. Focus on dialogue, thoughts, emotions, and actions."},
        {"role": "assistant", "content": context},
        {"role": "user", "content": "And so, the story comes to a close. Please write a fitting ending based on the previous context."}
    ]

    # Make the API call to GPT-3 to generate the ending
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Replace with the model you're using
        messages=messages,
        max_tokens=200  # Limit the tokens to generate a concise ending
    )

    generated_ending = response['choices'][0]['message']['content'].strip()

    # Update the story and word count
    story += "\n" + generated_ending
    new_words = len(generated_ending.split())
    story_length += new_words
    words_generated += new_words

    # You need to define the update_word_count function
    update_word_count()

    # Insert the generated ending into the scrolled text box (you need to define this)
    scrolled_text.insert(tk.END, generated_ending)

    print("Story ending complete.")  # Debugging print


# Function to update word count
def update_word_count():
    global story_length
    word_count_label.config(text=f"Word Count: {story_length}")

# Function to save the story to a text file
def save_to_txt():
    global story
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(story)

# Initialize an empty conversation history
conversation_history = [{"role": "system", "content": "You are a friendly girl who loves to write. You speak in a casual and engaging manner, more like a friend than a machine."}]

def send_chat_message():
    global conversation_history  # Declare it as global so that we can modify it
    
    # Capture User Input
    user_input = chat_input_var.get()

    # Append user's message to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Generate AI Response using OpenAI API
    openai.api_key = api_key_var.get()
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=conversation_history
    )
    
    ai_output = response['choices'][0]['message']['content']

    # Append AI's message to the conversation history
    conversation_history.append({"role": "assistant", "content": ai_output})

    # Update Chat History
    chat_history.insert(tk.END, f"You: {user_input}\n")
    chat_history.insert(tk.END, f"AI: {ai_output}\n")

def save_conversation():
    # Extract text from chat_history
    conversation_text = chat_history.get("1.0", tk.END)
    
    # Write the text to a file
    with open("saved_conversation.txt", "w") as f:
        f.write(conversation_text)
    
    print("Conversation saved.")



def generate_idea():
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Generate a unique 3-sentence story idea."}
    ]
    max_tokens = 50  # Limiting to approximately 3 sentences

    # Use GPT-3.5-turbo for the chat-based API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=max_tokens,
            api_key=api_key_var.get()  # Assuming you have stored API key in a tkinter StringVar
        )
        generated_idea = response['choices'][0]['message']['content'].strip()
        
        # Update the shared text widget with the generated idea
        shared_text.insert(tk.END, f"Idea: {generated_idea}\n")
    
    except Exception as e:
        shared_text.insert(tk.END, f"An error occurred: {e}\n")
import openai

def generate_name():
    details = name_details_var.get()
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Generate 20 character names based on these details: {details}"}
    ]
    max_tokens = 200  # Estimating enough tokens for 20 names

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=max_tokens,
            api_key=api_key_var.get()  # Assuming you have stored API key in a tkinter StringVar
        )
        generated_names = response['choices'][0]['message']['content'].strip().split('\n')

        # Update the shared text widget with the generated names
        for name in generated_names:
            shared_text.insert(tk.END, f"Name: {name}\n")

    except Exception as e:
        shared_text.insert(tk.END, f"An error occurred: {e}\n")


def generate_character_sheet():
    details = name_details_var.get()  # Fetch details from the input box
    print(f"Received details: {details}")  # Debugging print
    
    # Base message without details
    user_message = "Generate a character sheet with the following format:"
    
    # If details are provided, include them in the prompt
    if details:
        user_message = f"Generate a character sheet based on these details: {details}. The format is:"
    
    messages = [
        {"role": "system", "content": "You are a creative writing assistant specialized in generating character sheets."},
        {"role": "user", "content": user_message},
        {"role": "user", "content": """
        Please fill out each of the following fields to create a complete character profile by generating a character:
        Ultimate Character Sheet
        -------------------------
        General Information
        -------------------
        Full Name:
        Nicknames (Optional):
        Age:
        Birthday:
        Gender:
        Sex:
        Sexuality:
        Race/Species:
        Social Class (Optional):
        Occupation/Job:
        Hometown:
        Current Residence:
        Education Level:
        Languages Spoken:

        Physical Traits
        ---------------
        Height:
        Weight:
        Hair Color:
        Eye Color:
        Skin Color:
        Body Details (Tattoos, scars, etc.):
        Physical Build (Muscular, slim, etc.):
        Dick Size/Breast Size:
        Ass Size (Plump, flat, etc.):

        Powers & Abilities
        -----------------
        Skills:
        Abilities:
        Special Powers (if any):
        Combat Style:
        Equipment/Inventory:
        Weapon(s):
        Armor/Clothing:
        Other Items:
        Weaknesses:
        Physical Conditions (Any illnesses, etc.):

        Personality & Mental Traits
        ---------------------------
        Overall Personality:
        Five Key Personality Traits:
        Likes:
        Dislikes:
        Turn-Ons/Kinks:
        Turn-Offs:
        Role (Dom/Sub, Top/Bottom, etc.):
        Mental Disorders/Illnesses:
        Insecurities:
        Habits:
        Fears/Phobias:
        Aspirations:
        Regrets:
        Favorite Food:
        Least Favorite Food:
        Favorite Color:
        Least Favorite Color:

        Background & Lore
        ----------------
        Bio/Backstory:
        About Their Family:
        Key Events that Shaped Them:
        Goals/Motivations:
        Allies/Enemies:
        Personal Achievements:
        Personal Failures:

        Extras
        ------
        Personal Facts:
        Limits:
        Relationship Status (Optional):
        Pets (if any):
        Hobbies:
        Talents:
        """}
      
    ]
    
    # Here you'd make the API call to GPT-3
    model_engine = "gpt-3.5-turbo"
    api_key = api_key_var.get()  # Get the API key from the user
    
    openai.api_key = api_key  # Set the API key
    
    # Make the API call
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages
    )
    
    generated_character_sheet = response['choices'][0]['message']['content']  # Extracting the generated text from the API response
    
    if generated_character_sheet:
        print("Received character sheet from API.")  # Debugging print
    else:
        print("Received empty character sheet from API.")  # Debugging print
    
    # Update the shared text widget with the generated character sheet
    shared_text.insert(tk.END, f"Character Sheet:\n{generated_character_sheet}\n")

# Function to clear the main text field, reset the story, word count, and context
def clear_story_and_reset():
    global story, story_length  # Access the global story and story_length variables

    # Clear the scrolled_text widget
    scrolled_text.delete('1.0', tk.END)

    # Reset the global story and story_length variables
    story = ""
    story_length = 0

    # Reset the word count label
    word_count_label.config(text="Word Count: 0")

    print("Story and context cleared.")  # Debugging print



# Initialize global variables
game_text = ""
game_word_count = 0
is_initialized = False 
game_history = [
    {"role": "system", "content": "You are a third person text-based adventure game formatted like a novel.  The user will send an input which will be treated like a continuation of this story. And you continue where they leave off. Your role is to describe the world, the outcomes of the player's actions. Never ask them to choose."}
]



# Function to save game state
def save_game_state():
    global game_text

    if not os.path.exists('game_saves'):
        os.makedirs('game_saves')

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir='./game_saves', title="Save game", filetypes=[("Text files", "*.txt")])

    if file_path:
        with open(file_path, 'w') as f:
            f.write(game_text)
        print(f"Game saved to {file_path}")

# Function to clear the game state
def clear_game_state():
    global game_text
    game_text = ""
    output_scrolled_text.delete("1.0", tk.END)
    print("Game state cleared.")

def call_ai_to_generate(prompt):
    global game_history
    
    print("Before API call, game history is:", game_history)
    
    api_key = api_key_var.get()
    openai.api_key = api_key
    
    game_history.append({"role": "user", "content": prompt})
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=game_history)
    
    assistant_reply = response['choices'][0]['message']['content'].strip()
    game_history.append({"role": "assistant", "content": assistant_reply})
    
    print("After API call, game history is:", game_history)
    
    return assistant_reply


def initialize_game():
    global is_initialized
    # No scenario generation here, just setting the flag
    is_initialized = True


def send_command():
    global game_text, game_word_count, is_initialized

    user_input = user_input_text.get("1.0", tk.END).strip()
    
    print(f"Debug: User Input is '{user_input}'")

    if not is_initialized:
        initialize_game()
    
    game_text += f"{user_input}\n"
    
    generated_text = call_ai_to_generate(user_input)
    game_text += f"{generated_text}\n"
    
    game_word_count += len(user_input.split()) + len(generated_text.split())
    
    output_scrolled_text.delete('1.0', tk.END)
    output_scrolled_text.insert(tk.END, game_text)
    user_input_text.delete("1.0", tk.END)


def generate_game_scenario():
    global game_text
    game_scenario = call_ai_to_generate("Begin a new story like the start of a novel.")
    game_text = f"{game_scenario}\n"
    
    output_scrolled_text.delete('1.0', tk.END)
    output_scrolled_text.insert(tk.END, game_text)




# Generate game scenario
def generate_game_scenario():
    global game_text
    # Prompt the assistant to generate a new beginning like that of a novel
    game_scenario = call_ai_to_generate("Begin a new story like the start of a novel.")
    # Add this generated text to game_text without any label
    game_text = f"{game_scenario}\n"
    
    # Clear and update the output text box with this new game scenario
    output_scrolled_text.delete('1.0', tk.END)
    output_scrolled_text.insert(tk.END, game_text)



def save_lore_book_to_json():
    with open('lore_book.json', 'w') as f:
        json.dump(lore_book, f)
    print("Lore book saved to lore_book.json.")
def load_lore_book_from_json():
    global lore_book  # Declare as global to modify it
    try:
        with open('lore_book.json', 'r') as f:
            lore_book = json.load(f)
        print("Lore book loaded from lore_book.json.")
    except FileNotFoundError:
        print("No existing lore book found. Starting with a new one.")

def save_lore_book_to_file():
    with open('lore_book.json', 'w') as f:
        json.dump(lore_book, f)
    print("Lore book saved.")

def load_lore_book_from_file():
    global lore_book  # Declare as global if it is
    try:
        with open('lore_book.json', 'r') as f:
            lore_book = json.load(f)
    except FileNotFoundError:
        print("Lore book not found, starting with a blank slate.")
        lore_book = {'World': '', 'Characters': [], 'Settings': [], 'Items': [], 'Events': []}
def on_closing():
    save_lore_book_to_json()  # or save_lore_book_to_file, whichever you prefer
    root.destroy() 


# Initialize lore_book
lore_book = {'Characters': [], 'Settings': [], 'Items': [], 'Events': []}
load_lore_book_from_json()



current_category = "Characters"

# Functions
def show_category(category):
    global current_category
    current_category = category
    main_display.delete('1.0', tk.END)
    for entry in lore_book[category]:
        main_display.insert(tk.END, entry + "\n\n")

def create_new_entry():
    new_entry = main_display.get('1.0', tk.END).strip()
    if new_entry:  # Don't add empty entries
        lore_book[current_category].append(new_entry)
        show_category(current_category)  # This will refresh the displayed entries

def save_lore_to_txt():
    with open('lore_book.txt', 'w') as f:
        for category, entries in lore_book.items():
            f.write(f"=== {category} ===\n")
            for entry in entries:
                f.write(entry + "\n\n")

def generate_lore_entry(category, prompt, world_description):  # Merged the two functions into one
    api_key = api_key_var.get()
    openai.api_key = api_key
    
    full_prompt = f"In a world where {world_description}, {prompt}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )
    generated_entry = response['choices'][0]['message']['content'].strip()
    return generated_entry

def generate_world_description():
    api_key = api_key_var.get()
    openai.api_key = api_key
    
    prompt = "Generate a description of a coherent fantasy world:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    world_description = response['choices'][0]['message']['content'].strip()
    lore_book['World'] = world_description

def generate_lore_book():
    categories = ['Characters', 'Settings', 'Items', 'Events']
    prompts = {
        'Characters': "generate a character description.",
        'Settings': "describe a setting.",
        'Items': "describe an item.",
        'Events': "describe an event."
    }

    # First, generate the world description
    generate_world_description()
    world_description = lore_book['World']

    # Loop through each category and generate 10 entries
    for category in categories:
        for _ in range(10):
            prompt = prompts[category]
            generated_entry = generate_lore_entry(category, prompt, world_description)
            
            # Append only if the generated entry is not already in the lore_book
            if generated_entry not in lore_book[category]:
                lore_book[category].append(generated_entry)

    print("Lore book generated.")


def clear_lore_book():
    global lore_book
    lore_book = {
        "Characters": [],
        "Settings": [],
        "Items": [],
        "Events": []
    }
    main_display.delete('1.0', tk.END)



# Tkinter setup
root = tk.Tk()
root.title("Story Writer")
root.option_add('*theme', 'light')
tab_control = ttk.Notebook(root)
style = ttk.Style(root)
load_lore_book_from_file()
root.protocol("WM_DELETE_WINDOW", on_closing)
word_goal_var = tk.StringVar()
def change_widget_colors(root, fg, bg, frame_bg):
    for widget in root.winfo_children():
        widget_type = widget.winfo_class()
        if widget_type in ("Button", "Label", "Text", "Entry"):
            widget.config(foreground=fg, background=bg)
        if widget_type == 'Frame' or widget_type == 'TFrame':
            widget.config(background=frame_bg)  # Change background color of frames
            change_widget_colors(widget, fg, bg, frame_bg)  # Recursive call to change colors in children

def toggle_theme():
    global frame, frame_discussion, frame_tools, frame_script_unbound, frame_settings  # Declare frames as global if they are

    if root.option_get('theme', 'light') == 'light':
        root.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
        style.theme_use('clam')
        style.configure('TButton', foreground='#FFFFFF', background='#555555')
        style.configure('TLabel', foreground='#FFFFFF', background='#2E2E2E')
        root.option_add('*theme', 'dark')
        root.config(bg='#2E2E2E')  # Change root background to dark gray
        # Update Canvas background color
        frame.config(bg='#1E1E1E')  # Change canvas background to darker gray
        frame_discussion.config(bg='#1E1E1E')
        frame_tools.config(bg='#1E1E1E')
        frame_script_unbound.config(bg='#1E1E1E')
        frame.config(bg='#1E1E1E')  
        frame_discussion.config(bg='#1E1E1E')
        frame_tools.config(bg='#1E1E1E')
        frame_script_unbound.config(bg='#1E1E1E')
        frame_settings.config(bg='#1E1E1E')
    else:
        root.tk_setPalette(background='#FFFFFF', foreground='#000000')
        style.theme_use('default')
        style.configure('TButton', foreground='#000000', background='#DDDDDD')
        style.configure('TLabel', foreground='#000000', background='#FFFFFF')
        root.option_add('*theme', 'light')
        root.config(bg='#FFFFFF')  # Change root background to white
        # Update Canvas background color
        frame.config(bg='#FFFFFF')  # Change canvas background to white
        frame_discussion.config(bg='#FFFFFF')
        frame_tools.config(bg='#FFFFFF')
        frame_script_unbound.config(bg='#FFFFFF')
 # Reset to light gray for frames
        frame.config(bg='#DDDDDD')  
        frame_discussion.config(bg='#DDDDDD')
        frame_tools.config(bg='#DDDDDD')
        frame_script_unbound.config(bg='#DDDDDD')
        frame_settings.config(bg='#DDDDDD')

# Main tab
frame = tk.Canvas(tab_control, bg='#FFFFFF')
tab_control.add(frame, text="Main")

# Story discussion tab
frame_discussion = tk.Canvas(tab_control, bg='#FFFFFF')
tab_control.add(frame_discussion, text="Story Discussion")

# Tools tab
frame_tools = tk.Canvas(tab_control, bg='#FFFFFF')
tab_control.add(frame_tools, text="Tools")

# Script Unbound tab
frame_script_unbound = tk.Canvas(tab_control, bg='#FFFFFF')
tab_control.add(frame_script_unbound, text="Script Unbound")

# Lore Book tab
frame_lore_book = tk.Canvas(tab_control, bg='#FFFFFF')  # White background by default
tab_control.add(frame_lore_book, text="Lore Book")

# Settings tab
frame_settings = tk.Canvas(tab_control, bg='#FFFFFF')
tab_control.add(frame_settings, text="Settings")

tab_control.pack(expand=1, fill="both")



# Populate Main tab (This is where your original widgets go)
ttk.Label(frame, text="Enter Plot:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W)
plot_var = tk.StringVar()
api_key_var = tk.StringVar()  # Add this line for API key
# Entry box for API key
ttk.Label(frame, text="Enter API Key:", font=("Arial", 14)).grid(row=1, column=0, sticky=tk.W)
ttk.Label(frame, text="API Key:", font=("Arial", 14)).grid(row=4, column=0, sticky=tk.W)
api_key_entry = ttk.Entry(frame, textvariable=api_key_var, font=("Arial", 14), width=40)
api_key_entry.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
plot_entry = ttk.Entry(frame, textvariable=plot_var, font=("Arial", 14), width=40)
plot_entry.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
generate_button = ttk.Button(frame, text="Generate",  command=lambda: generate_story_content(plot_var.get(), api_key_var.get()))
generate_button.grid(row=0, column=2)
continue_button = ttk.Button(frame, text="Continue Story", command=continue_story, width=20)
continue_button.grid(row=0, column=3)
end_button = ttk.Button(frame, text="End Story", command=end_story, width=20)
end_button.grid(row=1, column=3)
scrolled_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20, font=("Arial", 14))
scrolled_text.grid(row=1, columnspan=3)
word_count_label = ttk.Label(frame, text="Word Count: 0", font=("Arial", 14))
word_count_label.grid(row=2, column=0, sticky=tk.W)
save_button = ttk.Button(frame, text="Save to TXT", command=save_to_txt)
save_button.grid(row=4, column=2)
# Adding the Clear Button in the UI
clear_button = ttk.Button(frame, text="Clear", command=clear_story_and_reset, width=20)
clear_button.grid(row=0, column=4)

# Create a label for word goal
word_goal_label = ttk.Label(frame, text="Enter Word Goal:", font=("Arial", 14))
word_goal_label.grid(row=5, column=0, sticky=tk.W)

# Create an Entry widget for word goal input
word_goal_entry = ttk.Entry(frame, textvariable=word_goal_var, font=("Arial", 14), width=40)
word_goal_entry.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))


# Populate Story Discussion tab
# Text variable for user input
chat_input_var = tk.StringVar()
# Text entry box for user input
chat_entry = ttk.Entry(frame_discussion, textvariable=chat_input_var, font=("Arial", 14), width=40)
chat_entry.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
# Chat button to send the message
chat_button = ttk.Button(frame_discussion, text="Chat", command=send_chat_message, width=20)
chat_button.grid(row=0, column=1)
# Text area to display the conversation history
chat_history = scrolledtext.ScrolledText(frame_discussion, wrap=tk.WORD, width=60, height=20, font=("Arial", 14))
chat_history.grid(row=1, columnspan=2)
# Save Conversation button
save_convo_button = ttk.Button(frame_discussion, text="Save Conversation", command=save_conversation, width=20)
save_convo_button.grid(row=2, column=0)


# Label for Input
ttk.Label(frame_tools, text="Input:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W)
# Entry box for Input
name_details_var = tk.StringVar()
input_entry = ttk.Entry(frame_tools, textvariable=name_details_var, font=("Arial", 14), width=30)
input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

# Buttons for Idea, Name, and Character Sheet
idea_button = ttk.Button(frame_tools, text="Generate Idea", command=generate_idea)
idea_button.grid(row=1, column=0, sticky=tk.W)

name_button = ttk.Button(frame_tools, text="Generate Name", command=generate_name)
name_button.grid(row=2, column=0, sticky=tk.W)

character_sheet_button = ttk.Button(frame_tools, text="Generate Character Sheet", command=generate_character_sheet)
character_sheet_button.grid(row=3, column=0, sticky=tk.W)

# Shared scrolled text box for the output
shared_text = scrolledtext.ScrolledText(frame_tools, wrap=tk.WORD, width=60, height=20, font=("Arial", 14))
shared_text.grid(row=1, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))


# Script Unbound tab layout

# Summary of how the game works
summary_label = ttk.Label(frame_script_unbound, text="Welcome to Script Unbound! Here, you can play an interactive text game where the possibilities are endless. Simply type what you do in the game in the input box below and click 'Send' to continue the story. Be sure to start with a game scenario or click generate for one to be generated.", wraplength=600)
summary_label.grid(row=0, column=0, columnspan=3, pady=10)

# Multiline Input box for user commands
user_input_text = tk.Text(frame_script_unbound, font=("Arial", 14), width=40, height=4)  # height set to 4 lines
user_input_text.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

# Send button
send_button = ttk.Button(frame_script_unbound, text="Send", command=send_command)
send_button.grid(row=2, column=2, pady=10)

# Output scrolled text
output_scrolled_text = scrolledtext.ScrolledText(frame_script_unbound, wrap=tk.WORD, width=60, height=20, font=("Arial", 14))
output_scrolled_text.grid(row=3, column=0, columnspan=3, pady=10)

# Generate game scenario button
generate_game_button = ttk.Button(frame_script_unbound, text="Generate", command=generate_game_scenario)
generate_game_button.grid(row=4, column=2, pady=10)

# Save and Clear buttons
# Save button for saving the game state
save_game_button = ttk.Button(frame_script_unbound, text="Save Game", command=save_game_state)
save_game_button.grid(row=4, column=0, pady=10)


# Clear button to clear the game state
clear_game_button = ttk.Button(frame_script_unbound, text="Clear", command=clear_game_state)
clear_game_button.grid(row=4, column=1, pady=10)



# Theme Toggle Button
theme_toggle_button = ttk.Button(frame_settings, text="Toggle Theme", command=toggle_theme)
theme_toggle_button.grid(row=0, column=0, pady=10)


# Sidebar for Categories
sidebar_frame = tk.Frame(frame_lore_book, bg='#DDDDDD')  # Light gray background
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

# Buttons for Categories
character_button = tk.Button(sidebar_frame, text="Characters", command=lambda: show_category("Characters"))
character_button.pack(fill=tk.X)

settings_button = tk.Button(sidebar_frame, text="Settings", command=lambda: show_category("Settings"))
settings_button.pack(fill=tk.X)

items_button = tk.Button(sidebar_frame, text="Items", command=lambda: show_category("Items"))
items_button.pack(fill=tk.X)

events_button = tk.Button(sidebar_frame, text="Events", command=lambda: show_category("Events"))
events_button.pack(fill=tk.X)

# Main Display Area
main_display = tk.Text(frame_lore_book, wrap=tk.WORD, bg='#FFFFFF')  # White background by default
main_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Button frame to hold the buttons
button_frame = tk.Frame(frame_lore_book, bg='#FFFFFF')  # White background by default
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Button to create new entry
new_entry_button = tk.Button(button_frame, text="New Entry", command=create_new_entry)
new_entry_button.grid(row=0, column=0, sticky=tk.W+tk.E)

# Button to save lore book as TXT
save_lore_button = tk.Button(button_frame, text="Save Lore Book", command=save_lore_to_txt)
save_lore_button.grid(row=1, column=0, sticky=tk.W+tk.E)

# Button to generate lore book
generate_lore_button = tk.Button(button_frame, text="Generate Lore Book", command=generate_lore_book)
generate_lore_button.grid(row=2, column=0, sticky=tk.W+tk.E)

# Button to clear the lore book
clear_lore_button = tk.Button(button_frame, text="Clear Lore Book", command=clear_lore_book)
clear_lore_button.grid(row=3, column=0, sticky=tk.W+tk.E)

root.mainloop()
