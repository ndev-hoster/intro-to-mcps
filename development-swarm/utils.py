import os

def load_persona(persona:str)->str:
    with open(f"personas/{persona}.md","r") as f:
        return f.read()

