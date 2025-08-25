from src.PAI.PAI import PAI

def show_call_response():
    pai = PAI("test")
    response = pai.call_resources([{
        "Name": "Sam's Cake Preferences",
        "ID": "379c6bbe-1380-46d9-862f-973ae5052e51",
        "Description": "A string containing Sam's preferences for cake flavors and types",
        "ContentType": "string"
    }])
    return response

if __name__ == "__main__":
    print(show_call_response())
