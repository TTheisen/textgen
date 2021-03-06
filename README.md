# textgen

### Objective of Project:

Use the opinions, statements, and questions of 330 million Reddit users as training data to generate personalized replies to a given comment on a post. The scope of subreddits used in this project are those that may contain content related to the United States highly debated topics such as healthcare, immigration, and gun control. This project *is not intended to troll*, but produce coherent, personalized responses as to maximize the probability our model's reply will not be detected as being generated by a machine and will subsequently be replied to. 

### Overview of Project Architecture:

The image below represents a two topic architecture. The architecture is setup to be distributed so any number of topics are theoretically possible. For instance, topic1 may be healthcare and topic2 may be immigration. Each of these topics have a predefined list of subreddits to stream from using the Reddit API. Each topic also has a predefined set of target keywords to search for within the title of each streamed post. For example, 'healthcare' is a keyword for the healthcare topic. If a keyword is contained in the title, a new document is created within a MongoDB collection that stores that posts information. 

Post Information Stored: Postid, Title, Author, DateTime Posted, Number of Current Upvotes, and Number of Current Comments

The issue with streaming data from Reddit is all posts are brand new, meaning most posts will have no comments when the posts information is stored in MongoDB. Thus, every hour, the collection is polled and another call is made via the Reddit API to update the current number of comments for each post. If the second difference of the number of comments in a given post turns negative the post is archived and the postid is sent via Kafka producer to the scrape program. The Kafka consumer receives this postid and proceeds to scrape all comments under the post in linear order i.e. top to bottom. Each comment/record of the post is serialized and sent via another Kafka Producer to a program that transforms each record. Each record is inserted into a Postgres database.

Comment Information Sent/Stored: Postid, Comment Parent ID, Comment ID, Comment Author, Comment, Level, Thread, and Upvotes

The 3 major operations performed on each post are determining the post's keywords, all interactions between users on the post, and extracting any URLs mentioned. After the operations are performed on a record the Neo4j graph database is updated to reflect this new information. 


![System Design](https://user-images.githubusercontent.com/32493141/54935725-e7d21a80-4eee-11e9-8db9-7632947d5f07.PNG)

### Network of Posts and Keywords:

Suppose there are two posts 'A' and 'B'. To quickly determine if 'A' and 'B' are related in some way, we can query the graph and see if 'A' and 'B' both contain a given keyword. 

![Keywords](https://user-images.githubusercontent.com/32493141/54936446-7dba7500-4ef0-11e9-80d9-40b6f025661e.PNG)

### Network of Interactions between Comment Authors and Posts:


Suppose there are two posts 'A' and 'B'. User1 has a previous interaction with User2 on post 'A'. Today, post 'B' was published and User1 interacted with User2 again. The weight on the edge of the graph between User1 and User2 would be updated from 1 to 2. Additionally, both User1 and User2 would have an edge (relationship) with the post 'A' and post 'B'. 


![Interactions](https://user-images.githubusercontent.com/32493141/54939356-67afb300-4ef6-11e9-902a-1fa85d44fd61.PNG)




**API Used:** Reddit API (PRAW)

**Tools Used:** Python, Scala, SQL, Cypher, Apache Spark, Apache Kafka

**Databases Used:** MongoDB, Postgres, Neo4j
