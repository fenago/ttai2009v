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
# st.image("https://lwfiles.mycourse.app/65a6a0bb6e5c564383a8b347-public/81791ed30dbcd226feec79d58591be68.png")
st.image("https://reddotmiami.com/wp-content/uploads/bfi_thumb/rdm17-sponsors-feature_miami-dade-college-ni0a0heylglji1208ljp6e0q3d88qq8jbo2h48yk4w.gif")

# Sidebar for API key and options
openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
model_option = st.sidebar.selectbox("Select Model", ["gpt-4-vision-preview", "gpt-4-1106-vision-preview"], index=0)

# Tab layout
tab1, tab2 = st.tabs(["Image Analysis", "DALL-E Image Generation"])

with tab1:
    st.subheader("Upload an Image or Provide Image URL for Analysis")
    image_url = st.text_input("Or enter an Image URL", "")
    uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])
    user_prompt = st.text_area("Enter Prompt", "What's in this image?")

    if st.button("Analyze Image"):
        if openai_api_key and (uploaded_image or image_url):
            image_to_analyze = None

            if uploaded_image:
                # Display and process the uploaded image
                image_to_analyze = Image.open(uploaded_image)
                st.image(image_to_analyze, caption='Uploaded Image', use_column_width=True)
                image_url = get_image_url(image_to_analyze)
            elif image_url:
                try:
                    # Verify and display the image from the URL
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image_to_analyze = Image.open(BytesIO(response.content))
                    st.image(image_to_analyze, caption='Image from URL', use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading image from URL: {e}")
                    image_url = None  # Reset image URL if there's an error

            if image_url:
                # Configure OpenAI client
                openai.api_key = openai_api_key

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
                try:
                    # Extract the response text correctly according to the response structure
                    result_text = response['choices'][0]['message']['content']
                    st.write(result_text)
                except KeyError as e:
                    st.error(f"Error extracting response: {e}")
                    st.write(response)  # Print the whole response for debugging
        else:
            st.warning("Please provide an image URL or upload an image and ensure the API key is entered.")

# Adding the second tab for DALL-E image generation
with tab2:
    st.subheader("Generate Images with DALL-E")

    # DALL-E settings
    dalle_model = st.selectbox("Select DALL-E Model", ["dall-e-3", "dall-e-2"], index=0)
    dalle_prompt = st.text_input("Enter Prompt for DALL-E", "a white siamese cat")
    dalle_size = st.selectbox("Select Image Size", ["1024x1024", "512x512", "256x256"], index=0)
    dalle_quality = st.selectbox("Select Image Quality", ["standard", "hd"], index=0)
    dalle_n = st.slider("Number of Images", 1, 4, 1)

    if st.button("Generate Image"):
        if openai_api_key:
            # Configure OpenAI client
            openai.api_key = openai_api_key

            try:
                # Request to OpenAI DALL-E
                response = openai.Image.create(
                    model=dalle_model,
                    prompt=dalle_prompt,
                    size=dalle_size,
                    quality=dalle_quality,
                    n=dalle_n,
                )

                # Display generated images
                for i in range(len(response.data)):
                    st.image(response.data[i].url, caption=f"Generated Image {i+1}")

            except Exception as e:
                st.error(f"Error generating images with DALL-E: {e}")
        else:
            st.warning("Please enter the OpenAI API key.")
