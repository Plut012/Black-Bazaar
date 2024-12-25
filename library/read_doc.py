import os
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Step 1: Set the folder path for Obsidian documents
obsidian_path = "~/TimeCapsule"
print("enter path to file within vault:")
FOLDER_PATH = input()  

# Step 2: Read all Markdown files from the folder
def read_obsidian_documents(folder_path):
    documents = []

    for filename in os.listdir(folder_path):

        if filename.endswith(".md"):  # Only process Markdown files
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                documents.append(file.read())
    return documents

# Step 3: Initialize the local Ollama model
llm = Ollama(model="llama3.1")

# Step 4: Define a LangChain pipeline
prompt = PromptTemplate(
    input_variables=["content"],
    template="Summarize the following content:\n\n{content}\n\nSummary:",
)

chain = LLMChain(llm=llm, prompt=prompt)

# Step 5: Process each document and get summaries
def process_documents(documents):
    summaries = []
    for doc in documents:
        try:
            summary = chain.run(content=doc)
            summaries.append(summary)
        except Exception as e:
            print(f"Error processing document: {e}")
    return summaries

# Step 6: Run the pipeline
if __name__ == "__main__":
    print("Reading Obsidian documents...")
    documents = read_obsidian_documents(FOLDER_PATH)
    
    print(f"Processing {len(documents)} documents...")
    summaries = process_documents(documents)
    
    # Print summaries
    for idx, summary in enumerate(summaries, 1):
        print(f"Summary {idx}:\n{summary}\n")

