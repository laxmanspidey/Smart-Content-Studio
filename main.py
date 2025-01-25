import streamlit as st
import sqlite3
import bcrypt
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Initialize DB connection
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_db()

# Sign up function
def signup_user(username, email, password):
    if not email.endswith("@gmail.com"):
        return "Invalid email address. Only Gmail addresses are allowed."

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Login function
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    record = c.fetchone()
    conn.close()
    if record:
        if bcrypt.checkpw(password.encode('utf-8'), record[0]):
            return True
    return False

# Streamlit app layout
st.set_page_config(page_title="✨ Smart Content Studio ✨", layout="wide")

# Custom CSS for styling


# Header
st.markdown("""
    <div class="header">
        <h1>✨ Smart Content Studio ✨</h1>
        <h6>Effortlessly generate essays, emails, posts, and more with AI!</h6>
    </div>
    """, unsafe_allow_html=True)

# Handle Login/Signup/Logout
if 'username' not in st.session_state:
    st.session_state['username'] = None

# Logout functionality
def logout():
    st.session_state['username'] = None
    st.rerun()

# Top-right logout button
if st.session_state['username']:
    st.sidebar.markdown(f"### Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        logout()

# Authentication form
def auth_form():
    # Create two columns
    col1, col2 = st.columns(2)

    # Display the first image in the first column
    with col1:
        st.image(
            "https://media.gettyimages.com/id/1436216218/video/social-media-chart-inside.jpg?s=640x640&k=20&c=3ym3s242m6JdsSPaKDt0UZuKGlVmp_CVQrYm1B434Pw=",
            use_column_width=True,  # Ensures the image takes up the full column width
            caption="Image 1",  # Optional caption
        )
    
    # Display the second image in the second column
    with col2:
        st.image(
            "data:image/jpeg;base64,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",
            use_column_width=True,  # Ensures the image takes up the full column width
            caption="Image 2",  # Optional caption
        )

    auth_option = st.selectbox('Select Authentication Method', ['Login', 'Signup'])
    
    if auth_option == 'Signup':
        username = st.text_input('Enter Username')
        email = st.text_input('Enter Email (must end with @gmail.com)')
        password = st.text_input('Enter Password', type='password')
        confirm_password = st.text_input('Confirm Password', type='password')
        
        if st.button('Sign Up'):
            if password != confirm_password:
                st.error('Passwords do not match.')
            else:
                result = signup_user(username, email, password)
                if result == True:
                    st.success('Signup successful! You can now log in.')
                else:
                    st.error(result if isinstance(result, str) else 'Username or email already exists.')

    if auth_option == 'Login':
        username = st.text_input('Enter Username')
        password = st.text_input('Enter Password', type='password')

        if st.button('Log In'):
            if login_user(username, password):
                st.session_state['username'] = username
                st.success(f'Welcome back, {username}!')
            else:
                st.error('Invalid credentials. Please try again.')

# Main app
if st.session_state['username'] is None:
    auth_form()
else:
    # Content generation section
    mailtype = ""
    Reply = ""
    optionpg1 = ""

    with st.sidebar:
        api_key = os.getenv("apikey")
        
        option = st.selectbox(
            'Select type of app you want?',
            ('Email Generation', 'Post Generation', 'Essay Generation', 'Text Generation', 'Image Captioning and Tagging'))

        if option == "Post Generation":
            optionpg1 = st.selectbox('Choose Social Media', ('Linkedin', 'Twitter/X'))

            if optionpg1 == "Linkedin":
                style = st.selectbox('Choose Post Style', ('Professional', 'Friendly', 'Creative', 'Inspirational', 'Storytelling'))
                domain = st.text_input('Your Working Domain/Field')
                optionlp = st.selectbox('Select length of post you want?', ('small - approx 150 words', 'medium - approx 350 words', 'long - approx 500 words'))

            if optionpg1 == "Twitter/X":
                style1 = st.selectbox('Choose Post Style', ('Professional', 'Friendly', 'Creative', 'Inspirational', 'Storytelling'))
                optiontp = st.selectbox('Select length of post you want?', ('small - approx 50 words', 'medium - approx 150 words', 'long - approx 250 words'))

        if option == "Essay Generation":
            optioneg1 = st.selectbox('Select length of essay you want?', ('small - approx 150 words', 'medium - approx 350 words', 'long - approx 500 words', 'extensive - more than 800 words'))

        if option == "Essay Generation":
            optioneg2 = st.selectbox('Select type of essay you want?', ('simple', 'descriptive', 'narrative', 'Persuasive', 'professional'))

        if option == "Email Generation":
            mailtype = st.radio("Select Email Type 👇", ["Compose", "Reply"], horizontal=True)

            if mailtype == "Compose":
                sender = st.text_input("Name of sender with details", value=st.session_state['username'], disabled=False)
                receiver = st.text_input("Name of receiver with details")
                optionec1 = st.selectbox('Select length of email you want?', ('small - approx 150 words', 'medium - approx 350 words', 'long - approx 500 words', 'extensive - more than 800 words'), index=1)
                emailtone = st.selectbox('Select tone of email you want?', ('Friendly', 'Funny', 'Casual', 'Excited', 'Professional', 'Sarcastic', 'Persuasive'), index=0)
                emaillang = st.selectbox('Select language of email?', ("Arabic", "Bengali", "Bulgarian", "Chinese simplified", "English", "French", "German", "Hindi", "Spanish"), index=4)

            if mailtype == "Reply":
                sender1 = st.text_input("Name of sender with details")
                receiver1 = st.text_input("Name of receiver with details")
                optionec2 = st.selectbox('Select length of email you want?', ('small - approx 150 words', 'medium - approx 350 words', 'long - approx 500 words', 'extensive - more than 800 words'), index=1)
                emailtone1 = st.selectbox('Select tone of email you want?', ('Friendly', 'Funny', 'Casual', 'Excited', 'Professional', 'Sarcastic', 'Persuasive'), index=0)
                emaillang1 = st.selectbox('Select language of email?', ("Arabic", "Bengali", "Bulgarian", "Chinese simplified", "English", "French", "German", "Hindi", "Spanish"), index=4)

    st.markdown(f"<h1 style='font-size: 24px;'>{option}</h1>", unsafe_allow_html=True)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')    

    def generate(prompt):
        response = model.generate_content(prompt)
        return response

    if option == "Essay Generation":
        with st.form("myform"):
            ip = st.text_input("Write topic of essay")
            additional = st.text_input("Write some extra about topic (optional)")

            submitted = st.form_submit_button("Submit")

            prompt = f"""Write an essay that is on topic - {ip} with a {optioneg1} tone. Here are some additional points regarding this - {additional}. Structure your essay with a clear introduction, body paragraphs that support your thesis, and a strong conclusion. Use evidence and examples to illustrate your points. Ensure your writing is clear, concise, and engaging. Pay attention to tone given above, grammar, spelling, and punctuation. Most important, give me essay {optioneg1} long."""

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if option == "Text Generation":
        with st.form("myform"):
            ip = st.text_input("Enter whatever you want to enter..")
            submitted = st.form_submit_button("Submit")

            prompt = ip

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if mailtype == "Compose":
        with st.form("myformcompose"):
            subject = st.text_input("Subject of Email")
            Purpose = st.text_input("Purpose of Email")
            submitted = st.form_submit_button("Submit")

            prompt = f"""Compose a professional email with a tone appropriate for the purpose of {Purpose}. **To:** {receiver} **From:** {sender} **Subject:** {subject}
            **Body:**
            Begin the email with a friendly and appropriate greeting, addressing the recipient by name.
            Clearly state the purpose of the email in the first sentence or two.
            Provide concise and relevant information related to the purpose, using a clear and easy-to-read format.
            Structure the body paragraphs logically, using bullet points or numbered lists if necessary.
            Very important Maintain a {emailtone} throughout the email.
            **Closing:**
            End the email with a polite closing phrase, such as "Sincerely," "Best regards," or "Thank you."
            Include the sender's full name and contact information (email address, phone number, etc.) below the closing.
            **Additional details:**
            - Proofread the email carefully before sending to ensure accuracy and clarity.
            - The email length must be {optionec1} and give me in language {emaillang}."""

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if mailtype == "Reply":
        with st.form("myformreply"):
            replyto = st.text_area("Received Mail")
            subject1 = st.text_input("Subject of Email")
            Purpose1 = st.text_input("Purpose of Email")
            submitted = st.form_submit_button("Submit")

            prompt = f"""**Analyze the following email received from {receiver1} and generate a suitable response for {sender1}:**
            **Subject:** {subject1}
            **Body:** {replyto}
            **Context and Purpose:**
            * **Purpose of the email:** {Purpose1}
            * **Desired tone of the reply:** {emailtone1}
            **Specific Points and Instructions:**
            * **Key issues or requests raised by the sender:** Briefly summarize the main points the sender wants to address.
            * **Specific questions to answer:** List any specific questions you need to answer in the reply.
            * **Desired action or outcome:** What do you want to achieve with your reply? (e.g., Schedule a meeting, provide information, address concerns)
            **Reply Generation:**
            * **Generate a reply that is:**
                * Clear, concise, and {emailtone1} tone
                * Start the email with a polite phrase as per the post of receiver (e.g., Respected, Dear, etc.)
                * Consistent with the tone of the original email
                * Addresses the sender's concerns or requests
                * Takes the appropriate action based on the purpose of the email
            **I look forward to assisting you in crafting the perfect email response in language {emaillang1} and reply must have length {optionec2}!"""

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if optionpg1 == "Linkedin":
        with st.form("myformlinkedin"):
            desc = st.text_area("Describe About Post")

            submitted = st.form_submit_button("Submit")

            prompt = f"""**Craft a LinkedIn post that captures attention and sparks conversations.**
            **Imagine you're a skilled storyteller, weaving a captivating narrative that blends:**
            - A {style} tone, resonating with your audience's emotions and values.
            - A length of approximately {optionlp} words, delivering your message concisely and impactfully.
            - I work in the domain of {domain}.
            - These key elements, handpicked to shape your story: {desc}

    **Guidelines for your masterpiece:**


            - **Paint a vivid picture:** Use descriptive language and maintain post tone like {style}.
            - **Add Emoji to make post more attractive**
            - **Weave in relevant keywords and hashtags:** Enhance visibility and reach within your professional network.
            - **Polish your prose to perfection:** Ensure clarity, conciseness, and flawless grammar.
            **Now, Bard, unleash your creativity and craft a LinkedIn post that resonates, inspires, and leaves a lasting impression!**"""

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if optionpg1 == "Twitter/X":
        with st.form("myformtwitter"):
            desc1 = st.text_area("Describe About Post")
            submitted = st.form_submit_button("Submit")

            prompt = f"""Prompt for generating Twitter posts that capture human-like creativity and authenticity.
            Template:
            Write a tweet that is {style1} in tone, {optiontp} characters long, and incorporates the following elements:
            * {desc1}
            Ensure the tweet is:
            * Engaging and attention-grabbing
            * Clear and concise
            * Likely to resonate with their audience
            * Add Mentions if possible and must add tags at the end
            Feel free to use creative language, wordplay, humor, or other techniques to make the tweet stand out.
            """

            if not api_key:
                st.info("Please add your API key to continue.")
            elif submitted:
                response = generate(prompt)
                st.write(response.text)

    if option == "Image Captioning and Tagging":
        #st.markdown("### Image Captioning, Tagging, and Description")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            if st.button('Upload'):
                if api_key.strip() == '':
                    st.error('Enter a valid API key')
                else:
                    # Create the 'temp' directory if it doesn't exist
                    if not os.path.exists("temp"):
                        os.makedirs("temp")
                    
                    file_path = os.path.join("temp", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    img = Image.open(file_path)
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        caption = model.generate_content(["Write a caption for the image in english", img])
                        tags = model.generate_content(["Generate 5 hash tags for the image in a line in english", img])
                        st.image(img, caption=f"Caption: {caption.text}")
                        st.write(f"Tags: {tags.text}")
                        desc = model.generate_content(["Generate description for the image without mentioning like here is the description", img])
                        st.write(f"\nDescription: {desc.text}")
                    except Exception as e:
                        error_msg = str(e)
                        if "API_KEY_INVALID" in error_msg:
                            st.error("Invalid API Key. Please enter a valid API Key.")
                        else:
                            st.error(f"Failed to configure API due to {error_msg}")

# Hide Streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Footer
footer = """
<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}
a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by Laxman.</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
