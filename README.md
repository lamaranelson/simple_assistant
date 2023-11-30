# Simple Assistant

This LLM based Chat Assistant allows users to interact with an AI model through a Tkinter GUI. It supports both OpenAI and Azure LLM models, enabling users to choose their preferred provider and model for generating responses.

## Features

- Tkinter GUI
- Support for multiple models directly from OpenAI or from an Azure instance.
- Real-time streaming of LLM responses.
- Token count tracking for monitoring usage.
- Customizable system prompt.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.6 or higher
- `pip` for installing Python packages

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/lamaranelson/simple_assistant.git
   ```
2. Navigate to the project directory:
   ```
   cd simple_assistant
   ```
3. Set up a virtual environment:
   ```
   python3 -m venv venv
   ```
   Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory of the project with the following content:

```
OPENAI_API_KEY= "your-openai-api-key"
AZURE_API_KEY= "your-azure-api-key"
AZURE_API_BASE= "your-azure-api-endpoint"
```

Replace the placeholder values with your actual API keys and endpoint.

## Usage

Run the `assistant.py` script to launch the AI Chat Assistant:

```
python assistant.py
```

Once the application is running:
- Select the AI provider (Azure or OpenAI) from the dropdown menu.
- Choose the desired AI model from the second dropdown menu.
- Type your message in the input box and press Enter or click the "Send" button to get a response from the AI.


<img width="499" alt="ex1" src="https://github.com/lamaranelson/simple_assistant/assets/65568691/73534986-f585-4bc4-af95-9f40bdfc94fa">


<img width="497" alt="ex2" src="https://github.com/lamaranelson/simple_assistant/assets/65568691/cbec434f-27b0-4168-9741-54f73d724c63">


