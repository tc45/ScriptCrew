# Testing Guide for VarAI

This guide explains how to run and write tests for the VarAI system.

## Overview

VarAI uses Django's testing framework along with some custom testing scripts to ensure code quality and correctness. Tests are organized into several categories:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test how components work together
- **Functional tests**: Test end-to-end behavior from a user perspective
- **Direct tests**: Standalone scripts that test specific functionality

## Running Standard Django Tests

### Running All Tests

To run all tests for the entire project:

```bash
cd /path/to/varai
python src/manage.py test
```

### Running Tests for a Specific App

To run tests for a specific app:

```bash
python src/manage.py test apps.clients
python src/manage.py test apps.projects
python src/manage.py test apps.parsers
python src/manage.py test apps.inventory
python src/manage.py test apps.reports
```

### Running a Specific Test Case or Method

To run a specific test case or method:

```bash
# Run a specific test case
python src/manage.py test apps.parsers.tests.DeviceFileModelTest

# Run a specific test method
python src/manage.py test apps.parsers.tests.DeviceFileModelTest.test_device_file_creation
```

### Running Tests with Coverage

To measure test coverage:

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='src/apps' src/manage.py test

# Generate a coverage report
coverage report

# Generate an HTML coverage report
coverage html
# Then open htmlcov/index.html in a browser
```

## Parser-Specific Tests

The network device parsers have specialized tests that can be run in different ways.

### Running Parser Tests via Django

```bash
# Run all parser tests
python src/manage.py test apps.parsers.tests.test_parsers

# Run tests for specific parser components
python src/manage.py test apps.parsers.tests.test_parsers.TestBaseParser
python src/manage.py test apps.parsers.tests.test_parsers.TestCiscoIOSParser
python src/manage.py test apps.parsers.tests.test_parsers.TestParserFactory
python src/manage.py test apps.parsers.tests.test_parsers.TestDeviceFileParseMethod
```

### Running Direct Parser Tests

For cases where Django's test discovery has issues or you need more control, you can use the direct test scripts:

```bash
# Test basic parser functionality
python src/test_parsers_directly.py

# Test parser factory
python src/test_parser_factory_directly.py

# Test DeviceFile integration
python src/test_device_file_parse.py
```

These scripts provide simple, direct testing of the parser components without the overhead of Django's test runner.

## Testing Specific Features

### Client and Project Management

```bash
python src/manage.py test apps.clients
python src/manage.py test apps.projects
```

### Device File Upload and Parsing

```bash
python src/manage.py test apps.parsers
```

### Inventory Data Storage

```bash
python src/manage.py test apps.inventory
```

### AI-Assisted Reporting

```bash
python src/manage.py test apps.reports
```

## Writing New Tests

### Unit Test Structure

Django unit tests typically follow this structure:

```python
from django.test import TestCase
from apps.your_app.models import YourModel

class YourModelTest(TestCase):
    def setUp(self):
        """Set up the test data."""
        # Create test data
        self.test_object = YourModel.objects.create(
            name="Test Name",
            description="Test Description"
        )
    
    def test_model_creation(self):
        """Test that a model instance can be created."""
        self.assertEqual(self.test_object.name, "Test Name")
        self.assertEqual(self.test_object.description, "Test Description")
    
    def test_model_method(self):
        """Test a method of the model."""
        result = self.test_object.some_method()
        self.assertEqual(result, expected_value)
```

### Parser Test Structure

When writing tests for parsers, follow this structure:

```python
import unittest
from apps.parsers.parsers.your_parser import YourParser

class TestYourParser(unittest.TestCase):
    def setUp(self):
        """Set up the test case."""
        self.parser = YourParser()
        self.test_config = """
        # Sample device configuration for testing
        hostname TestDevice
        interface Ethernet1
         description Test Interface
         ip address 192.168.1.1 255.255.255.0
        """
    
    def test_detect_device_type(self):
        """Test that the parser correctly identifies configurations."""
        self.assertTrue(self.parser.detect_device_type(self.test_config))
        
        non_matching_config = "this is not a valid configuration"
        self.assertFalse(self.parser.detect_device_type(non_matching_config))
    
    def test_extract_hostname(self):
        """Test that the parser correctly extracts the hostname."""
        hostname = self.parser.extract_hostname(self.test_config)
        self.assertEqual(hostname, "TestDevice")
    
    def test_parse(self):
        """Test the complete parsing process."""
        parsed_data = self.parser.parse(self.test_config)
        
        self.assertEqual(parsed_data["device_type"], "your-device-type")
        self.assertEqual(parsed_data["hostname"], "TestDevice")
        self.assertEqual(len(parsed_data["interfaces"]), 1)
        # Check other expected data
```

### Using Mocks

For testing components that have external dependencies, use mocks:

```python
from unittest.mock import patch, MagicMock
from django.test import TestCase
from apps.your_app.models import YourModel

