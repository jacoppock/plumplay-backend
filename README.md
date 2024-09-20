# PlumPlay Backend with FooMedical Frontend

## Running the Application

1. Build and start the Docker containers:
   ```
   make start-all
   ```

2. Access the frontend at `http://localhost:3000`
3. Access the backend API at `http://localhost:8000`

## Development

- Frontend code is located in `src/frontend`
- Backend code is located in `src/backend`

Refer to the respective README files in each directory for more detailed instructions.

## Prerequisites

- Docker
- Docker Compose
- Make (optional, but recommended for easier command execution)

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/your-username/plumplay-backend.git
   cd plumplay-backend
   ```

2. Create a `.env` file in the project root and add necessary environment variables:
   ```
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ```

3. Build and start the Docker containers:
   ```
   make build
   make up
   ```

   If you don't have Make installed, you can use Docker Compose directly:
   ```
   docker-compose build
   docker-compose up -d
   ```

4. Apply database migrations:
   ```
   make migrate
   ```

5. Create a superuser (optional):
   ```
   make createsuperuser
   ```

6. The application should now be running at `http://localhost:8000`

## Available Commands

Use the following Make commands to manage the application:

- `make build`: Build the Docker containers
- `make up`: Start the Docker containers
- `make down`: Stop the Docker containers
- `make restart`: Restart the Docker containers
- `make logs`: View logs for all services
- `make migrate`: Apply database migrations
- `make createsuperuser`: Create a Django superuser
- `make collectstatic`: Collect static files
- `make shell`: Open Django shell
- `make lint`: Run linters
- `make test`: Run tests
- `make venv`: Create a virtual environment for local development
- `make install`: Install project dependencies in the virtual environment

To set up a local development environment:

1. Create a virtual environment:
   ```
   make venv
   ```

2. Activate the virtual environment:
   - On Unix or MacOS: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`

3. Install project dependencies:
   ```
   make install
   ```

This will create a virtual environment and install all necessary dependencies for local development.

## Development

This project uses Poetry for dependency management. To add new dependencies:

1. Install Poetry if you haven't already:
   ```
   pip install poetry
   ```

2. Add a new dependency:
   ```
   poetry add package_name
   ```

3. Update the `pyproject.toml` and `poetry.lock` files in the repository.

## Testing

Run the test suite using:

```
make test
```

## Deployment

[