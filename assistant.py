# This version is hard coded parsing from AI agent response

import os
import openai
import importlib
import tkinter as tk
from tkinter import scrolledtext, ttk
import tiktoken
from dotenv import load_dotenv
import re
import sys

sys.setrecursionlimit(3000)  # Increase the recursion limit to 3000

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
azure_api_key = os.getenv('AZURE_API_KEY')
azure_api_base = os.getenv('AZURE_API_BASE')


def reset_openai_client():
    global openai
    openai = importlib.reload(openai)


def split_with_separator(input_string):
    # Split the string by ' '
    parts = input_string.split(' ')

    # Create a new list with both parts and separators
    result = [val for pair in zip(parts, [' '] * len(parts))
              for val in pair[:-1] + (pair[-1],)]

    return result


def calc_token_count(input_text: str) -> int:
    """Returns the number of tokens in a text string using tiktoken for GPT-4."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(input_text)
    return len(tokens)


conversation_history = []


def display_streaming_content(chat_area, chunk, window, first_chunk=True):
    """
    Display a chunk of content in chat_area with a delay, properly formatting paragraphs, bullet points, and numbered lists.
    Adjusts spacing to limit extra lines after paragraphs and numbered points.
    """
    # Split the chunk into lines to check for paragraphs, bullet points, and numbered lists
    lines = chunk.split('\n')
    formatted_lines = []
    previous_line_was_numbered = False

    for line in lines:
        # Trim the line to remove leading and trailing spaces
        line = line.strip()
        if not line:
            # Skip empty lines to avoid double spacing
            continue

        # Check if the line starts with a numbered list pattern (e.g., "1. ")
        if re.match(r'^\d+\.\s', line):
            if previous_line_was_numbered:
                # If the previous line was a numbered item, don't add an extra newline
                formatted_lines.append(line)
            else:
                # For the first numbered item, ensure it starts on a new line
                formatted_lines.append('\n' + line)
            previous_line_was_numbered = True
        else:
            # For non-numbered lines, reset the flag and add the line with a preceding newline if it's not the first
            if previous_line_was_numbered or (formatted_lines and not formatted_lines[-1].endswith('\n')):
                formatted_lines.append('\n' + line)
            else:
                formatted_lines.append(line)
            previous_line_was_numbered = False

    # Join the formatted lines back into a single string, ensuring not to start with a newline
    formatted_chunk = ''.join(formatted_lines).lstrip('\n')

    if first_chunk:
        chat_area.insert(tk.END, f"Assistant: {formatted_chunk}\n", 'assistant')
    else:
        chat_area.insert(tk.END, formatted_chunk + '\n', 'assistant')
    chat_area.see(tk.END)
    window.update_idletasks()  # Update the GUI to refresh the text area


def safe_update(window):
    if window.winfo_exists():
        window.update()

def send_message_streaming_effect(user_input, chat_area, system_prompt, token_counter, window, provider_var, model_var, temperature_var):
    SOME_THRESHOLD = 50  # Adjust this value as needed
    SOME_DELAY = 500  # Adjust this value as needed
    user_message = user_input.get("1.0", tk.END).strip()
    user_input.delete("1.0", tk.END)
    if user_message == '':
        return

    chat_area.insert(tk.END, f"\nYou: {user_message}\n", 'user')

    conversation_history.append({"role": "user", "content": user_message})

    # Update to use the selected provider and model
    use_azure = provider_var.get() == 'Azure'
    api_param_value = model_var.get()
    temperature = temperature_var.get()

    if use_azure:
        openai.api_type = "azure"
        openai.api_base = azure_api_base  # Azure-specific API base
        openai.api_version = "2023-07-01-preview"  # Azure-specific API version
        openai.api_key = azure_api_key
        api_param_name = 'engine'
    else:
        reset_openai_client()
        openai.api_key = openai_api_key
        api_param_name = 'model'

    try:
        response = openai.ChatCompletion.create(
            **{api_param_name: api_param_value},
            temperature=temperature,  # Use the temperature value from the slider
            messages=conversation_history,
            stream=True
        )

        assistant_response = []
        # Assuming this is part of the send_message_streaming_effect function
        # and focusing on the streaming logic

        # Initialize an empty buffer
        buffer = ""
        first = True
        for i in response:
            if i.get("choices") and "content" in i["choices"][0].get("delta", {}):
                content = i["choices"][0]["delta"]["content"]
                print(content)
                buffer += content  # Add content to the buffer

                # Check if the buffer ends with a full stop or newline, indicating the end of a sentence or paragraph
                if buffer.endswith('.') or buffer.endswith('\n'):
                    # Process the buffer here (e.g., display it in the chat area)
                    display_streaming_content(chat_area, buffer, window=window, first_chunk=first)
                    first = False
                    window.after(SOME_DELAY, lambda: safe_update(window))
                    window.update_idletasks()  # Update the GUI to refresh the text area
                    buffer = ""  # Reset the buffer after processing

        # If there's any remaining content in the buffer after the loop, display it
        if buffer:
            display_streaming_content(chat_area, buffer, window=window, first_chunk=first)

        conversation_history.append(
            {"role": "assistant", "content": ''.join(assistant_response)})

        total_tokens = sum(calc_token_count(
            message["content"]) for message in conversation_history)

        print(f"Conversation History at the moment: {conversation_history}")
        token_counter.set(f"Total tokens: {total_tokens}")

    except openai.error.OpenAIError as e:
        chat_area.insert(tk.END, f"\nAssistant Error: {str(e)}\n", 'error')


def insert_newline(event):
    event.widget.insert(tk.INSERT, '\n')
    return "break"


def undo(event):
    event.widget.edit_undo()


def create_gui():
    window = tk.Tk()
    window.title("OpenAI Assistant")
    window.geometry('500x700')

    main_frame = tk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    chat_area = scrolledtext.ScrolledText(main_frame, width=60, height=30)
    chat_area.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    chat_area.tag_config('user', foreground='blue')  # Default user color
    chat_area.tag_config('assistant', foreground='yellow')  # Default assistant color
    chat_area.tag_config('error', foreground='red')

    system_prompt_frame = tk.Frame(main_frame)
    system_prompt_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

    system_prompt_label = tk.Label(system_prompt_frame, text="System Prompt:")
    system_prompt_label.pack(side=tk.LEFT)

    system_prompt = tk.StringVar()
    system_prompt.set("You are a super helpful Assistant.")
    system_prompt_entry = tk.Entry(
        system_prompt_frame, textvariable=system_prompt, width=70)
    system_prompt_entry.pack(fill=tk.X, expand=True)

    conversation_history.append(
        {"role": "system", "content": system_prompt.get()})

    token_counter = tk.StringVar()
    token_counter.set("Total tokens: 0")
    token_counter_label = tk.Label(main_frame, textvariable=token_counter)
    token_counter_label.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

    user_input = tk.Text(main_frame, width=50, height=5, undo=True)
    user_input.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    user_input.bind('<Shift-Return>', insert_newline)
    user_input.bind('<Command-z>', undo)

    # Bind the Return key to the send_message_streaming_effect function
    user_input.bind('<Return>', lambda event: send_message_streaming_effect(
        user_input, chat_area, system_prompt, token_counter, window, provider_var, model_var, temperature_var))

    provider_frame = tk.Frame(main_frame)
    provider_frame.grid(row=5, column=0, sticky='ew', padx=5, pady=5)

    tk.Label(provider_frame, text="Select Provider:").pack(side=tk.LEFT)
    provider_var = tk.StringVar()
    provider_dropdown = ttk.Combobox(provider_frame, textvariable=provider_var)
    provider_dropdown['values'] = ('Azure', 'OpenAI')
    provider_dropdown.set('OpenAI')  # default value
    provider_dropdown.pack(side=tk.LEFT)
    user_input.bind('<Return>', lambda event: send_message_streaming_effect(
        user_input, chat_area, system_prompt, token_counter, window, provider_var, model_var, temperature_var))

    # Dropdown for selecting the model
    model_frame = tk.Frame(main_frame)
    model_frame.grid(row=6, column=0, sticky='ew', padx=5, pady=5)

    tk.Label(model_frame, text="Select Model:").pack(side=tk.LEFT)
    model_var = tk.StringVar()
    model_dropdown = ttk.Combobox(model_frame, textvariable=model_var)
    model_dropdown['values'] = (
        'gpt-3.5-turbo-1106',
        'gpt-4-0613',
        # 'gpt-4-32k-0613',
        'gpt-4-1106-preview'
    )  # default to OpenAI models
    model_dropdown.set('gpt-4-1106-preview')  # default value
    model_dropdown.pack(side=tk.LEFT)

    # Create a variable to hold the temperature value
    temperature_var = tk.DoubleVar()
    temperature_var.set(0.5)  # default value
    # Create a style
    style = ttk.Style(window)
    # Set the theme to "clam" which supports the fieldbackground option
    style.theme_use('clam')
    # Configure the HScale (horizontal scale) style
    style.configure('TScale', troughcolor='white',
                    background='yellow', sliderrelief='flat')

    temperature_frame = tk.Frame(main_frame)
    temperature_frame.grid(row=7, column=0, sticky='ew', padx=5, pady=5)

    # Label to display the temperature value
    temperature_label = tk.Label(
        temperature_frame, text=f"Temperature: {temperature_var.get():.2f}")
    temperature_label.pack(side=tk.LEFT)

    def update_temperature_label(value):
        temperature_label.config(text=f"Temperature: {float(value):.2f}")
    # Create the slider with the new style and command to update the label
    temperature_slider = ttk.Scale(temperature_frame, from_=0.0, to=1.0,
                                   orient=tk.HORIZONTAL, variable=temperature_var, style='TScale',
                                   command=update_temperature_label)
    temperature_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_model_dropdown(event):
        provider = provider_var.get()
        if provider == 'Azure':
            model_dropdown['values'] = (
                'gpt-35',
                'gpt-35-16k',
                'gpt-4-32k',
                'gpt-4',
                'gpt-4-1106-preview'
            )
        else:
            model_dropdown['values'] = (
                'gpt-3.5-turbo-1106',
                'gpt-4-0613',
                'gpt-4-1106-preview'
            )
        # Set to first value in the list
        model_dropdown.set(model_dropdown['values'][0])

    provider_dropdown.bind('<<ComboboxSelected>>', update_model_dropdown)
    send_button = tk.Button(main_frame, text="Send", command=lambda: send_message_streaming_effect(
        user_input, chat_area, system_prompt, token_counter, window, provider_var, model_var, temperature_var))
    send_button.grid(row=4, column=0, padx=5, pady=5)

    # Dropdown for selecting the user text color
    user_color_frame = tk.Frame(main_frame)
    user_color_frame.grid(row=8, column=0, sticky='ew', padx=5, pady=5)

    tk.Label(user_color_frame, text="User Text Color:").pack(side=tk.LEFT)
    user_color_var = tk.StringVar()
    user_color_dropdown = ttk.Combobox(user_color_frame, textvariable=user_color_var)
    user_color_dropdown['values'] = ('black', 'blue', 'green', 'red')
    user_color_dropdown.set('blue')  # Set default user color to blue
    user_color_dropdown.pack(side=tk.LEFT)

    # Dropdown for selecting the assistant (agent) text color
    agent_color_frame = tk.Frame(main_frame)
    agent_color_frame.grid(row=9, column=0, sticky='ew', padx=5, pady=5)

    tk.Label(agent_color_frame, text="Assistant Text Color:").pack(side=tk.LEFT)
    agent_color_var = tk.StringVar()
    agent_color_dropdown = ttk.Combobox(agent_color_frame, textvariable=agent_color_var)
    agent_color_dropdown['values'] = ('blue', 'magenta', 'orange', 'yellow')
    agent_color_dropdown.set('yellow')  # Set default assistant color to yellow
    agent_color_dropdown.pack(side=tk.LEFT)

    # Function to update text colors based on selection
    def update_text_colors():
        user_color = user_color_var.get()
        agent_color = agent_color_var.get()
        chat_area.tag_config('user', foreground=user_color)
        chat_area.tag_config('assistant', foreground=agent_color)

    # Call update_text_colors function when a new color is selected
    user_color_dropdown.bind('<<ComboboxSelected>>', lambda event: update_text_colors())
    agent_color_dropdown.bind('<<ComboboxSelected>>', lambda event: update_text_colors())

    # Continue with the rest of your GUI setup code...
    # This includes setting up other GUI components like input fields, buttons, etc.

    window.mainloop()


create_gui()
