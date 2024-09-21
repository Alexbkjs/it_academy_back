# 🚀 Backend FastAPI with PostgreSQL, SQLAlchemy, Alembic, Docker and Docker Compose.

Backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy** and **Docker**. This project serves as a foundation for modern web applications and APIs.

## 🛠️ Features

- **FastAPI**: High-performance Python web framework for building APIs.
- **PostgreSQL**: Powerful, open-source relational database.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **Alembic**: Database migrations tool for SQLAlchemy.
- **Docker**: Streamlines deployment by packaging applications into portable containers, ensuring consistency across environments.
- **Docker Compose**: Simplifies multi-container orchestration with a single configuration file, managing services like databases and APIs efficiently.

## 📝 Prerequisites

The backend was tested with the following front end version of the application: https://github.com/UPCoD-UNKD/it-academy-rpg-front/tree/OLE-21-app-loading-page

It is expected that this version or any other compatible with it, making requests to the backend and the requests are not intercepted by Mock Service Worker(msw).

You can achive it by

- setting the variable VITE_BASE_API_URL in .env(front end side) to the HTTPS address of your back-end
- make sure that either variable VITE_ENABLE_MSW=false in .env(front-end side) or msw handlers were removed from /src/mocks/handlers/index.ts

For example, by removing "...userHandlers" from:

```bash
export const handlers = [...userHandlers, ...questsHandlers, ...avatarsHandlers];
```

quests and avatars routes will still be intercepted and use the data from front-end mock database, while user routes(since there are no handlers(even with enabled msw), will go to external db for data).

To the the URL, your backend end should be exposed and reachable via HTTPS from the Internet.
You can achive it by running:

```bash
ssh -R replaceWithYourSubdomain:80:localhost:9000 serveo.net
```
Use received link(e.g. https://someSubdomain.serveo.net) as VITE_BASE_API_URL on front end side in .env file.

The same can be applied to expose your front end application to receive HTTPS URL which can be used to set it in BotFather so your bot is connected to the correct URL of your front end application.
Replaced the port to port of your front-end application.

```bash
ssh -R replaceWithYourAnotherSubdomain:80:localhost:5173 serveo.net
```

A quick recap on setting front-end up:

- Clone the Repository and Navigate to the Project Directory:

```bash
git clone https://github.com/UPCoD-UNKD/it-academy-rpg-front.git -b OLE-21-app-loading-page
cd it-academy-rpg-front
```

- Install Dependencies

```bash
npm install
```

- Start the Development Server:

```bash
npm run dev
```

- Expose the Development Server():
In new terminal(Ctrl + Shift + ` in VS Code), run:
```bash
ssh -R yourSubdomain:80:localhost:5173 serveo.net
```
Be aware that since it is a free solution from time to time you will get ssh: connect to host serveo.net port 22: Connection refused, can be fixed by running the command once again or wait for a couple of minutes or hours/days) or use alternative(ngrok, localtunnel).

P.S. Docker or Docker Desktop(Windows) should be installed on your machine as well to proceed further.

## 📦 Installation and Setup of the back end

Follow these steps to clone the repository and set up the project locally.

### 1. Clone the Branch

```bash
git clone https://github.com/UPCoD-UNKD/it-academy-rpg-back.git -b front-back_connection_attempt
cd it-academy-rpg-back
```

### 2. Create and Activate a Virtual Environment

For Unix/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Check for Environment Variables(especially Bot Token)

```bash
cp .env_example .env
```

### 4. Build and Start Docker Services

Once you have the repository cloned and the .env file in place, you can proceed to build and start your services with Docker Compose.

- Build the Containers (if it’s the first time or if you need to rebuild):

```bash
docker-compose up --build
```

This will build and start the containers based on the docker-compose.yml file.

If you’ve already built the containers and just want to start them:

```bash
docker-compose up
```

#### 4.1. Database Migrations and Database seeding is handled in docker-compose.yml

```bash
bash -c "python wait_for_db.py && python seed_db.py && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 9000"

```

Otherwise:

#### 4.2. Run Database Migrations (if applicable)

If your project uses a database and includes migration scripts (like Alembic for Python), you’ll likely need to run them after the containers start to make sure the database schema is up to date.

For example, with Alembic, you would use:

```bash
docker-compose exec <service-name> alembic upgrade head
```

Make sure to replace <service-name> with the appropriate service name, typically something like app or web.

#### 4.3. Seed the Database (if needed)

If your project includes a database seeding script, you’ll want to run that to populate the database with initial data. This could be automated in the Docker Compose setup, but if not, you can run it manually:

```bash
docker-compose exec <service-name> python path/to/seed_script.py
```

### 5. Access the Running Application

Once Docker Compose starts the services, you should be able to access the application. Depending on the setup, you can usually reach the app on localhost (or 0.0.0.0) at the defined port in your docker-compose.yml file.

For example, if the app is running on port 9000(you will get an error even if you try to open :

```bash
[http://localhost:9000](http://localhost:9000/docs)
```
#### 5.1 To create a connection to database and verify the present data I am using Database Client JDBC (by Weijan Chen) VS Code extension. To create a connection to it, use the data from .env file.

Up to this moment, if the app is working and you forgot to modify the .env file and disable msw on front end, that is because mocking data. If so, expose your back end with ssh -R someDomain:80:localhost:9000 serveo.net and paste https://someDomain.serveo.net instead of https://example.com keeping the path /api/v1, so you have VITE_BASE_API_URL=https://someDomain.serveo.net/api/v1. 

Disable msw by setting VITE_ENABLE_MSW=false, save the file.

At this moment, app will automatically reload and the request will go through to back end app. You can verify it by seeing user with your details in database > Tables > users. As well as, default user_achievements and user_quest_progress field during user registration. Keep in mind, that if you decide to remove your user profile from db directly, you should remove the fields related to the user from those tables first as they are connected to the user and prevent the action. You can locate the needed fields by user_id field.

To remove the user from GUI: on profile page > gears icon. It will remove the user from db as well.


### 6. Working with the Code

Now that everything is up and running:

- Edit the code locally: You can work on the code within your development environment. If Docker Compose is configured properly, code changes should automatically reflect in the container, especially if you're using volumes in the docker-compose.yml like this:

```bash
volumes:
  - .:/app
```

- Restart Containers (if needed): Sometimes, especially after large changes, you might need to restart the containers:

```bash
docker-compose down
docker-compose up
```

#### 7. Push Changes to the Remote Repository

Once you have made and tested your changes, you can commit and push them to the remote repository:

```bash
git add .
git commit -m "Your commit message"
git push origin <branch-name>
```

#### 8. Push Changes to the Remote Repository

When you’re done working on the project, you can stop the running containers:

```bash
docker-compose down
```

## ✅ Running Tests

To run tests, you can use pytest:

```bash
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue.

1. - Fork the repository.
2. - Create a new branch (git checkout -b feature-branch).
3. - Commit your changes (git commit -m 'Add some feature').
4. - Push to the branch (git push origin feature-branch).
5. - Open a Pull Request.

## 🛡️ License

This project is licensed under the Apache License. See the LICENSE file for more details.

## 🌟 Acknowledgements

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Docker Compose
