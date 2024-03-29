/****** Object:  Database [MeetingInfo]    Script Date: 7/26/2022 3:20:02 PM ******/
CREATE DATABASE [MeetingInfo]  (EDITION = 'GeneralPurpose', SERVICE_OBJECTIVE = 'GP_S_Gen5_1', MAXSIZE = 32 GB) WITH CATALOG_COLLATION = SQL_Latin1_General_CP1_CI_AS, LEDGER = OFF;
GO
ALTER DATABASE [MeetingInfo] SET COMPATIBILITY_LEVEL = 150
GO
ALTER DATABASE [MeetingInfo] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [MeetingInfo] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [MeetingInfo] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [MeetingInfo] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [MeetingInfo] SET ARITHABORT OFF 
GO
ALTER DATABASE [MeetingInfo] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [MeetingInfo] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [MeetingInfo] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [MeetingInfo] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [MeetingInfo] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [MeetingInfo] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [MeetingInfo] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [MeetingInfo] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [MeetingInfo] SET ALLOW_SNAPSHOT_ISOLATION ON 
GO
ALTER DATABASE [MeetingInfo] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [MeetingInfo] SET READ_COMMITTED_SNAPSHOT ON 
GO
ALTER DATABASE [MeetingInfo] SET  MULTI_USER 
GO
ALTER DATABASE [MeetingInfo] SET ENCRYPTION ON
GO
ALTER DATABASE [MeetingInfo] SET QUERY_STORE = ON
GO
ALTER DATABASE [MeetingInfo] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 100, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
/*** The scripts of database scoped configurations in Azure should be executed inside the target database connection. ***/
GO
-- ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP = 8;
GO
/****** Object:  User [opendatauser]    Script Date: 7/26/2022 3:20:02 PM ******/
CREATE USER [opendatauser] FOR LOGIN [opendatauser] WITH DEFAULT_SCHEMA=[dbo]
GO
sys.sp_addrolemember @rolename = N'db_datareader', @membername = N'opendatauser'
GO
sys.sp_addrolemember @rolename = N'db_datawriter', @membername = N'opendatauser'
GO
/****** Object:  Table [dbo].[Meeting]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Meeting](
	[Meeting ID] [int] IDENTITY(1,1) NOT NULL,
	[Subject] [nvarchar](max) NULL,
	[Length] [int] NOT NULL,
	[Organizer ID] [int] NOT NULL,
	[Creation time] [datetime] NOT NULL,
	[Status] [nchar](10) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[Meeting ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Meeting times]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Meeting times](
	[Meeting ID] [int] NOT NULL,
	[Time] [nvarchar](50) NOT NULL,
	[Approved] [bit] NOT NULL,
	[MeetingTime ID] [int] IDENTITY(1,1) NOT NULL,
 CONSTRAINT [PK_Meeting times] PRIMARY KEY CLUSTERED 
(
	[MeetingTime ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Accept status]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Accept status](
	[Meeting ID] [int] NOT NULL,
	[Person ID] [int] NOT NULL,
	[MeetingTime ID] [int] NOT NULL,
	[Status] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[Meeting ID] ASC,
	[MeetingTime ID] ASC,
	[Person ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Persons]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Persons](
	[Person ID] [int] IDENTITY(1,1) NOT NULL,
	[E-mail] [nvarchar](50) NULL,
	[Code] [nchar](10) NULL,
PRIMARY KEY CLUSTERED 
(
	[Person ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[AcceptStatusView]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[AcceptStatusView]
	AS SELECT distinct [Accept status].[Meeting ID] as meeting, [Meeting].[Organizer ID] as organizer, [Meeting times].[Time] as currtime, [Accept status].Status as status, [Accept status].[Person ID] as personid, [Persons].[E-mail] as email FROM [Accept status] INNER JOIN [Meeting times] on [Accept status].[MeetingTime ID]=[Meeting times].[MeetingTime ID] inner join [Persons] on [Accept status].[Person ID] = [Persons].[Person ID] inner join [Meeting] on [Accept status].[Meeting ID] = [Meeting].[Meeting ID]
GO
/****** Object:  Table [dbo].[Invitees]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Invitees](
	[Meeting ID] [int] NOT NULL,
	[Person ID] [int] NOT NULL,
	[Last time reminded] [datetime] NULL,
 CONSTRAINT [PK_Invitees] PRIMARY KEY CLUSTERED 
(
	[Meeting ID] ASC,
	[Person ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[NotResponded]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO



CREATE VIEW [dbo].[NotResponded]
AS
SELECT        dbo.Invitees.[Person ID] as invitee, dbo.Persons.[E-mail] AS email, dbo.Invitees.[Meeting ID] AS meetingid, dbo.Persons.[Code] AS code
FROM            dbo.Persons INNER JOIN
                         dbo.Invitees ON dbo.Persons.[Person ID] = dbo.Invitees.[Person ID] LEFT OUTER JOIN
                         dbo.[Accept status] ON dbo.Invitees.[Meeting ID] = dbo.[Accept status].[Meeting ID] AND dbo.Invitees.[Person ID] = dbo.[Accept status].[Person ID]
WHERE        (ISNULL(dbo.[Accept status].[Meeting ID], 0) = 0) AND (ISNULL(dbo.[Accept status].[Person ID], 0) = 0)
GO
/****** Object:  View [dbo].[MeetingList]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[MeetingList]
	AS SELECT        dbo.Invitees.[Meeting ID] AS meetingid, Persons_1.Code AS pers_code, dbo.Persons.Code AS org_code, dbo.Persons.[E-mail] AS org_email, dbo.Meeting.Subject as subject
FROM            dbo.Invitees INNER JOIN
                         dbo.Meeting ON dbo.Invitees.[Meeting ID] = dbo.Meeting.[Meeting ID] INNER JOIN
                         dbo.Persons ON dbo.Meeting.[Organizer ID] = dbo.Persons.[Person ID] INNER JOIN
                         dbo.Persons AS Persons_1 ON dbo.Invitees.[Person ID] = Persons_1.[Person ID]
GO
ALTER TABLE [dbo].[Meeting] ADD  DEFAULT ((60)) FOR [Length]
GO
ALTER TABLE [dbo].[Meeting] ADD  DEFAULT (getdate()) FOR [Creation time]
GO
ALTER TABLE [dbo].[Meeting] ADD  DEFAULT (N'active') FOR [Status]
GO
ALTER TABLE [dbo].[Meeting times] ADD  DEFAULT ((0)) FOR [Approved]
GO
ALTER TABLE [dbo].[Accept status]  WITH CHECK ADD  CONSTRAINT [FK_Accept status_ToTable] FOREIGN KEY([Meeting ID])
REFERENCES [dbo].[Meeting] ([Meeting ID])
GO
ALTER TABLE [dbo].[Accept status] CHECK CONSTRAINT [FK_Accept status_ToTable]
GO
ALTER TABLE [dbo].[Accept status]  WITH CHECK ADD  CONSTRAINT [FK_Accept status_ToTable_1] FOREIGN KEY([Person ID])
REFERENCES [dbo].[Persons] ([Person ID])
GO
ALTER TABLE [dbo].[Accept status] CHECK CONSTRAINT [FK_Accept status_ToTable_1]
GO
ALTER TABLE [dbo].[Accept status]  WITH CHECK ADD  CONSTRAINT [FK_Accept status_ToTable_2] FOREIGN KEY([MeetingTime ID])
REFERENCES [dbo].[Meeting times] ([MeetingTime ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Accept status] CHECK CONSTRAINT [FK_Accept status_ToTable_2]
GO
ALTER TABLE [dbo].[Invitees]  WITH CHECK ADD  CONSTRAINT [FK_Invitees_ToTable] FOREIGN KEY([Meeting ID])
REFERENCES [dbo].[Meeting] ([Meeting ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Invitees] CHECK CONSTRAINT [FK_Invitees_ToTable]
GO
ALTER TABLE [dbo].[Invitees]  WITH CHECK ADD  CONSTRAINT [FK_Invitees_ToTable_1] FOREIGN KEY([Person ID])
REFERENCES [dbo].[Persons] ([Person ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Invitees] CHECK CONSTRAINT [FK_Invitees_ToTable_1]
GO
ALTER TABLE [dbo].[Meeting]  WITH CHECK ADD  CONSTRAINT [FK_Meeting_ToTable] FOREIGN KEY([Organizer ID])
REFERENCES [dbo].[Persons] ([Person ID])
GO
ALTER TABLE [dbo].[Meeting] CHECK CONSTRAINT [FK_Meeting_ToTable]
GO
ALTER TABLE [dbo].[Meeting times]  WITH CHECK ADD  CONSTRAINT [FK_Meeting times_ToTable] FOREIGN KEY([Meeting ID])
REFERENCES [dbo].[Meeting] ([Meeting ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Meeting times] CHECK CONSTRAINT [FK_Meeting times_ToTable]
GO
/****** Object:  StoredProcedure [dbo].[AddNewMeeting]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[AddNewMeeting]  
		@subject nvarchar(MAX),
		@length int,
		@organizerid int,
		@meetingid int OUTPUT
AS
BEGIN
SET NOCOUNT ON
SET @meetingid = 0
		INSERT INTO [Meeting] ([Meeting].[Subject], [Meeting].[Length], [Meeting].[Organizer ID]) VALUES(@subject, @length, @organizerid) 
		SELECT @meetingid  = Scope_identity()
END
GO
/****** Object:  StoredProcedure [dbo].[AddNewMeetingTime]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[AddNewMeetingTime]  
		@meetingid int,
		@mtime datetime,
		@meetingtimeid int OUTPUT
AS
BEGIN
SET NOCOUNT ON
SET @meetingtimeid = 0

	INSERT INTO [Meeting times] ( [Meeting ID], [Time] ) VALUES( @meetingid, CONVERT(DATETIME,@mtime)) 
	SELECT @meetingtimeid = Scope_identity()
END
GO
/****** Object:  StoredProcedure [dbo].[AddNewPerson]    Script Date: 7/26/2022 3:20:02 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[AddNewPerson]  
		@email nvarchar(50),
		@code nchar(10),
		@personid int OUTPUT
AS
BEGIN
SET NOCOUNT ON
SET @personid = 0

	SELECT @personid = Persons.[Person ID] FROM Persons 
	WHERE [Persons].[E-mail] = @email
	
	IF IsNull(@personid, 0) = 0
	BEGIN
		INSERT INTO [Persons] ( [E-mail], [Code] ) VALUES( @email, @code) 
		SELECT @personid = Scope_identity()

	END
END
GO
ALTER DATABASE [MeetingInfo] SET  READ_WRITE 
GO
