#Import Necessary Libraries
#Virtual Environment
#python -m venv .venv
from googleapiclient.discovery import build
import pandas as pd
import mysql.connector
from PIL import Image
import streamlit as st

# -------------------------------------------------------------------------------------------- #

#API Details
api_key="AIzaSyCucq7LK4QSLCbB6ffF_aUCI7JS2Yh-hWk"
api_service_name = "youtube"
api_version = "v3"
youtube = build(api_service_name, api_version, developerKey=api_key)

# -------------------------------------------------------------------------------------------- #
#FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(c_id):
    ch_data=[]
    request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id=c_id)
    ch = request.execute()

    for i in range(len(ch['items'])):
         data = {"Channel_Name":ch['items'][i]['snippet']['title'],
            "Channel_Id":ch['items'][i]['id'],
            "Channel_Views":ch['items'][i]['statistics']['viewCount'],
            "Subscription_Count":ch['items'][i]['statistics']['subscriberCount'],
            "Channel_Description":ch['items'][i]['snippet']['description']
        }
    ch_data.append(data)
    return ch_data

# -------------------------------------------------------------------------------------------- #

# FUNCTION TO GET VIDEO IDS
def get_channel_videos(c_id):
    video_ids = []
    response = youtube.channels().list(id=c_id,part="contentDetails").execute()
    # get Uploads playlist id
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(part="snippet",maxResults=50,pageToken=next_page_token,playlistId=playlist_id).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break

    return video_ids

# -------------------------------------------------------------------------------------------- #

# FUNCTION TO GET VIDEO DETAILS
def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response=request.execute()

        for item in response["items"]:
            data=dict(Channel_Name=item['snippet']['channelTitle'],
                    Channel_Id=item['snippet']['channelId'],
                    Video_Id=item['id'],
                    Title=item['snippet']['title'],
                    Tags=item['snippet'].get('tags'),
                    Thumbnail=item['snippet']['thumbnails']['default']['url'],
                    Description=item['snippet'].get('description'),
                    Published_Date=item['snippet']['publishedAt'],
                    Duration=item['contentDetails']['duration'],
                    Views=item['statistics'].get('viewCount'),
                    Likes=item['statistics'].get('likeCount'),
                    Comments=item['statistics'].get('commentCount'),
                    Favorite_Count=item['statistics']['favoriteCount'],
                    Definition=item['contentDetails']['definition'],
                    Caption_Status=item['contentDetails']['caption']
                    )
            video_data.append(data)    
    return video_data

# -------------------------------------------------------------------------------------------- #

#FUNCTION TO GET COMMENT INFORMATION
def get_comment_info(video_ids):
    Comment_data=[]
    for video_id in video_ids:
        try:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                Comment_data.append(data)
        except:
            pass
    return Comment_data

# -------------------------------------------------------------------------------------------- #

#FUNCTION TO GET PLAYLIST INFORMATION
def get_playlist_details(channel_id):
        next_page_token=None
        All_data=[]
        while True:
                request=youtube.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()

                for item in response['items']:
                        data=dict(Playlist_Id=item['id'],
                                Title=item['snippet']['title'],
                                Channel_Id=item['snippet']['channelId'],
                                Channel_Name=item['snippet']['channelTitle'],
                                PublishedAt=item['snippet']['publishedAt'],
                                Video_Count=item['contentDetails']['itemCount'])
                        All_data.append(data)

                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
        return All_data

# -------------------------------------------------------------------------------------------- #
#Establish connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Fiitjee@123",
    database="YT_Scrap"
)

# Create cursor
cursor = conn.cursor()
# -------------------------------------------------------------------------------------------- #
#Streamlit Code


