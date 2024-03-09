# Kalauer GPT Helper
This go through the kalauer list and checks for duplicates.

## How to use
1. Create venv and install requirements
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2. Overwrite the file `.venv/lib/python3.10/site-packages/pyChatGPT/pyChatGPT.py` with the file `pyChatGPT.py` in this repository
3. Adjust the `config.txt`, see example
    - `token` the token of the ChatGPT session
    - `file` the path to the `kalauerdb.json` file
4Run main.py with command argument `-c` to the path of the `config.txt` file