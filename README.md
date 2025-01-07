# HAL-9000: Your Intuitive Command Line GPT Assistant

HAL-9000 is a powerful command-line tool that brings the magic of GPT to your terminal. It allows you to interact with your system using natural language, simplifying complex tasks and boosting your productivity. Describe what you want to achieve, and HAL-9000 will translate your intent into precise commands.
![preview-gif](https://github.com/user-attachments/assets/457e4188-2c45-4e7d-aca1-5c4946b846dc)



## Features

*   **Natural Language Processing (NLP):**  Interact with your computer using plain English (or other languages supported by your GPT model). No more memorizing arcane syntax!
*   **Command Generation:**  HAL-9000 generates the appropriate command-line instructions based on your natural language input.
*   **Command Execution (Optional):**  You can choose to have HAL-9000 execute the generated commands directly or simply review them first.
*   **Context Awareness (Future):** HAL-9000 is being developed to retain context from previous interactions, making multi-step tasks even easier.
*   **Customization (Future):** Plans are in place to allow you to tailor HAL-9000 to your specific needs and preferences, like creating aliases for common tasks.
*   **Cross-Platform Compatibility:** Designed to work seamlessly across Linux, macOS, and Windows (with potential limitations in certain environments).

## Why HAL-9000?

*   **Increased Productivity:** Spend less time struggling with command syntax and more time getting things done.
*   **User-Friendly Interface:** Perfect for both command-line novices and experienced users who want a more intuitive way to work.
*   **Reduced Errors:** NLP-powered command generation minimizes the risk of typos and errors that can lead to unintended consequences.
*   **Faster Learning Curve:**  New to the command line? HAL-9000 helps you learn by showing you the commands that correspond to your natural language requests.

## Getting Started

### Prerequisites

*   Python 3.x (>= 3.8 recommended)
*   An OpenAI API Key (or other compatible LLM provider API Key)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd HAL-9000
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure API Key:**
    * Store your OpenAI (or other LLM provider) API Key in an environment variable (e.g., `OPENAI_API_KEY`). Or
    * Set API Key in the configuration file. (Create a configuration file based on the example provided.)

### Usage

```bash
hal9000 "find all pdf files in my Downloads folder and move them to a new folder called PDFs"
