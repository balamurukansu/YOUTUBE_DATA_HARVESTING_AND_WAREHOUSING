#Use Database
use YT_Scrap;

#Create a new database
CREATE DATABASE IF NOT EXISTS YT_Scrap

# Create a yt_channeldetails
CREATE table yt_channeldetails (
Channel_Id	varchar(255) primary key,
Channel_Name	varchar(255),
Channel_Views	varchar(255),
Subscription_Count	int,
Channel_Description	text
);

# Create table  yt_videodetails
CREATE TABLE yt_videodetails (
    Channel_Name varchar(255),
    Channel_Id varchar(255),
    Video_Id varchar(255) PRIMARY KEY,
    video_name varchar(255),
    Tags varchar(255),
    Thumbnail varchar(255),
    Description text,
    Published_Date datetime,
    Duration varchar(255),
    Views_count int,
    Likes_count int,
    Comments_count int,
    Favorite_Count int,
    Caption_Status varchar(255),
    FOREIGN KEY (Channel_Id) REFERENCES yt_channeldetails(Channel_Id)
);

# Create table  yt_commentdetails
CREATE table yt_commentdetails (Channel_Id	varchar(255),
Channel_Name varchar(255),
Comment_Id	varchar(255) primary key,
Video_Id	varchar(255),
Comment_Text	text,
Comment_Author	varchar(255),
Comment_Published	datetime,
FOREIGN KEY (Channel_Id) REFERENCES yt_channeldetails(Channel_Id)
);

# Create table  yt_playlistdetails
CREATE table yt_playlistdetails (Playlist_Id varchar(255) primary key,
Channel_Id	varchar(255),
Channel_Name	varchar(255),
Video_Count	int,
playlistname varchar(255),
FOREIGN KEY (Channel_Id) REFERENCES yt_channeldetails(Channel_Id)
);

show columns from yt_channeldetails;
show columns from yt_videodetails;
show columns from yt_commentdetails;
show columns from yt_playlistdetails;

select * from yt_channeldetails;
select * from yt_videodetails;
select * from yt_commentdetails;
select * from yt_playlistdetails;

#truncate table yt_channeldetails;

