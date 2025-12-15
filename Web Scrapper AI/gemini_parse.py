from google import genai
from google.genai import types


instruction = (
    "You are tasked with extracting specific information from a text which wil be mentioned."
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)


def gemini(dom_content, parse_description):
    # pass your api-key explicitly: client = genai.Client(api_key="YOUR_API_KEY")
    client = genai.Client(api_key="")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(f"You are tasked with extracting specific information from the following text content: {dom_content},\n Only extract the information that directly matches the following description:{parse_description}"),
        config=types.GenerateContentConfig(
            system_instruction=instruction)

    )

    return(response.text)

