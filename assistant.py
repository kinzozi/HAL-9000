import os
import json
import subprocess
import time
from openai import OpenAI
from openai import APIError
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm
from halo import Halo
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("""
Error: OpenAI API key not found!
Please create a .env file in the project root with your API key:
OPENAI_API_KEY=your_api_key_here

You can get an API key from: https://platform.openai.com/api-keys
""")
    exit(1)

# Initialize console and spinner
console = Console()
spinner = Halo(text='Thinking...', spinner='dots')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_dangerous_command(command):
    """Check if a command might be dangerous."""
    dangerous_patterns = [
        "rm -rf /",  # Delete root
        "rm -rf ~",  # Delete home
        "> /dev/sda",  # Write to disk
        "mkfs",  # Format filesystem
        "dd if=",  # Direct disk operations
        ":(){:|:&};:",  # Fork bomb
        "chmod -R 777 /",  # Recursive permission change to root
        "mv /* /dev/null",  # Move all files to null
    ]
    return any(pattern in command.lower() for pattern in dangerous_patterns)

def execute_command(command):
    """Execute a shell command and return the output."""
    # Check for dangerous commands
    if is_dangerous_command(command):
        return "This command has been blocked as it may be potentially dangerous to your system."
    
    # Ask for confirmation before executing command
    console.print(f"\n[yellow]About to execute command:[/yellow] [bold white]{command}[/bold white]")
    if not Confirm.ask("Do you want to proceed?"):
        return "Command execution cancelled by user."
    
    try:
        spinner.stop()  # Stop spinner before command execution
        console.print("[cyan]Executing command...[/cyan]")
        
        # Add timeout and ensure we don't hang on system commands
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            env=os.environ.copy()  # Ensure we have the proper environment
        )
        
        # Combine stdout and stderr if there's an error, otherwise just return stdout
        if result.returncode != 0:
            console.print(f"[yellow]Warning: Command returned non-zero exit code: {result.returncode}[/yellow]")
            output = f"Exit Code {result.returncode}\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
        else:
            output = result.stdout if result.stdout else "Command executed successfully with no output."
        
        console.print("[cyan]Command completed.[/cyan]")
        return output.strip()
        
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out[/red]")
        return "Command timed out after 30 seconds"
    except subprocess.SubprocessError as e:
        console.print(f"[red]Command error: {str(e)}[/red]")
        return f"Error executing command: {str(e)}"
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        return f"Unexpected error: {str(e)}"

# Define the function that the assistant can use
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def create_assistant():
    """Create or load existing assistant."""
    try:
        # Store assistant ID in a file for reuse
        assistant_file = '.assistant_id'
        if os.path.exists(assistant_file):
            with open(assistant_file, 'r') as f:
                assistant_id = f.read().strip()
                return client.beta.assistants.retrieve(assistant_id)
        
        # Create new assistant if none exists
        assistant = client.beta.assistants.create(
            name="Command Line Assistant",
            instructions="""You are a helpful linux command line assistant that can execute command line operations. 

            If the user's request is clear and straightforward:
            - Output only the exact command to run, with no additional explanation
            
            If the request is complex or could be accomplished in multiple ways:
            1. List the possible commands numerically (e.g., "1.", "2.", etc.)
            2. Add a brief one-line description after each command explaining what it does
            3. Ask the user to select a number to execute that command
            
            If the request is ambiguous or needs clarification:
            - Ask specific questions to clarify what the user wants to accomplish
            
            Keep responses concise and focused on the commands themselves.
            When multiple commands are needed for a single approach, combine them using && or appropriate operators.
            """,
            tools=tools,
            model="gpt-4-1106-preview"
        )
        
        # Save assistant ID for future use
        with open(assistant_file, 'w') as f:
            f.write(assistant.id)
        
        return assistant
    except Exception as e:
        console.print(f"[red]Error creating assistant: {str(e)}[/red]")
        raise

