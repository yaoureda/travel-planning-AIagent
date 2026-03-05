# 1. Import required modules
import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI

# 2. Load environment variables and create model with temperature 0
load_dotenv()
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
    temperature=0
)

# 3. Define your teaching examples list with input/output pairs
#    - Each example should show a product description as input
#    - And the corresponding JSON format as output (use json.dumps for formatting)
examples = [
    {
        "input": "Premium wireless headphones with noise cancellation, $199",
        "output": json.dumps({
            "name": "Premium wireless headphones",
            "price": "$199",
            "category": "electronics",
            "highlight": "noise cancellation"
        })
    },
    {
        "input": "Organic cotton t-shirt in blue, comfortable fit, $29.99",
        "output": json.dumps({
            "name": "Organic cotton t-shirt",
            "price": "$29.99",
            "category": "clothing",
            "highlight": "comfortable fit"
        })
    },
    {
        "input": "Gaming laptop with RTX 4070, 32GB RAM, $1,499",
        "output": json.dumps({
            "name": "Gaming laptop",
            "price": "$1,499",
            "category": "computers",
            "highlight": "RTX 4070, 32GB RAM"
        })
    }
]

# 4. Create an example template using ChatPromptTemplate.from_messages
#    with ("human", "{input}") and ("ai", "{output}")
example_template = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}")
    ]
)

# 5. Create a FewShotChatMessagePromptTemplate with your examples
few_shot_template = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_template,
)

# 6. Build a final prompt that includes the few-shot template
final_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that converts product descriptions into structured JSON format."),
        few_shot_template,
        ("human", "{input}")
    ]
)

# 7. Test with new product descriptions and parse the JSON output with json.loads()
chain = final_template | model
test_descriptions = [
    "Smartwatch with heart rate monitor, GPS, $199.99",
    "Bluetooth speaker with 12 hours playtime, $49.95"
]

for description in test_descriptions:
    result = chain.invoke({"input": description})
    print(f"Input: {description}")
    print("Output:", json.loads(result.content))