def main():
    icon = Image.open("youtube-logo.png")
    st.image(icon,width=150)
    st.title("Youtube Data Harvesting & Warehousing") 
    # st.sidebar("By Balamurukan")

    # Define the menu options
    menu = ["Extract", "View"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Extract":
        home()
    elif choice == "View":
        data()
  

def home():
    st.markdown("#    ")
    st.write("### Please input YouTube Channel_ID below :")
    channel_id = st.text_input("Channel_ID")

    if channel_id and st.button("Extract Data"):
        ch_details = get_channel_details(channel_id)
        # st.write(channel_id)
        #  st.write(ch_details[0])
        st.write('Channel Name:',ch_details[0]["Channel_Name"])
        st.write('Channel Views:',ch_details[0]["Channel_Views"])
        st.write('Subscription Count:',ch_details[0]["Subscription_Count"]) 
        st.write('Description:',ch_details[0]["Channel_Description"])  

        pl_details=get_playlist_details(channel_id)
        vi_ids=get_channel_videos(channel_id)
        vi_details=get_video_info(vi_ids)
        com_details=get_comment_info(vi_ids)

        df1 = pd.DataFrame(ch_details)
        df2 = pd.DataFrame(pl_details)
        df3 = pd.DataFrame(vi_details)
        df4 = pd.DataFrame(com_details)
        
        # #  st.write("Channel Details", df1)
        # #  st.write("Playlist Details", df2)
        # #  st.write("Video Details", df3)
        # #  st.write("Comment Details", df4)
         
        # Insert Channel Information
        for index, row in df1.iterrows():
            insert_query = '''INSERT IGNORE INTO yt_channeldetails(
                            Channel_Name,
                            Channel_Id,
                            Channel_Views,
                            Subscription_Count,
                            Channel_Description)
                        VALUES (%s, %s, %s, %s, %s)'''
            values = (
                row['Channel_Name'],
                row['Channel_Id'],
                row['Channel_Views'],
                row['Subscription_Count'],
                row['Channel_Description']
                )  
            # print( insert_query, values)
            cursor.execute(insert_query,values)
            conn.commit()

        # Insert Playlist Information
        for index,row in df2.iterrows():
                insert_query1='''INSERT IGNORE INTO yt_playlistdetails(Playlist_Id,
                                            Channel_Id,
                                            Channel_Name,
                                            Video_Count,
                                            playlistname)                                            
                                            values(%s,%s,%s,%s,%s)'''
                values1=(row['Playlist_Id'],
                            row['Channel_Id'],
                            row['Channel_Name'],
                            row['Video_Count'],
                            row['Title']
                            )
                # print( insert_query1, values1)
                cursor.execute(insert_query1,values1)
                conn.commit()
        # Insert Video Information -Error
        for index, row in df3.iterrows():
            insert_query2 = '''INSERT IGNORE INTO yt_videodetails(
                                Channel_Name,
                                Channel_Id,
                                Video_Id,
                                video_name,                            
                                Thumbnail,
                                Description,
                                Published_Date,
                                Duration,
                                Views_count,
                                Likes_count,
                                Comments_count,
                                Favorite_Count,
                                Caption_Status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            values2 = (
                row['Channel_Name'],
                row['Channel_Id'],
                row['Video_Id'],
                row['Title'],         
                row['Thumbnail'],
                row['Description'],
                row['Published_Date'],
                row['Duration'],
                row['Views'],
                row['Likes'],
                row['Comments'],
                row['Favorite_Count'],
                row['Caption_Status']
                )
            # print(insert_query2, values2)   
            cursor.execute(insert_query2, values2)
            conn.commit()

        # Insert Comment Information
        for index,row in df4.iterrows():
            insert_query3='''INSERT IGNORE INTO yt_commentdetails(Channel_Id,
                                                    Comment_Id,
                                                    Video_Id,
                                                    Comment_Text,
                                                    Comment_Author,
                                                    Comment_Published)
                                                    values(%s,%s,%s,%s,%s,%s)'''
            values3=(channel_id,
                    row['Comment_Id'],
                    row['Video_Id'],
                    row['Comment_Text'],
                    row['Comment_Author'],
                    row['Comment_Published']
                    )
            print(insert_query3, values3)
            cursor.execute(insert_query3,values3)
            conn.commit()

            # st.success(Table)
# -------------------------------------------------------------------------------------------- #

def data():
    st.write("Channel Insights!")
    #st.selectbox(label, options, index=0, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, placeholder="Choose an option", disabled=False, label_visibility="visible")
    questions = st.selectbox('Questions',['Select question to get insights',
                              '1. What are the names of all the videos and their corresponding channels?'
                             ,'2. Which channels have the most number of videos, and how many videos do they have?'
                             ,'3. What are the top 10 most viewed videos and their respective channels?'
                             ,'4. How many comments were made on each video, and what are their corresponding video names?'
                             ,'5. Which videos have the highest number of likes, and what are their corresponding channel names?'
                             ,'6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?'
                             ,'7. What is the total number of views for each channel, and what are their corresponding channel names?'
                             ,'8. What are the names of all the channels that have published videos in the year 2022?'
                             ,'9. What is the average duration of all videos in each channel, and what are their corresponding channel names?'
                             ,'10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        cursor.execute("""SELECT distinct video_name AS title, Channel_Name FROM yt_videodetails ORDER BY Channel_Name""")
        dfq1 = pd.DataFrame(cursor.fetchall())
        st.dataframe(dfq1)
    
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        cursor.execute("""SELECT channel_name AS Channel_Name, count(*) As Video_Count FROM yt_videodetails GROUP BY Channel_Name ORDER BY Channel_Name DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        cursor.execute("""SELECT Channel_Name AS Channel_Name, video_name AS Video_Title, Views_count AS Views FROM yt_videodetails ORDER BY Views_count DESC LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
    
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        cursor.execute("""SELECT a.video_id AS Video_id, a.video_name AS Video_Title, b.Total_Comments FROM yt_videodetails AS a LEFT JOIN (SELECT video_id,COUNT(Comment_Id) AS Total_Comments FROM yt_commentdetails GROUP BY video_id) AS b ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cursor.execute("""SELECT Channel_Name AS Channel_Name,video_name AS Title,Likes_count AS Likes FROM yt_videodetails ORDER BY Likes_count DESC LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
        st.dataframe("### :green[Top 10 most liked videos :]")
        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        cursor.execute("""SELECT video_name AS Title, Likes_count AS Likes_Count FROM yt_videodetails ORDER BY Likes_count DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
         
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT Channel_Name AS Channel_Name, Channel_Views AS Views FROM yt_channeldetails ORDER BY Channel_Views DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        cursor.execute("""SELECT Channel_Name AS Channel_Name FROM yt_videodetails WHERE published_date LIKE '2022%' GROUP BY channel_name ORDER BY channel_name""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
        
    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name AS Channel_Name,AVG(duration)/60 AS "Average_Video_Duration (mins)"  FROM yt_videodetails GROUP BY channel_name ORDER BY AVG(duration)/60 DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)
        st.write("### :green[Avg video duration for channels :]")
        
    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cursor.execute("""SELECT Channel_Name AS Channel_Name,Video_ID AS Video_ID,Comments_count AS Comments FROM yt_videodetails ORDER BY Comments_count DESC LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.dataframe(df)

if __name__ == "__main__":
     main()