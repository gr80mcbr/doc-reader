import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS 
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplates import css, bot_template, user_template

def main():
	load_dotenv()
	st.set_page_config(page_title="Chat with multiple docs", page_icon=":books:")

	st.write(css, unsafe_allow_html=True)

	st.header("Chat with multiple docs :books:")
	user_question = ""
	user_question = st.text_input("Ask a question about your documents:")
	if user_question:
		handle_user_input(user_question)

	with st.sidebar:
		st.subheader("Your documents")
		docs = st.file_uploader("Upload your docs here and click on 'Process'",
						 accept_multiple_files=True)
		if st.button("Process"):
			with st.spinner("Processing"):
				# get document text
				text = get_doc_text(docs)

				# get the text chunks
				text_chunks = get_text_chunks(text)

				# create vector store
				vectorstore = get_vectorstore(text_chunks)

				# create conversation
				st.session_state.conversation = get_conversation_chain(vectorstore)


def get_doc_text(docs):
    combined_text = ""
    for file in docs:
        file_text = file.read()
        combined_text += file_text.decode('utf-8')
    return combined_text

def get_text_chunks(text):
	text_splitter = CharacterTextSplitter(
		separator="\n",
		chunk_size=1000,
		chunk_overlap=200,
		length_function=len
	)
	chunks = text_splitter.split_text(text)
	return chunks

def get_vectorstore(text_chunks):
	embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
	vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
	return vectorstore

def get_conversation_chain(vectorstore):
	llm = ChatOpenAI()
	memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
	conversation_chain = ConversationalRetrievalChain.from_llm(
		llm=llm,
		retriever=vectorstore.as_retriever(),
		memory=memory
	)

	return conversation_chain

def handle_user_input(user_question):
	print("User Question: " + str(user_question) + "|" + str(type(user_question)))
	response = st.session_state.conversation({'question': user_question})
	st.session_state.chat_history = response['chat_history']
	for i, message in enumerate(st.session_state.chat_history):
		if i % 2 == 0:
			st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
		else:
			st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

if __name__ == '__main__':
	if "conversation" not in st.session_state:
		st.session_state.conversation = None

	if "chat_history" not in st.session_state:
		st.session_state.chat_history = None
	main()