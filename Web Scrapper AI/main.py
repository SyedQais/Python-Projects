import streamlit as st
from scrape import (scrape_website,
                    split_dom_content,
                    clean_body_content,
                    extract_body_content,
                     )

from gemini_parse import gemini

st.title("AI Web Scarapper")
url = st.text_input("Enter website url here")

if st.button("scrape site"):
    st.write("Scrapping the website")
    result = scrape_website(url)
    body_content = extract_body_content(result)
    cleaned_content = clean_body_content(body_content)

    # Store both the cleaned content for display and the original body_content for parsing
    st.session_state.dom_content = cleaned_content
    st.session_state.raw_body_content = body_content

    with st.expander("View DOM Content"):
        st.text_area("DOM Content", cleaned_content, height=300)

if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse?")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")
          
            # Retrieve the body_content from session state instead of local scope
            # you canuse both raw contemt and cleaned ccontent based on your preference, i have added code for both, to use raw content uncomment the code below and comment out the other code.
            # content_to_parse = st.session_state.raw_body_content
            content_to_parse = st.session_state.dom_content
            
            # Pass the retrieved content to your gemini function
            result = gemini(content_to_parse, parse_description)
            st.write(result)

