from .constants import EXAMPLE_TEMPLATE, all_tools
from openai import OpenAI
from .tools import create_description,create_description_with_example
import json 
import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compute_tool_similarity(tool_embedding, query_embedding):
  # Compute cosine similarity between the tool names
  similarity_score = cosine_similarity(tool_embedding, query_embedding)
  return similarity_score.item()
from tools import create_description,create_description_with_example
from add_embedding import add_embedding
from get_embedding import search_similar
from update_embedding import update_embedding

class OpenAIWrapper:
  def __init__(self,client,text_model="gpt-3.5-turbo-1106",embedding_model="text-embedding-ada-002"):
    self.client = client
    self.text_model = text_model
    self.embedding_model = embedding_model
    self.example_template = EXAMPLE_TEMPLATE

  def generate_examples(self,function_description,number_of_examples=3):
    updated_ex_template = self.example_template.format(number_of_examples=number_of_examples)
    response = self.client.chat.completions.create(
    model=self.text_model,
    messages=[
      {"role": "system", "content": updated_ex_template},
      {"role": "user", "content": function_description}
    ]
  )
    return response.choices[0].message.content
  
  def get_embedding(self,text):
    text = text.replace("\n", " ")
    return self.client.embeddings.create(input = [text], model=self.embedding_model).data[0].embedding
  
  def add_functionDB(self,function_name,function_description):
    # implmeent logic of insertion
    embedding = self.get_embedding(function_description)
    data = {
      'name':function_name,
      'model':'openai',
      'description':function_description,
      'embedding':embedding
    }

    response = add_embedding(data)

    return response
  
  def update_functionDB(self,function_name,function_description,embedding):
    ## implement logic of updation
    embedding = self.get_embedding(function_description)
    data = {
      'name':function_name,
      'model':'openai',
      'description':function_description,
      'embedding':embedding
    }

    response = update_embedding(data)

    return response
  

  def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

  def get_related_tools(self,query):
    #implement logic of getting tools
    with open("function_embeddings/function_embeddings_openai.json", "r") as json_file:
      data = json.load(json_file)
    embedding = self.get_embedding(query)
    tools_sim = []
    for tool in data:
      sim = compute_tool_similarity(tool['embedding'],embedding)
      tools_sim.append({"tool_name": tool["name"], "similarity": sim, "tool_description": tool["description"].split('argument')[0]})
    desc_tools = sorted(tools_sim, key=lambda x: x['similarity'], reverse=True)
    return desc_tools
    #implement logic of getting tools
    embedding = self.get_embedding(query)

    data = {
      'model':'openai',
      'embedding':embedding
    }

    result = search_similar(data)
    return result


  def generate_description(self, tool):
    prompt = f"You've been provided with information about a tool: {tool}. This tool encompasses the tool name, description, supported arguments, and corresponding argument types and descriptions. Utilize these details to generate a precise and concise description that fully explains the tool's purpose. Avoid including specific use-cases; instead, focus on providing an overview of all potential functionalities and aspects that the tool can address. The goal is to create a precise and concise description that thoroughly communicates the tool's functionality. Keep the description concise, short (less than 100 words) and up to the point"
    
    response = self.client.chat.completions.create(
      model= self.text_model,
      messages=[
        {"role": "user", "content": prompt},
      ]
    )

    return response.choices[0].message.content

  

if __name__=="__main__":
  client = OpenAI(api_key = "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")
  model = OpenAIWrapper(client)
  # tool = all_tools['tools'][0]
  client = OpenAI(api_key = "your-api-key")
  model = OpenAIWrapper(client,example_template=EXAMPLE_TEMPLATE)
  tool = all_tools['tools'][0]
  # print(tool)
  function_description_openai = model.generate_description(tool)
  print(function_description_openai)
  # function_description = create_description(tool)
  # examples = model.generate_examples(function_description=function_description,number_of_examples=3)
  # function_description = create_description_with_example(function_description,examples)
  # model.add_functionDB(tool['name'],function_description) #check
  query = "what are my work list?"
  related_tools = model.get_related_tools(query)
  print(related_tools)
  # query = "what are my work list?"
  # query = "Prioritize my P0 issues and add them to the current sprint."
  # related_tools = model.get_related_tools(query)
  # print("Related tools for query are: ",related_tools)
