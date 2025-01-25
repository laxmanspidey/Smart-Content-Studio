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
    st.image("https://internal-blog.contentstudio.io/wp-content/uploads/2023/04/image26-4.jpg", use_container_width=True)
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
