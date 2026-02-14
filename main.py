

from api.chatgpt import ChatGPTService
    
def main():
    response = ChatGPTService.generate(prompt="Return the name of the first three starter pokemons in the first pokemon game", model="gpt-5.0")
    print(response)

if __name__ == "__main__":
    main()