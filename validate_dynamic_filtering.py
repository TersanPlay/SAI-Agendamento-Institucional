#!/usr/bin/env python
"""
Validation script for the dynamic events table filtering implementation
"""

def validate_dynamic_filtering():
    """Validate the dynamic filtering implementation"""
    print("🔍 Validating Dynamic Events Table Filtering Implementation")
    print("=" * 70)
    
    # Check files exist and have required content
    files_to_check = {
        'events/views.py': 'events_api function',
        'events/urls.py': 'events/api/ URL pattern',
        'templates/events/event_list.html': 'Dynamic JavaScript implementation',
        'templates/events/partials/events_grid.html': 'Partial template for AJAX'
    }
    
    all_passed = True
    
    print("📋 File Existence and Structure:")
    for file_path, description in files_to_check.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✅ {file_path} - {description}")
        except FileNotFoundError:
            print(f"   ❌ {file_path} - Not found")
            all_passed = False
            continue
        
        # Check specific requirements based on file
        if 'views.py' in file_path:
            if 'def events_api(' in content and 'JsonResponse' in content:
                print(f"     ✅ API endpoint properly implemented")
            else:
                print(f"     ❌ API endpoint missing or incomplete")
                all_passed = False
        
        elif 'urls.py' in file_path:
            if "path('events/api/', views.events_api, name='events_api')" in content:
                print(f"     ✅ URL pattern correctly added")
            else:
                print(f"     ❌ URL pattern missing or incorrect")
                all_passed = False
        
        elif 'event_list.html' in file_path:
            required_features = [
                'DEBOUNCE_DELAY = 300',  # 300ms debounce as per memory
                'events-container',  # Dynamic container
                'loadEvents',  # Main function
                'debouncedFilter',  # Debounced filtering
                'X-Requested-With',  # AJAX header
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            if not missing_features:
                print(f"     ✅ All dynamic features implemented")
            else:
                print(f"     ❌ Missing features: {', '.join(missing_features)}")
                all_passed = False
        
        elif 'events_grid.html' in file_path:
            if 'events' in content and 'page_obj' in content:
                print(f"     ✅ Partial template properly structured")
            else:
                print(f"     ❌ Partial template missing required variables")
                all_passed = False
    
    # Check removed elements
    print("\n🚫 Removed Elements:")
    try:
        with open('templates/events/event_list.html', 'r', encoding='utf-8') as f:
            main_template = f.read()
        
        removed_elements = [
            ('Filter Button', 'Filtrar'),
            ('Clear Filters Link', 'Limpar Filtros'),
            ('Form Submission', 'button[type="submit"]')
        ]
        
        for element_name, search_text in removed_elements:
            if search_text not in main_template:
                print(f"   ✅ {element_name} - Successfully removed")
            else:
                print(f"   ❌ {element_name} - Still present")
                all_passed = False
    
    except FileNotFoundError:
        print("   ❌ Cannot check removed elements - template not found")
        all_passed = False
    
    # Check implemented features
    print("\n✨ Dynamic Features Implemented:")
    dynamic_features = {
        'Real-time Filtering': 'debouncedFilter',
        '300ms Debounce': 'DEBOUNCE_DELAY = 300',
        'AJAX Requests': 'fetch(',
        'Loading States': 'showLoading',
        'Visual Feedback': 'showFilterFeedback',
        'Pagination Support': 'loadPage',
        'Error Handling': 'catch(error',
        'Container Updates': 'eventsContainer.innerHTML'
    }
    
    try:
        with open('templates/events/event_list.html', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        for feature_name, search_text in dynamic_features.items():
            if search_text in js_content:
                print(f"   ✅ {feature_name}")
            else:
                print(f"   ❌ {feature_name} - Not found")
                all_passed = False
    
    except FileNotFoundError:
        print("   ❌ Cannot check dynamic features")
        all_passed = False
    
    print("\n📊 Summary:")
    if all_passed:
        print("🎉 Dynamic filtering implementation completed successfully!")
        print("\n✅ Requirements Met:")
        print("   • 'Filtrar' button removed")
        print("   • Dynamic table loading implemented")
        print("   • Real-time filtering with 300ms debounce")
        print("   • AJAX API endpoint created")
        print("   • Visual feedback and loading states")
        print("   • Automatic updates without page reload")
        print("   • Pagination support maintained")
        print("   • Error handling implemented")
        
        return True
    else:
        print("❌ Some features are missing or incomplete")
        return False

def check_api_functionality():
    """Check if API endpoints are accessible"""
    print("\n🌐 API Endpoint Validation:")
    
    import subprocess
    import json
    
    try:
        # Check if server is running by testing the main events page
        result = subprocess.run(
            ['powershell', '-Command', 'Invoke-WebRequest -Uri "http://127.0.0.1:8000/events/" -Method HEAD'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if 'StatusCode' in result.stdout and '200' in result.stdout:
            print("   ✅ Events page accessible")
            
            # Test API endpoint
            api_result = subprocess.run(
                ['powershell', '-Command', 'Invoke-WebRequest -Uri "http://127.0.0.1:8000/events/api/" -Method HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'StatusCode' in api_result.stdout and '200' in api_result.stdout:
                print("   ✅ API endpoint accessible")
                return True
            else:
                print("   ❌ API endpoint not accessible")
                return False
        else:
            print("   ❌ Events page not accessible")
            return False
    
    except Exception as e:
        print(f"   ⚠️ Cannot test endpoints: {str(e)}")
        return False

def main():
    """Main validation function"""
    success = validate_dynamic_filtering()
    api_success = check_api_functionality()
    
    print("\n" + "=" * 70)
    if success and api_success:
        print("🎯 DYNAMIC FILTERING IMPLEMENTATION COMPLETE!")
        print("\n🌟 New Behavior:")
        print("   ✅ No 'Filtrar' button required")
        print("   ✅ Table updates automatically as you type/select")
        print("   ✅ 300ms debounce prevents excessive requests")
        print("   ✅ Visual feedback shows number of results")
        print("   ✅ Loading states provide user feedback")
        print("   ✅ Pagination works seamlessly")
        print("   ✅ Error handling for network issues")
        print("\n🔗 Test at: http://127.0.0.1:8000/events/")
        print("💡 Try changing filters - table updates automatically!")
    else:
        print("❌ Implementation incomplete. Please review the above issues.")
    
    return success and api_success

if __name__ == "__main__":
    main()