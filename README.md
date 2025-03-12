# VarAI - Network Device Configuration Management System

VarAI is a Django-based, multi-user system that manages Clients and Projects, parses network device files, organizes structured inventory data, and generates AI-assisted reports. The solution leverages CrewAI—an AI-empowered workflow comprising multiple specialized agents—to parse device configurations, generate reports based on project intent, and streamline collaboration.

## Features

- **Client Management**: Track client organizations and their contact information
- **Project Management**: Organize work by projects associated with clients
- **Device Configuration Parsing**: Upload and parse network device configuration files
- **Inventory Management**: Store structured data about network devices, interfaces, VRFs, ACLs, and routing tables
- **AI-Assisted Reporting**: Generate reports using CrewAI for intelligent analysis

## Project Structure

The project follows a clean structure with all Django code in the `src/` directory:

```
.
├── manage.py              # Project management script
├── src/                   # Main source code directory
│   ├── apps/              # Django applications
│   │   ├── clients/       # Client management
│   │   ├── projects/      # Project management per client
│   │   ├── parsers/       # Device file uploads and parsing logic
│   │   ├── inventory/     # Stores all parsed configurations
│   │   └── reports/       # AI-driven report generation
│   ├── media/             # User-uploaded files
│   ├── static/            # Static files
│   ├── staticfiles/       # Collected static files for production
│   ├── templates/         # HTML templates
│   ├── varai/             # Project configuration
│   └── manage.py          # Django management script (inner)
└── .env                   # Environment variables
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Poetry (for dependency management)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd varai
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   # Django settings
   DEBUG=True
   SECRET_KEY=your_secret_key
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database settings
   DB_NAME=varai
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   # Email settings
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=example@example.com
   EMAIL_HOST_PASSWORD=your_email_password
   EMAIL_USE_TLS=True
   ```

4. Create the PostgreSQL database:
   ```
   createdb varai
   ```

5. Run migrations:
   ```
   poetry run python manage.py migrate
   ```

6. Create a superuser:
   ```
   poetry run python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   poetry run python manage.py runserver
   ```

## Usage

1. Access the admin interface at `http://localhost:8000/admin/` to manage clients, projects, and other data.
2. Use the API endpoints at `http://localhost:8000/api/` to interact with the system programmatically.

## API Endpoints

- `/api/clients/` - Client management
- `/api/projects/` - Project management
- `/api/parsers/` - Device file uploads and parsing
- `/api/inventory/` - Inventory data access
- `/api/reports/` - Report generation and access

## Development

### Running Tests

```
poetry run python manage.py test
```

### Creating Migrations

```
poetry run python manage.py makemigrations
```

## License

[Specify your license here]

## Contributors

[List contributors here] 