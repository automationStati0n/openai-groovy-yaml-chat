import os
import sys
import json
import requests
import yaml
from typing import Dict, List, Tuple

class OpenAIChat:
    def __init__(self, token: str):
        self.user_input_file = 'input.txt'
        self.conv_yaml_file = 'input.yaml'
        self.output_file = 'output.md'
        self.token = token
        self.url = 'https://api.openai.com/v1/chat/completions'
        self.model_list = ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        self.system_role_init_content = ''
        self.conversation = []
        self.last_conversation = None

    def start_listener(self):
        while True:
            console_input = input("Press Enter to submit the input file...")
            if "clear" in console_input:
                self.write_to_yaml("conversation: []")
                self.conversation = []
            elif "reset" in console_input:
                self.write_to_yaml("conversation: []")
                self.conversation = []
                self.write_output("")
            else:
                array_index_selected = int(''.join(filter(str.isdigit, console_input))) if any(char.isdigit() for char in console_input) else 1
                if "4e" in console_input:
                    self.system_role_init_content = 'You are a helpful assistant'
                model_choice = 1 if array_index_selected != 4 else 0
                max_token_choice = 3200 if array_index_selected != 4 else 7200

                if "3l" in console_input:
                    self.system_role_init_content = 'You are a helpful assistant'
                    model_choice = 2
                    max_token_choice = 1500

                if not os.path.exists(self.conv_yaml_file):
                    with open(self.conv_yaml_file, 'w') as f:
                        f.write("conversation: []")

                with open(self.conv_yaml_file, 'r') as f:
                    yaml_content = yaml.safe_load(f)
                    self.conversation = yaml_content.get("conversation")

                self.update_conversation_yaml('user', self.read_input_file())

                self.set_json_payload(model_choice, max_token_choice)

                if self.conversation == self.last_conversation:
                    print("The input file has not changed since the last submission. Skipping...")
                else:
                    self.process_conversation()

    def process_conversation(self):
        json_string = json.dumps(self.json_payload)
        ai_response, server_response = self.send_request('POST', self.url, json_string, False, True)

        if ai_response is None:
            print(f"Error occurred while sending the request: {server_response}")
            print(f"AI response:\n {server_response}")
            return

        if os.path.exists(self.output_file):
            with open(self.output_file, 'a') as f:
                if f.tell() > 0:
                    f.write('\n---\n')
        else:
            self.write_output('# Conversation\n')

        self.write_output(ai_response, mode='a')

        updated_yaml = self.update_conversation_yaml('assistant', ai_response)
        self.write_to_yaml("conversation:\n" + updated_yaml)

        self.last_conversation = self.conversation

    def update_conversation_yaml(self, role: str, text: str) -> str:
        new_entry = {role: text}
        if not self.conversation:
            self.write_to_yaml("conversation: []")
            self.conversation = []

        self.conversation.append(new_entry)

        return yaml.dump(self.conversation, default_flow_style=False, indent=2)

    def set_json_payload(self, model_choice: int, max_token_choice: int):
        self.json_payload = {
            "model": self.model_list[model_choice],
            "messages": [],
            "max_tokens": max_token_choice,
            "temperature": 0.6
        }
        self.json_payload["messages"].append({"role": "system", "content": self.system_role_init_content})

        for entry in self.conversation:
            for input_key, input_content in entry.items():
                self.json_payload["messages"].append({"role": input_key, "content": input_content})

    def send_request(self, method: str, url: str, payload: str, is_json: bool, use_auth: bool) -> Tuple[str, str]:
        headers = {
            "Content-Type": "application/json" if is_json else "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {self.token}" if use_auth else ""
        }
        response = requests.request(method, url, headers=headers, data=payload)

        if response.status_code != 200:
            return None, response.text

        response_json = response.json()
        ai_response = response_json['choices'][0]['message']['content']

        return ai_response, response.text

    def read_input_file(self) -> str:
        with open(self.user_input_file, 'r') as f:
            return f.read()

    def write_output(self, content: str, mode: str = 'w'):
        with open(self.output_file, mode) as f:
            f.write(content)

    def write_to_yaml(self, content: str):
        with open(self.conv_yaml_file, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    token = sys.argv[1]
    chat = OpenAIChat(token)
    chat.start_listener()