class YourModelTest(TestCase):
    @patch('apps.your_app.some_module.external_function')
    def test_method_with_external_dependency(self, mock_external_function):
        """Test a method that calls an external function."""
        # Configure the mock
        mock_external_function.return_value = "mock result"
        
        # Create test instance
        obj = YourModel.objects.create(name="Test")
        
        # Call the method that uses the external function
        result = obj.method_that_calls_external_function()
        
        # Assert the result
        self.assertEqual(result, "expected result")
        
        # Verify the mock was called correctly
        mock_external_function.assert_called_once_with("expected argument")
```

## Testing Views

### Testing Function-Based Views

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.your_app.models import YourModel

class YourViewTest(TestCase):
    def setUp(self):
        """Set up the test case."""
        self.client = Client()
        self.test_object = YourModel.objects.create(
            name="Test Name",
            description="Test Description"
        )
        self.url = reverse('your_app:view_name', args=[self.test_object.id])
    
    def test_view_get(self):
        """Test GET request to the view."""
        response = self.client.get(self.url)
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check context
        self.assertEqual(response.context['object'], self.test_object)
        
        # Check template used
        self.assertTemplateUsed(response, 'your_app/template.html')
    
    def test_view_post(self):
        """Test POST request to the view."""
        data = {
            'name': 'Updated Name',
            'description': 'Updated Description'
        }
        response = self.client.post(self.url, data)
        
        # Check redirect
        self.assertRedirects(response, reverse('your_app:success_view'))
        
        # Check database update
        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.name, 'Updated Name')
```

### Testing Class-Based Views

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.your_app.models import YourModel

class YourViewTest(TestCase):
    def setUp(self):
        """Set up the test case."""
        self.client = Client()
        self.test_object = YourModel.objects.create(
            name="Test Name",
            description="Test Description"
        )
        self.list_url = reverse('your_app:list')
        self.detail_url = reverse('your_app:detail', args=[self.test_object.id])
    
    def test_list_view(self):
        """Test the list view."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Name")
    
    def test_detail_view(self):
        """Test the detail view."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.test_object)
```

## Testing API Endpoints

For testing API endpoints, you can use Django REST framework's `APITestCase`:

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.your_app.models import YourModel

class YourAPITest(APITestCase):
    def setUp(self):
        """Set up the test case."""
        self.test_object = YourModel.objects.create(
            name="Test Name",
            description="Test Description"
        )
        self.list_url = reverse('api:your_model-list')
        self.detail_url = reverse('api:your_model-detail', args=[self.test_object.id])
    
    def test_list_api(self):
        """Test the list API endpoint."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Name")
    
    def test_create_api(self):
        """Test the create API endpoint."""
        data = {
            'name': 'New Object',
            'description': 'New Description'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(YourModel.objects.count(), 2)
        self.assertEqual(YourModel.objects.last().name, 'New Object')
```

## Troubleshooting Common Test Issues

### Test Discovery Issues

If Django's test discovery isn't finding your tests:

1. Ensure your test files follow the naming convention: start with `test_` or end with `_test.py`
2. Make sure your test directory has an `__init__.py` file
3. Check that your test classes inherit from `TestCase` or another test class
4. Verify your test methods start with `test_`

### Database Issues

If tests fail due to database issues:

1. Tests use a separate test database that's created and destroyed for each test run
2. Make sure your migrations are up to date: `python src/manage.py makemigrations`
3. If using fixtures, ensure they're compatible with your current models

### Mock Issues

Common issues with mocks:

1. Make sure you're patching the correct path (where the function is used, not where it's defined)
2. For class methods, use `patch.object()` instead of `patch()`
3. Remember to add mocks as arguments to your test method
4. Check that your mock's return value matches what your code expects

### Slow Tests

If your tests are running slowly:

1. Use `SimpleTestCase` instead of `TestCase` when you don't need database access
2. Use `TransactionTestCase` only when necessary (test database operations are slower)
3. Use tags to run only specific test groups: `python src/manage.py test --tag=fast`
4. Mock external services and API calls

## Continuous Integration

The VarAI project is configured for continuous integration testing. When you push changes to the repository, the CI system will automatically:

1. Run all tests
2. Check code coverage
3. Run linting checks
4. Report any issues

### Setting Up CI Locally

To simulate the CI environment locally:

```bash
# Run all checks
./ci/run_tests.sh

# Run specific check
./ci/run_lint.sh
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Arrange-Act-Assert**: Structure tests with setup, action, and verification phases
3. **Meaningful Names**: Use descriptive test method names that explain what's being tested
4. **Small Tests**: Keep tests focused on testing one thing
5. **Clean Setup/Teardown**: Initialize what you need in `setUp` and clean up in `tearDown`
6. **Use Factories**: For complex model creation, use factory libraries like `factory_boy`
7. **Test Edge Cases**: Don't just test the happy path; also test boundary and error conditions 