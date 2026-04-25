A powerful conversational AI agent with file manipulation capabilities, built on top of Ollama's API. This agent can read, list, and edit files through natural language conversations, making it an ideal tool for automated code assistance and file management tasks.

## Features

- **Conversational Interface**: Interact with the AI using natural language
- **File Operations**: 
  - Read file contents
  - List files and directories
  - Edit existing files or create new ones
- **Tool-Based Architecture**: Extensible tool system using Pydantic schemas
- **Ollama Integration**: Connects to Ollama's cloud API (qwen3.5:cloud model)
- **Error Handling**: Robust error handling for file operations and API calls
- **Session Memory**: Maintains conversation context across multiple interactions

## Requirements

- Python 3.8+
- Ollama API access

## Installation

1. **Clone or download the repository**

2. **Install dependencies**:
   ```bash
   pip install openai pydantic python-dotenv
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```bash
   Ollama_API_KEY=your_api_key_here
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `Ollama_API_KEY` | Your Ollama API key for authentication | Yes |

### API Configuration

The agent connects to Ollama's API at:
- **Base URL**: `https://ollama.com/v1`
- **Model**: `qwen3.5:cloud`
- **Max Tokens**: `2048`

## Usage

### Command Line Interface

Run the agent:
```bash
python agent.py
```

### Interactive Session

```
AI Code Assistant
=================
Type 'exit' or 'quit' to end the conversation.

You: Show me the files in the current directory
Assistant: Contents of .:
[DIR]  src/
[FILE] agent.py
[FILE] README.md

You: Read the contents of agent.py
Assistant: File contents of agent.py:
import os, sys, json
...

You: Create a new file called test.txt with "Hello World"
Assistant: Successfully created test.txt
```

### Programmatic Usage

```python
from agent import Agent

# Initialize the agent
agent = Agent(api_key="your_api_key")

# Send a request
response = agent.ask("List all files in the current directory")
print(response)
```

## Available Tools

### 1. `read_file`
Read the contents of a file at a specified path.

**Parameters:**
- `path` (string, required): The path to the file to read

### 2. `list_files`
List all files and directories in the specified path.

**Parameters:**
- `path` (string, optional): The path to list (defaults to current directory)

### 3. `edit_file`
Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.

**Parameters:**
- `path` (string, required): The path to the file to edit
- `old_text` (string, optional): The text to search for and replace
- `new_text` (string, required): The text to replace old_text with

## Architecture

```
agent.py
├── Tool (BaseModel)          # Tool schema definition
├── Agent (Class)
│   ├── __init__()            # Initialize client and tools
│   ├── _setup_tools()        # Configure available tools
│   ├── _execute_tool()       # Execute tool based on name
│   ├── _read_file()          # Read file contents
│   ├── _list_files()         # List directory contents
│   ├── _edit_file()          # Edit or create files
│   └── ask()                 # Main conversation handler
└── main()                    # CLI entry point
```

## Error Handling

The agent handles various error scenarios:
- File not found errors
- Permission errors
- API connection errors
- Invalid tool arguments
- Keyboard interrupts (Ctrl+C)

## Security Considerations

⚠️ **Important**: This agent has file system access. Use with caution:
- Only run in trusted directories
- Review file changes before executing in production
- Keep your API key secure and never commit it to version control

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Built with**  **Ollama** | **OpenAI SDK** | **Pydantic**
