#!/usr/bin/env python
"""
Test script to verify the unified reports page functionality
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

# Add the project directory to the Python path
sys.path.append('c:\\Users\\Play\\pop')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

def test_unified_reports_page():
    """Test the unified reports page"""
    # Create a test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Create a test client
    client = Client()
    
    # Log in the user
    login_result = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {login_result}")
    
    # Test accessing the unified reports page
    response = client.get('/reports/')
    print(f"Reports page status code: {response.status_code}")
    
    # Check if the page loads successfully
    if response.status_code == 200:
        print("SUCCESS: Unified reports page loads correctly")
        # Check if the page contains expected elements
        content = response.content.decode('utf-8')
        if 'Gerar Novo Relatório' in content:
            print("SUCCESS: Report generation form is present")
        else:
            print("ERROR: Report generation form is missing")
            
        if 'Relatórios Salvos' in content:
            print("SUCCESS: Saved reports section is present")
        else:
            print("ERROR: Saved reports section is missing")
    else:
        print("ERROR: Failed to load unified reports page")
    
    # Clean up
    user.delete()

if __name__ == '__main__':
    test_unified_reports_page()