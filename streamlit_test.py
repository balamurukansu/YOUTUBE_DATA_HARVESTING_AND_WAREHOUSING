import streamlit as st
from PIL import Image

icon = Image.open("youtube-logo.png")
st.image(icon,width=150)
st.title("Youtube Data Harvesting & Warehousing") 



# def home():
#     channel_id = st.text_input('Enter channel ID') 
#     st.button("Scrape Channel")

# def data():
#     st.write("Welcome to the Data page!")
#     # Add data page content here
#     st.write("Here's some data visualization.")
#     st.line_chart([1, 2, 3, 4, 5])

# def about():
#     st.write("Welcome to the About page!")
#     # Add about page content here
#     st.write("This app is created using Streamlit.")

# def main():
#     st.title("Streamlit Sidebar Menu Example")

#     # Define the menu options
#     menu = ["Home", "Data", "About"]
#     choice = st.sidebar.radio("Menu", menu)

#     if choice == "Home":
#         home()
#     elif choice == "Data":
#         data()
#     elif choice == "About":
#         about()

# if __name__ == "__main__":
#     main()
st.markdown("#    ")
st.write("### Enter YouTube Channel_ID below :")
ch_id = st.text_input("Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')