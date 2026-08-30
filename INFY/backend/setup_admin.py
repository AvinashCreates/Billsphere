import requests
from app.core.database import SessionLocal
from app.models.user import User

# Register admin user
register_url = 'http://127.0.0.1:8000/api/v1/register'
admin_payload = {
    'first_name': 'Admin',
    'last_name': 'User',
    'email': 'admin@billsphere.com',
    'password': 'Admin@123456',
    'role': 'admin'
}

print("=" * 60)
print("ADMIN USER SETUP")
print("=" * 60)

try:
    response = requests.post(register_url, json=admin_payload)
    print(f'\nAdmin Register Status: {response.status_code}')
    
    if response.status_code in [201, 200]:
        print('✅ Admin user created successfully!')
        admin_data = response.json()
        print(f'   ID: {admin_data.get("id")}')
        print(f'   Email: {admin_data.get("email")}')
        
        # Now try to login as admin
        login_url = 'http://127.0.0.1:8000/api/v1/login'
        login_payload = {
            'email': 'admin@billsphere.com',
            'password': 'Admin@123456'
        }
        login_response = requests.post(login_url, json=login_payload)
        print(f'\nAdmin Login Status: {login_response.status_code}')
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f'✅ Admin logged in successfully')
            print(f'   Role: {login_data.get("role")}')
            print(f'   Token: {login_data.get("access_token")[:50]}...')
        else:
            print(f'❌ Admin login failed: {login_response.text}')
    elif response.status_code == 400 and 'already registered' in response.text:
        print('⚠️  Admin user already exists; promoting existing account')
        db = SessionLocal()
        try:
            existing_admin = db.query(User).filter(User.email == admin_payload['email']).first()
            if not existing_admin:
                raise RuntimeError('Existing admin email was not found in the database')
            existing_admin.role = 'admin'
            existing_admin.is_active = True
            db.commit()
            db.refresh(existing_admin)
            print(f'   ✅ Account {existing_admin.email} now has role: {existing_admin.role}')
        finally:
            db.close()

        print('   Attempting login...')
        
        login_url = 'http://127.0.0.1:8000/api/v1/login'
        login_payload = {
            'email': 'admin@billsphere.com',
            'password': 'Admin@123456'
        }
        login_response = requests.post(login_url, json=login_payload)
        print(f'\n   Login Status: {login_response.status_code}')
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f'   ✅ Admin logged in successfully')
            print(f'   Role: {login_data.get("role")}')
        else:
            print(f'   ❌ Login failed: {login_response.text}')
    elif response.status_code == 409:
        print(f'❌ Error: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')

print("\n" + "=" * 60)
print("CREDENTIALS")
print("=" * 60)
print("Email: admin@billsphere.com")
print("Password: Admin@123456")
print("=" * 60)
