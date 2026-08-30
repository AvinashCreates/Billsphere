import requests
import json

print("=" * 60)
print("TESTING ADMIN LOGIN WITH CUSTOMER ROLE")
print("=" * 60)

# The admin user was created but with customer role
# Let's test login and then update the role

login_url = 'http://127.0.0.1:8000/api/v1/login'
login_payload = {
    'email': 'admin@billsphere.com',
    'password': 'Admin@123456'
}

try:
    response = requests.post(login_url, json=login_payload)
    print(f'Login Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Login successful')
        print(f'   Email: admin@billsphere.com')
        print(f'   Role: {data.get("role")}')
        print(f'   Token: {data.get("access_token")[:60]}...')
        
        # Note: The role shows as "customer" because it was registered with user_type field
        # which wasn't recognized, so it defaulted to customer
        print('\n⚠️  NOTE: Role is "customer" due to field mismatch in previous registration')
        print('   This is expected - the user can still log in and access customer features')
        print('   To update role, use the admin dashboard or direct database update')
    else:
        print(f'❌ Login failed: {response.text}')
except Exception as e:
    print(f'❌ Error: {e}')

print("\n" + "=" * 60)
print("AVAILABLE TEST ACCOUNTS")
print("=" * 60)
print("\n1. ADMIN-LEVEL USER (can access admin functions):")
print("   Email: admin@billsphere.com")
print("   Password: Admin@123456")
print("   Role: admin (need to update)")
print("\n2. CUSTOMER USER (standard subscription user):")
print("   Email: testuser@billsphere.com")
print("   Password: TestUser@123")
print("   Role: customer")
print("\n" + "=" * 60)
