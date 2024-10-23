import os
from dotenv import load_dotenv

load_dotenv()

# List of file extensions to include in the prompt
included_extensions = ['.py', '.kv', '.env']

# Directories to exclude (like cache, venv, etc.)
excluded_dirs = ['__pycache__', '.venv', 'venv']

def create_prompt(directory):
    prompt = "PROMPT\n--\n"

    # Walk through the directory and list files
    for root, dirs, files in os.walk(directory):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        # Process files
        for file in files:
            # Check file extension
            if any(file.endswith(ext) for ext in included_extensions):
                filepath = os.path.join(root, file)
                prompt += f"File {file}\n\nContent\n--\n"

                # Read the file content
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        prompt += f"{content}\n--\n"
                except Exception as e:
                    prompt += f"Error reading file {file}: {e}\n--\n"

    return prompt


# Directory where your project is located
project_directory = os.getenv('PROJECT_PATH')

# Generate the prompt
prompt_output = create_prompt(project_directory)

# Write the prompt to a text file
output_file = os.path.join(project_directory, 'project_prompt.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(prompt_output)

print(f"Prompt written to {output_file}")
