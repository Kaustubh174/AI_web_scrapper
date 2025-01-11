import streamlit as st
from scrape import scrape_website, extract_body_content, clean_body_content
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
import os

# Title of the app
st.title("AI Web Scraper")

# Input fields
api_key = st.text_input("Enter your OpenAI API key", type="password")
url = st.text_input("Enter a website URL:")
os.environ['OPENAI_API_KEY'] = api_key

# Initialize session state variables
if "dom_content" not in st.session_state:
    st.session_state.dom_content = ""
if "parse_description" not in st.session_state:
    st.session_state.parse_description = ""

# Scrape website button
if st.button("Scrape Site"):
    if url:
        st.write("Scraping the website...")
        result = scrape_website(url)
        body_content = extract_body_content(result)
        cleaned_content = clean_body_content(body_content)
        st.session_state.dom_content = cleaned_content
        st.write("Website scraped successfully!")

        with st.expander("View DOM content"):
            st.text_area("DOM content", cleaned_content, height=300)
    else:
        st.error("Please enter a valid URL.")

# Input for parsing description
if st.session_state.dom_content:
    parse_description = st.text_area("Describe what you want to parse?")
    st.session_state.parse_description = parse_description

# LLM setup
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)
prompt = ChatPromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)

# Parse content button
if st.button("Parse Content"):
    if st.session_state.parse_description and st.session_state.dom_content:
        output = chain.invoke({
            "dom_content": st.session_state.dom_content,
            "parse_description": st.session_state.parse_description
        })
        st.write(output)
    else:
        st.error("Please provide a parsing description and scrape a website first.")
