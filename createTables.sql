CREATE TABLE postInfo (
    id VARCHAR(20) NOT NULL,
    author VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    subreddit VARCHAR(20) NOT NULL,
    timecreated VARCHAR(30) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE nerInfo (
    nerword VARCHAR(20) NOT NULL,
    nerlabel VARCHAR(20) NOT NULL,
    postid VARCHAR(20),
    FOREIGN KEY (postid) REFERENCES postInfo(id) ON DELETE CASCADE
);