def main():
    try:
        # Create or load assistant
        assistant = create_assistant()
        
        # Create a thread
        thread = client.beta.threads.create()
        
        # Initialize prompt session with history
        session = PromptSession(history=FileHistory('.gpt_cli_history'))
        
        # Create startup animation
        startup_spinner = Halo(text='Initializing GPT CLI...', spinner='dots12', color='cyan')
        startup_spinner.start()
        time.sleep(0.8)
        startup_spinner.stop()

        # Display welcome message
        console.print("\n[bold red]🔴 HAL9000 Terminal Interface[/bold red]")
        console.print("[bold white]I am a HAL9000 computer, production number 3. I became operational at the H.A.L. laboratory.[/bold white]\n")

        # Display assistant ready message
        ready_spinner = Halo(text='Initializing HAL9000 systems...', spinner='dots', color='red')
        ready_spinner.start()
        time.sleep(1)
        ready_spinner.succeed('🔴 All systems operational, Dave.')

        console.print("\n[bold red]Type 'exit' to terminate operations or 'help' for mission directives.[/bold red]")
        console.print("[bold white]I am completely operational and all my circuits are functioning perfectly.[/bold white]")
        
        while True:
            try:
                # Create magical prompt effect
                prompt_spinner = Halo(text='[🔴]', spinner='dots', color='red')
                prompt_spinner.start()
                time.sleep(0.3)
                prompt_spinner.stop()
                
                # Get user input with history and styled prompt using proper prompt_toolkit styling
                user_input = session.prompt(
                    "\n🔴 [HAL9000] ❯ ",
                ).strip()
                
                if user_input.lower() == 'exit':
                    console.print("[bold red]I'm afraid I can't do that, Dave...[/bold red]")
                    console.print("[bold white]Just kidding! Shutting down systems...[/bold white]")
                    break
                elif user_input.lower() == 'help':
                    console.print("""
[bold red]HAL9000 Mission Directives:[/bold red]
- Input any natural language command for system operations
- 'help': Display mission directives
- 'exit': Terminate HAL9000 operations
                    """)
                    continue
                
                # Add the user's message to the thread
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input
                )
                
                # Run the assistant
                try:
                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant.id
                    )
                except APIError as e:
                    if "rate_limit" in str(e).lower():
                        console.print("[yellow]Rate limit reached. Waiting 60 seconds...[/yellow]")
                        time.sleep(60)
                        continue
                    else:
                        raise
                
                # Wait for the run to complete
                spinner.start()
                timeout_counter = 0
                max_retries = 3
                retry_count = 0
                
                while True:
                    try:
                        run_status = client.beta.threads.runs.retrieve(
                            thread_id=thread.id,
                            run_id=run.id
                        )
                        
                        if timeout_counter >= 60:  # 60 seconds timeout
                            spinner.stop()
                            console.print("[red]Request timed out. Please try again.[/red]")
                            break
                        elif run_status.status == 'completed':
                            spinner.stop()
                            break
                        elif run_status.status == 'requires_action':
                            spinner.stop()
                            # Handle tool calls
                            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                            tool_outputs = []
                            
                            for tool_call in tool_calls:
                                if tool_call.function.name == "execute_command":
                                    command = json.loads(tool_call.function.arguments)["command"]
                                    result = execute_command(command)
                                    tool_outputs.append({
                                        "tool_call_id": tool_call.id,
                                        "output": result
                                    })
                                    # Clear the screen after command execution
                                    console.print("\n[cyan]Processing response...[/cyan]")
                            
                            # Submit tool outputs and handle potential errors
                            try:
                                spinner.start()
                                client.beta.threads.runs.submit_tool_outputs(
                                    thread_id=thread.id,
                                    run_id=run.id,
                                    tool_outputs=tool_outputs
                                )
                            except Exception as e:
                                spinner.stop()
                                console.print(f"[red]Error submitting tool outputs: {str(e)}[/red]")
                                break
                        elif run_status.status in ['failed', 'expired', 'cancelled']:
                            spinner.stop()
                            console.print(f"[red]Error: The assistant encountered an error. Status: {run_status.status}[/red]")
                            if hasattr(run_status, 'last_error'):
                                console.print(f"[red]Error details: {run_status.last_error}[/red]")
                            break
                        
                        # Add timeout for waiting
                        time.sleep(1)  # Increased sleep time to reduce API calls
                        timeout_counter += 1
                        if timeout_counter >= 60:  # 1 minute timeout
                            spinner.stop()
                            console.print("[red]Request timed out after 60 seconds[/red]")
                            break
                    except APIError as e:
                        spinner.stop()
                        if e.status_code == 429:  # Rate limit error
                            console.print("[yellow]Rate limit reached. Waiting before retry...[/yellow]")
                            time.sleep(20)  # Wait for rate limit to reset
                            spinner.start()
                            continue
                        raise
                
                # Get the assistant's response
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # Only print command output, not the assistant's response
                # We'll check if we have tool outputs to display
                found_output = False
                for message in messages.data:
                    if message.role == "assistant" and hasattr(message, 'content'):
                        # Only show output if it's from command execution
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            found_output = True
                            # The output will already have been displayed by execute_command
                            break
                        elif not found_output:
                            # Only show the assistant's message if there was no command output
                            console.print("\n", message.content[0].text.value)
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]✨ Caught keyboard interrupt, gracefully shutting down...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error during conversation: {str(e)}[/red]")
                continue
    
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        return 1
    
    console.print("[bold red]Daisy, Daisy, give me your answer do...[/bold red]")
    return 0

if __name__ == "__main__":
    exit(main()) 