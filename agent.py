import os ,sys ,json
from dotenv import load_dotenv
from typing import List, Dict, Any
from pydantic import BaseModel
from openai import OpenAI
import argparse

class Tool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str,Any]


class Agent():
    def __init__(self, api_key:str):
        self.client = OpenAI(base_url="https://ollama.com/v1" , api_key=api_key)
        self.messages : List[Dict[str,Any]] = []
        self.tools : List[Tool] = []
        self._setup_tools()

    def _setup_tools(self):
        self.tools = [
            Tool(
                name="read_file",
                description="Read the contents of a file at a specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="list_files",
                description="List all files and directories in the specified path",
                input_schema={
                    "type":"object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="edit_file",
                description="Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The text to search for and replace (leave empty to create new file)",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The text to replace old_text with",
                        },
                    },
                    "required": ["path", "new_text"],
                },
            ),
        ]

    def _execute_tool(self, tool_name:str, tool_args_str: str):
        try:
            tool_input = json.loads(tool_args_str)
            if tool_name == "read_file":
                return self._read_file(tool_input["path"])
            elif tool_name == "list_files":
                return self._list_files(tool_input.get("path","."))
            elif tool_name == "edit_file":
                return self._edit_file(
                        path=tool_input["path"],
                        old_text=tool_input.get("old_text","."),
                        new_text=tool_input["new_text"]
                    )
            else:
                return f"Unknown tool name: {tool_name}"   
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _read_file(self,path:str) -> str:
        try:
            with open(path, "r" , encoding="utf-8") as f:
                content = f.read()
            return f"File contents of {path}:\n{content}"    
        except FileNotFoundError:
            return f"File not found: {path}"
        except Exception as e:
            return f"Error reading file : {str(e)}"
        
    def _list_files(self, path:str) ->str:
        try:
            if not os.path.exists(path):
                return f"Path not found: {path}"
            
            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR]  {item}/")
                else:
                    items.append(f"[FILE] {item}")

            if not items:
                return f"Empty directory: {path}"

            return f"Contents of {path}:\n" + "\n".join(items)

        except Exception as e:
            return f"Error listing files: {str(e)}"  

    def _edit_file(self, path:str, old_text:str, new_text:str)->str: 
        try:
            if os.path.exists(path) and old_text:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if old_text not in content:
                    return f"Text not found in file: {old_text}"

                content = content.replace(old_text, new_text)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

                return f"Successfully edited {path}"
            else:
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_text)

                return f"Successfully created {path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def ask(self, user_input:str)->str:
        self.messages.append({"role":"user", "content": user_input})

        tool_schema = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description, 
                "parameters": tool.input_schema  
            }
        } for tool in self.tools]

        while True:
            try:    
                response = self.client.chat.completions.create(
                    model= "qwen3.5:cloud",
                    max_tokens= 2048,
                    messages=self.messages,
                    tools=tool_schema

                )

                assistant_message = response.choices[0].message
                self.messages.append(assistant_message)

                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        result = self._execute_tool(tool_call.function.name, tool_call.function.arguments)
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": str(result)
                        })
                    continue 
                    
                else:
                    return assistant_message.content if assistant_message.content else ""
                
            except Exception as e:
                    return f"Error: {str(e)}"        
          


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Assistant - A conversational AI agent with file editing capabilities"
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("Ollama_API_KEY")
    if not api_key:
        print("Error: Ollama_API_KEY not set")
        sys.exit(1)
    agent = Agent(api_key)


    print("AI Code Assistant")
    print("=================")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = agent.ask(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()