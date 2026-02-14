from api.chatgpt import ChatGPTService

def main():
    response = ChatGPTService.generate(prompt="Return the name of the first three starter pokemons")
    print(response)

if __name__ == "__main__":
    main()