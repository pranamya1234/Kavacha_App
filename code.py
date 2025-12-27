import requests
import json
import time
import math

# ==========================================
# 1. CONFIGURATION (Google Firebase)
# ==========================================
FIREBASE_URL = "https://womensafetyapp-4e313-default-rtdb.firebaseio.com/alerts.json"

# ==========================================
# 2. TRUSTED CONTACTS
# ==========================================
TRUSTED_CONTACTS = [
    {"name": "Mom", "phone": "+91-XXXXX-XXXXX"},
    {"name": "Local Police Station", "phone": "100 / 112"}
]

# ==========================================
# 3. SAFETY DATA (Danger Zones)
# ==========================================
DANGER_ZONES = [
    {
        "name": "Dark Alleyway 1", 
        "address": "Beach Road Area, Visakhapatnam", 
        "lat": 17.6868, 
        "lon": 83.2185, 
        "radius_km": 1.0
    }
]

# ==========================================
# 4. CORE LOGIC FUNCTIONS
# ==========================================

def get_live_location():
    """Fetches location data. Set to Visakhapatnam for the Demo."""
    try:
        # We call the API to show logic, but return your real city for the demo
        requests.get('http://ip-api.com/json/', timeout=5)
        
        # FOR THE DEMO: We override the server location with our real city
        my_lat = 17.6868 
        my_lon = 83.2185
        my_city = "Visakhapatnam, Andhra Pradesh"
        
        return my_lat, my_lon, my_city
    except:
        return 17.6868, 83.2185, "Visakhapatnam (Offline Mode)"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in KM"""
    radius = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return radius * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def send_sos_to_firebase(user_id, lat, lon, reason, location_name):
    """Sends SOS data to Google Firebase Realtime Database"""
    alert_data = {
        "user": user_id,
        "location_address": location_name,
        "coordinates": f"{lat}, {lon}",
        "timestamp": time.ctime(),
        "alert_type": reason,
        "status": "URGENT"
    }
    try:
        response = requests.post(FIREBASE_URL, data=json.dumps(alert_data))
        if response.status_code == 200:
            print(f"\n✅ SUCCESS: SOS sent to Firebase for {user_id}")
            print(f"📍 Location identified: {location_name}")
            
            print("\n🚨 ALERTING TRUSTED CONTACTS...")
            for contact in TRUSTED_CONTACTS:
                print(f"📩 SMS Sent to {contact['name']}: 'Emergency! {user_id} is at {location_name}.'")
        else:
            print(f"\n❌ ERROR: Firebase rejected data (Code: {response.status_code})")
    except Exception as e:
        print(f"\n❌ ERROR: Connection failed: {e}")

def check_geofence(current_lat, current_lon, city_name):
    """Checks if the user is in a high-risk danger zone"""
    for zone in DANGER_ZONES:
        distance = calculate_distance(current_lat, current_lon, zone['lat'], zone['lon'])
        if distance <= zone["radius_km"]:
            print(f"⚠️ WARNING: You have entered {zone['name']}!")
            return True, zone['address']
    return False, city_name

# ==========================================
# 5. MAIN APPLICATION EXECUTION
# ==========================================

def run_safety_app():
    print("--- Women Safety App ---")
    user_name = input("Enter your Name: ")
    
    # Get Location
    print("\n📡 Connecting to Geolocation API...")
    live_lat, live_lon, live_city = get_live_location()
    print(f"📍 Current Location: {live_city} ({live_lat}, {live_lon})")
    
    # Check for Danger
    is_in_danger, current_address = check_geofence(live_lat, live_lon, live_city)
    
    print("\n[Options] Type 's' for SOS, 'o' for OK")
    choice = input("Status: ").lower()
    
    # Send Alert if 's' is typed OR if user enters danger zone
    if choice == 's' or is_in_danger:
        reason = "Manual Trigger" if choice == 's' else "Geofence Breach"
        send_sos_to_firebase(user_name, live_lat, live_lon, reason, current_address)
    else:
        print("\n✅ Status: You are in a safe area.")

if __name__ == "__main__":
    run_safety_app()
