CREATE TABLE IF NOT EXISTS Guilds (
    id      INTEGER     PRIMARY KEY,
    name    TEXT        NOT NULL,
    active  BOOLEAN     DEFAULT true
);

CREATE TABLE IF NOT EXISTS CustomPrefixes (
    fk_guildId  INTEGER     PRIMARY KEY,
    prefix      TEXT        NOT NULL, 
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Users (
    id          INTEGER     PRIMARY KEY,
    name        TEXT        NOT NULL,
    isBanned    BOOLEAN     DEFAULT false,
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
    isDeleted   BOOLEAN     DEFAULT false,
    misc        TEXT,        
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Roles (
	id                  INTEGER     PRIMARY KEY,
    fk_guildId          INTEGER     NOT NULL,
  	name                TEXT        NOT NULL,
    isRoleAssignable    BOOlEAN     DEFAULT false,     
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
    time            TEXT,       
    FOREIGN KEY(fk_authorId)
        REFERENCES Users (id),
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id),
    FOREIGN KEY(fk_channelId)
        REFERENCES Channels (id)
);

CREATE TABLE IF NOT EXISTS LogoutDates (
    id              INTEGER     PRIMARY KEY,
    date            TEXT        NOT NULL
);

CREATE TABLE IF NOT EXISTS DesignatedChannels (
    id              INTEGER     PRIMARY KEY,
    name            TEXT        NOT NULL
);

CREATE TABLE IF NOT EXISTS DesignatedChannels_Channels (
    fk_designatedChannelsId INTEGER     NOT NULL,
    fk_channelsId           INTEGER     NOT NULL,
    FOREIGN KEY(fk_channelsId)
        REFERENCES Channels (id),
    FOREIGN KEY(fk_designatedChannelsId)
        REFERENCES DesignatedChannels (id)
);

CREATE TABLE IF NOT EXISTS WelcomeMessages (
    id                      INTEGER     PRIMARY KEY,
    fk_guildId              INTEGER     UNIQUE NOT NULL,
    content                 TEXT        NOT NULL,
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Tags (
    id                      INTEGER     PRIMARY KEY,
    name                    TEXT        NOT NULL,
    content                 TEXT        NOT NULL,
    useCount                INTEGER     DEFAULT 0,
    CreationDate            TEXT        NOT NULL,
    fk_GuildId              INTEGER     NOT NULL,
    fk_UserId               INTEGER     NOT NULL,
    FOREIGN KEY(fk_GuildId)
        REFERENCES Guilds (id),
    FOREIGN KEY(fk_UserId)
        REFERENCES Users (id)
);


CREATE TABLE IF NOT EXISTS ClaimsMapping (
    id                       INTEGER      PRIMARY KEY,
    claimName                INTEGER      NOT NULL,
    fk_roleId                INTEGER      NOT NULL,
    fk_guildId               INTEGER      NOT NULL,
    FOREIGN KEY(fk_roleId)
        REFERENCES Roles (id),
    FOREIGN KEY(fk_GuildId)
        REFERENCES Guilds (id)
);

CREATE TABLE IF NOT EXISTS Reminders (
    id                      INTEGER          PRIMARY KEY,
    fk_userId               INTEGER          NOT NULL,
    fk_messageId            INTEGER          NOT NULL,
    link                    TEXT             NOT NULL,
    time                    INTEGER          NOT NULL,
    FOREIGN KEY(fk_messageId)
        REFERENCES Messages(id),
    FOREIGN KEY(fk_userId)
        REFERENCES Users(id)
);

CREATE TABLE IF NOT EXISTS Infractions (
    id                       INTEGER      PRIMARY KEY,
    fk_guildId               INTEGER      NOT NULL,
    fk_authorId              INTEGER      NOT NULL,
    fk_subjectId             INTEGER      NOT NULL,
    iType                    TEXT CHECK(iType IN ('ban', 'mute', 'warn')) NOT NULL,
    duration                 INTEGER,
    reason                   TEXT,
    active                   BOOLEAN,
    time                     TEXT,
    FOREIGN KEY(fk_guildId)
        REFERENCES Guilds (id),
    FOREIGN KEY(fk_authorId)
        REFERENCES Users (id),
    FOREIGN KEY(fk_subjectId)
        REFERENCES Users (id)
)
