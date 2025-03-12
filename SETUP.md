# Implementation Roadmap: Django App Provisioning Workflow

## **Step 1: User Input**
1. Prompt the user for:
   - Destination directory for the new Django app.
   - Name of the base Django application.
   - Public URL of the application.

## **Step 2: Poetry Virtual Environment Setup**
2. Create a new Poetry virtual environment using the specified name.
3. List available Python versions and allow the user to select one.
4. Install the selected Python version within the Poetry environment.

## **Step 3: Install Required Dependencies**
5. Add the following libraries to the Poetry environment:
   - `django = "4.2.11"`
   - `psycopg2-binary = "^2.9.10"`
   - `python-dotenv = "^1.0.1"`
   - `djangorestframework = "^3.15.2"`
   - `django-filter = "^25.1"`
   - `django-cors-headers = "^4.7.0"`
   - `django-crispy-forms = "^2.3"`
   - `crispy-bootstrap5 = "^2024.10"`

## **Step 4: Verify and Install Global Dependencies**
6. Check if `gunicorn` and `nginx` are installed globally.
7. If they are not installed, install them using the system package manager (not Poetry).

## **Step 5: Configure Django Project Structure**
8. Create the Django project with the specified name.
9. Set up the recommended folder structure:
```
├── manage.py 
├── config/
│ ├── settings/
│ │ ├── base.py
│ │ ├── dev.py
│ │ ├── test.py
│ │ ├── prod.py
│ ├── wsgi.py
│ ├── asgi.py
│ ├── urls.py
├── apps/ 
│ ├── main/ 
│ │ ├── models.py 
│ │ ├── views.py 
│ │ ├── urls.py 
│ │ ├── forms.py 
│ │ ├── serializers.py 
│ │ ├── static/ 
│ │ ├── templates/ 
├── static/ 
├── templates/ 
├── scripts/ 
├── logs/ 
├── .env 
├── requirements.txt 
├── README.md

```

## **Step 6: Database Configuration**
10. Set up a PostgreSQL database using the application name.
11. Store database credentials in a `.env` file.
12. Apply Django migrations.
13. Create a Django superuser.

## **Step 7: Create Home Page**
14. Use Bootstrap templates to generate a default home page.
15. Ensure the home page is set as the default route in `urls.py`.

## **Step 8: Environment Configuration**
16. Configure `.env` files for:
 - Development (`.env.dev`)
 - Testing (`.env.test`)
 - Production (`.env.prod`)
17. Modify `settings/base.py` to load environment-specific settings dynamically.

## **Step 9: Web Server Configuration**
18. Configure Gunicorn settings to work with the Django project.
19. Modify Nginx configuration to serve the Django app:
 - Define upstream Gunicorn service.
 - Set up static and media file serving.
 - Configure SSL if required.

## **Step 10: Finalization and Testing**
20. Validate installation by running:
 - `python manage.py check`
 - `python manage.py runserver` (development)
 - `gunicorn config.wsgi` (production)
21. Ensure the application is accessible via the public URL.
22. Output a summary of the configuration and next steps for deployment.

---
