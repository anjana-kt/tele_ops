### Backend

Prerequistic : Python, Git, Docker


#### Setup
- Install Fastapi and uvicorn `pip install "fastapi[standard]" "uvicorn[standard]"`

#### Docker
An open-source platform that uses operating-system-level virtualization to package, ship, and run applications inside lightweight, isolated containers.
Docker standardizes the runtime environment by bundling the application code with its specific dependencies into a single unit.

Enable Security/Virtualization from BIOS if Docker is not installed
- Dockerfile - for creating an image
- compose.yml - managing containers

- Docker Image → blueprint of instructions to build and run a Docker container
- Docker Container → Running instance of that image
- Docker Compose services can talk to each other using their service names as domain names.

A container is created when a Docker Image is executed. \
Docker builds and runs containers, Kubernetes orchestrates them across clusters.

#### Commands
`docker run`\
`docker ps`\
`docker start`\
`docker stop`\
`docker compose exec <service_name> <command>` -> docker compose exec postgres pg_isready -U miyuki -d telemetryops


SQL alchemy -> Python library to interact with relational dbs like MySQL, PostgreSQL, Oracle etc 
- Create an engine object to handle db connection\
`engine = create_engine(dialect+driver://username:password@host:port/database_name)`

<ins>Lazy Initialization</ins> : The Engine object, returned by the create_engine() function, will not connect to the database yet, the connection will be established the first time only when it is asked to perform a task against the database. This kind of software design pattern is often referred to as Lazy Initialization.

#### PostgreSQL (free & open-source relational database)
The name Postgres (originally styled as POSTGRES) means 

MySQL is built for speed and simplicity, making it the world's most popular choice for web applications like WordPress. PostgreSQL (Postgres) is built for complex data and extensibility, making it the preferred choice for enterprise applications and complex analytical queries.

Competitors (enterprise level):

• Oracle Database: The industry giant for massive corporations; highly secure and powerful, but comes with extremely expensive licensing fees.\
• Microsoft SQL Server: The standard choice for enterprise environments tied into the Microsoft ecosystem (.NET, Azure, Windows Server).\
• IBM Db2: A high-performance enterprise database built for heavy-duty industrial and mainframe computing workloads.

*When running locally where the container is host why do we not need the password for postgresql?*
- Docker compose exec bypasses the network layer and drops straight into the container's OS layer. Because you had the keys to the container kingdom, Postgres trusted your local socket connection.
- FastAPI app needs password to connect to PostgreSQL, it relies entirely on host name, ports, and TCP/IP networks.
`postgresql+asyncpg://postgres:secretpassword@postgres:5432/telemetryops`