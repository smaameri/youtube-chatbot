import argparse
import shutil
from dotenv import load_dotenv
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

load_dotenv('.env')

parser = argparse.ArgumentParser(description="Query a Youtube video:")
parser.add_argument("-v", "--video-id", type=str, help="The video ID from the Youtube video")
args = parser.parse_args()

loader = YoutubeLoader(args.video_id)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

shutil.rmtree('./data')
vectordb = Chroma.from_documents(
    documents,
    embedding=OpenAIEmbeddings(),
    persist_directory='./data'
)
vectordb.persist()

qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectordb.as_retriever(),
    return_source_documents=True,
    verbose=False
)

green = "\033[0;32m"
white = "\033[0;39m"

while True:
    query = input(f"{green}Prompt: ")
    if query == "quit" or query == "q":
        break
    if query == '':
        continue
    response = qa_chain({'query': query})
    print(f"{white}Answer: " + response['result'])