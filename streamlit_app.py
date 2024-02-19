import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO
import base64

# Function to get image URL from uploaded file
def get_image_url(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    data_uri = base64.b64encode(buffer.read()).decode('utf-8')
    return "data:image/jpeg;base64," + data_uri

# Streamlit app layout
st.title("AI Image Analysis")

# Display the header image
st.image("https://lwfiles.mycourse.app/65a6a0bb6e5c564383a8b347-public/4ef4ee108068d6f94365c6d2360b3a66.png")

# Sidebar for API key and options
openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
model_option = st.sidebar.selectbox("Select Model", ["gpt-4-vision-preview", "gpt-4-1106-vision-preview"], index=0)

# Tab layout
tab1, _ = st.tabs(["Image Analysis", "Other Features"])

with tab1:
    st.subheader("Upload an Image for Analysis")
    uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])
    user_prompt = st.text_area("Enter Prompt", "What's in this image?")

    if st.button("Analyze Image"):
        if uploaded_image and openai_api_key:
            # Configure OpenAI client
            openai.api_key = openai_api_key

            # Get image URL
            image_url = get_image_url(Image.open(uploaded_image))

            # Request to OpenAI
            response = openai.ChatCompletion.create(
                model=model_option,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_prompt},
                                    {"type": "image_url", "image_url": {"url": image_url}}],
                    }
                ],
                max_tokens=300,
            )

            st.write(response.choices[0].text)
        else:
            st.warning("Please upload an image and ensure the API key is entered.")
