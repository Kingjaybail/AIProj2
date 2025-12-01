How to run

Install Docker and Docker Compose 

Create the required environment files before running the system

Create a file named .env inside the CommBot-backend directory with the following variables
OPENAI_API_KEY=add key here

Create a second .env file inside the CommBot-frontend directory with the following variable
VITE_BACKEND_URL=http://localhost:8000

Make sure both .env files are present before starting the containers

Navigate to the root project directory

Build and run the system with
docker compose up --build

After the containers start

Backend is available at: http://localhost:8000
Frontend is available at: http://localhost:5173

To stop all containers run
docker compose down

To rebuild after making changes run
docker compose up --build
