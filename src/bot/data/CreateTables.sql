CREATE TABLE IF NOT EXISTS Guilds (
    id      INTEGER     PRIMARY KEY,
    name    TEXT        NOT NULL
);

CREATE TABLE IF NOT EXISTS Users (
    id          INTEGER     PRIMARY KEY,
    fk_guildId  INTEGER     NOT NULL,
    name        TEXT        NOT NULL,
    isBanned    BOOLEAN     DEFAULT false
    misc        TEXT        
);

CREATE TABLE IF NOT EXISTS Users_Guilds (
    fk_guildId  INTEGER     NOT NULL,
    fk_userId   INTEGER     NOT NULL,
    FOREIGN KEY(fk_userId)
        REFERENCES Users (id),
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Channels (
    id          INTEGER     PRIMARY KEY,
    fk_guildId  INTEGER     NOT NULL,
    name        TEXT        NOT NULL,
    isDeleted   BOOLEAN     DEFAULT false
    misc        TEXT        
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Messages (
    id              INTEGER     PRIMARY KEY,
    fk_guildId      INTEGER     NOT NULL,
    fk_channelId    INTEGER     NOT NULL,
    fk_authorId     INTEGER     NOT NULL,
    content         TEXT        NOT NULL,
    isDeleted       BOOLEAN     NOT NULL DEFAULT False,
    misc            TEXT        
    FOREIGN KEY(fk_authorId)
        REFERENCES Users (id),
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id),
    FOREIGN KEY(fk_channelId)
        REFERENCES Channels (id)
);
