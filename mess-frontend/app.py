import streamlit as st
import requests
import datetime
import json
from datetime import datetime, timedelta

# API endpoint
API_URL = "http://localhost:8000"  # Backend API URL
# In Docker environment, this would be changed to container name
# API_URL = "http://backend:8000"

# Page configuration
st.set_page_config(
    page_title="Hostel Mess Management System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# Helper functions for API calls
def get_api_data(endpoint):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data from API: Status code {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching data from API: {str(e)}")
        return None

def post_api_data(endpoint, data):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"Error posting data to API: Status code {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error posting data to API: {str(e)}")
        return None

# Login function
def login_user():
    st.title("🍽️ Hostel Mess Management System")
    st.subheader("Login")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username and password:
                # OAuth2 form data needs special handling
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.username = username
                    st.session_state.role = data["role"]
                    st.session_state.page = "dashboard" if data["role"] == "admin" else "menu"
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    with col2:
        st.markdown("""
        ### Demo Accounts
        
        **Admin User:**
        - Username: admin
        - Password: adminpassword
        
        **Student User:**
        - Username: student
        - Password: studentpassword
        """)
        
        st.info("This is a demonstration system for the Hostel Mess Management System.")

# Sidebar navigation
def render_sidebar():
    st.sidebar.title("Navigation")
    
    # Profile info
    if st.session_state.username:
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
        st.sidebar.markdown(f"**Role:** {st.session_state.role}")
    
    # Navigation based on role
    if st.session_state.role == "admin":
        selected_page = st.sidebar.radio(
            "Go to:",
            ["Dashboard", "Menu Management", "Student Records", "Inventory", "Reports", "Logout"]
        )
        
        if selected_page == "Dashboard":
            st.session_state.page = "dashboard"
        elif selected_page == "Menu Management":
            st.session_state.page = "menu_management"
        elif selected_page == "Student Records":
            st.session_state.page = "student_records"
        elif selected_page == "Inventory":
            st.session_state.page = "inventory"
        elif selected_page == "Reports":
            st.session_state.page = "reports"
        elif selected_page == "Logout":
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()
    else:
        selected_page = st.sidebar.radio(
            "Go to:",
            ["Weekly Menu", "Meal Booking", "My Attendance", "Feedback", "Logout"]
        )
        
        if selected_page == "Weekly Menu":
            st.session_state.page = "menu"
        elif selected_page == "Meal Booking":
            st.session_state.page = "booking"
        elif selected_page == "My Attendance":
            st.session_state.page = "attendance"
        elif selected_page == "Feedback":
            st.session_state.page = "feedback"
        elif selected_page == "Logout":
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Hostel Mess Management System")
    st.sidebar.caption("DevOps Implementation Project")

# Page functions
def show_menu():
    st.title("🍽️ Weekly Menu")
    
    menu_data = get_api_data("/menu")
    
    if menu_data:
        col1, col2, col3 = st.columns(3)
        
        # Display days in three columns
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day = datetime.now().strftime("%A")
        
        for i, day in enumerate(days):
            if i % 3 == 0:
                column = col1
            elif i % 3 == 1:
                column = col2
            else:
                column = col3
            
            with column:
                day_menu = next((item for item in menu_data if item["day"] == day), None)
                if day_menu:
                    if day == current_day:
                        st.markdown(f"### 📅 {day} (Today)")
                    else:
                        st.markdown(f"### 📅 {day}")
                    
                    st.markdown("#### 🌅 Breakfast")
                    st.markdown(day_menu["breakfast"])
                    
                    st.markdown("#### 🌞 Lunch")
                    st.markdown(day_menu["lunch"])
                    
                    st.markdown("#### 🌙 Dinner")
                    st.markdown(day_menu["dinner"])
                    
                    st.markdown("---")

def show_meal_booking():
    st.title("🍲 Meal Booking")
    
    # Get menu data
    menu_data = get_api_data("/menu")
    
    if not menu_data:
        st.error("Could not fetch menu data. Please try again later.")
        return
    
    # Date selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        today = datetime.now().date()
        selected_date = st.date_input(
            "Select Date",
            min_value=today,
            max_value=today + timedelta(days=7),
            value=today
        )
        
        # Format date for API
        date_str = selected_date.strftime("%Y-%m-%d")
        
        # Get existing booking for this date
        existing_bookings = get_api_data(f"/bookings/{st.session_state.username}")
        existing_booking = next((b for b in existing_bookings if b["date"] == date_str), None) if existing_bookings else None
        
        # Day of week
        day_of_week = selected_date.strftime("%A")
        day_menu = next((item for item in menu_data if item["day"] == day_of_week), None)
        
        if not day_menu:
            st.warning(f"No menu found for {day_of_week}")
            return
        
        st.subheader(f"Booking for {day_of_week}, {date_str}")
        
        # Meal selection sections with item quantities
        with st.expander("Breakfast", expanded=True):
            breakfast = st.checkbox(
                "Select Breakfast",
                value=existing_booking["breakfast"] if existing_booking else False
            )
            
            # Parse menu items
            breakfast_items = [item.strip() for item in day_menu['breakfast'].split(',')]
            
            breakfast_quantities = []
            if breakfast:
                st.markdown("**Select quantities for each breakfast item:**")
                for item in breakfast_items:
                    # Check if item exists in existing booking
                    default_qty = 0
                    if existing_booking and "breakfast_items" in existing_booking:
                        for existing_item in existing_booking.get("breakfast_items", []):
                            if existing_item.get("item") == item:
                                default_qty = existing_item.get("quantity", 0)
                    
                    qty = st.number_input(f"{item}", min_value=0, value=default_qty)
                    if qty > 0:
                        breakfast_quantities.append({"item": item, "quantity": qty})
        
        with st.expander("Lunch", expanded=True):
            lunch = st.checkbox(
                "Select Lunch",
                value=existing_booking["lunch"] if existing_booking else False
            )
            
            # Parse menu items
            lunch_items = [item.strip() for item in day_menu['lunch'].split(',')]
            
            lunch_quantities = []
            if lunch:
                st.markdown("**Select quantities for each lunch item:**")
                for item in lunch_items:
                    # Check if item exists in existing booking
                    default_qty = 0
                    if existing_booking and "lunch_items" in existing_booking:
                        for existing_item in existing_booking.get("lunch_items", []):
                            if existing_item.get("item") == item:
                                default_qty = existing_item.get("quantity", 0)
                    
                    qty = st.number_input(f"{item}", min_value=0, value=default_qty)
                    if qty > 0:
                        lunch_quantities.append({"item": item, "quantity": qty})
        
        with st.expander("Dinner", expanded=True):
            dinner = st.checkbox(
                "Select Dinner",
                value=existing_booking["dinner"] if existing_booking else False
            )
            
            # Parse menu items
            dinner_items = [item.strip() for item in day_menu['dinner'].split(',')]
            
            dinner_quantities = []
            if dinner:
                st.markdown("**Select quantities for each dinner item:**")
                for item in dinner_items:
                    # Check if item exists in existing booking
                    default_qty = 0
                    if existing_booking and "dinner_items" in existing_booking:
                        for existing_item in existing_booking.get("dinner_items", []):
                            if existing_item.get("item") == item:
                                default_qty = existing_item.get("quantity", 0)
                    
                    qty = st.number_input(f"{item}", min_value=0, value=default_qty)
                    if qty > 0:
                        dinner_quantities.append({"item": item, "quantity": qty})
        
        # Save booking
        if st.button("Save Booking"):
            booking_data = {
                "user": st.session_state.username,
                "date": date_str,
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "breakfast_items": breakfast_quantities,
                "lunch_items": lunch_quantities,
                "dinner_items": dinner_quantities
            }
            
            response = post_api_data("/bookings/save", booking_data)
            
            if response and "message" in response:
                st.success(response["message"])
            else:
                st.error("Failed to save booking. Please try again.")
    
    with col2:
        if day_menu:
            st.subheader(f"Menu for {day_of_week}")
            
            st.markdown(f"**Breakfast:** {day_menu['breakfast']}")
            st.markdown(f"**Lunch:** {day_menu['lunch']}")
            st.markdown(f"**Dinner:** {day_menu['dinner']}")
        
        # Show all bookings
        st.subheader("Your Bookings")
        if existing_bookings:
            bookings_df = []
            for booking in existing_bookings:
                day = datetime.strptime(booking["date"], "%Y-%m-%d").strftime("%A")
                meals = []
                if booking["breakfast"]:
                    meals.append("Breakfast")
                if booking["lunch"]:
                    meals.append("Lunch")
                if booking["dinner"]:
                    meals.append("Dinner")
                
                bookings_df.append({
                    "Date": booking["date"],
                    "Day": day,
                    "Meals": ", ".join(meals) if meals else "None"
                })
            
            st.dataframe(bookings_df)
            
            # Show selected booking details
            if existing_booking:
                st.subheader(f"Details for {date_str}")
                
                # Display breakfast items
                if existing_booking.get("breakfast") and "breakfast_items" in existing_booking and existing_booking["breakfast_items"]:
                    st.markdown("**Breakfast Items:**")
                    for item in existing_booking["breakfast_items"]:
                        st.markdown(f"- {item['item']}: {item['quantity']}")
                
                # Display lunch items
                if existing_booking.get("lunch") and "lunch_items" in existing_booking and existing_booking["lunch_items"]:
                    st.markdown("**Lunch Items:**")
                    for item in existing_booking["lunch_items"]:
                        st.markdown(f"- {item['item']}: {item['quantity']}")
                
                # Display dinner items
                if existing_booking.get("dinner") and "dinner_items" in existing_booking and existing_booking["dinner_items"]:
                    st.markdown("**Dinner Items:**")
                    for item in existing_booking["dinner_items"]:
                        st.markdown(f"- {item['item']}: {item['quantity']}")
        else:
            st.info("You have no bookings yet.")

def show_feedback():
    st.title("📝 Meal Feedback")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Date selection
        today = datetime.now().date()
        selected_date = st.date_input(
            "Select Date",
            max_value=today,
            value=today
        )
        
        # Format date for API
        date_str = selected_date.strftime("%Y-%m-%d")
        
        # Meal selection
        meal = st.selectbox(
            "Select Meal",
            ["breakfast", "lunch", "dinner"]
        )
        
        # Ratings
        st.subheader("Rate the meal")
        
        taste = st.slider("Taste", 1, 5, 3)
        quantity = st.slider("Quantity", 1, 5, 3)
        hygiene = st.slider("Hygiene", 1, 5, 3)
        service = st.slider("Service", 1, 5, 3)
        
        # Comments
        comments = st.text_area("Additional Comments", height=100)
        
        # Submit button
        if st.button("Submit Feedback"):
            feedback_data = {
                "user": st.session_state.username,
                "date": date_str,
                "meal": meal,
                "ratings": {
                    "taste": taste,
                    "quantity": quantity,
                    "hygiene": hygiene,
                    "service": service
                },
                "comments": comments
            }
            
            response = post_api_data("/feedback/submit", feedback_data)
            
            if response and "message" in response:
                st.success(response["message"])
            else:
                st.error("Failed to submit feedback. Please try again.")
    
    with col2:
        # Show previous feedback
        st.subheader("Your Previous Feedback")
        
        user_feedback = get_api_data(f"/feedback/{st.session_state.username}")
        
        if user_feedback:
            for feedback in user_feedback:
                with st.expander(f"{feedback['date']} - {feedback['meal'].capitalize()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Ratings:**")
                        for category, rating in feedback["ratings"].items():
                            st.markdown(f"- {category.capitalize()}: {'⭐' * rating}")
                    
                    with col2:
                        if feedback.get("comments"):
                            st.markdown("**Comments:**")
                            st.markdown(feedback["comments"])
        else:
            st.info("You haven't submitted any feedback yet.")

def show_attendance():
    st.title("📊 My Attendance")
    
    attendance_data = get_api_data(f"/attendance/{st.session_state.username}")
    
    if attendance_data:
        # Summary statistics
        total_meals_attended = sum(a["meals_attended"] for a in attendance_data)
        total_meals_possible = sum(a["total_meals"] for a in attendance_data)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            attendance_percentage = (total_meals_attended / total_meals_possible * 100) if total_meals_possible > 0 else 0
            st.metric("Overall Attendance", f"{attendance_percentage:.1f}%")
        
        with col2:
            st.metric("Meals Attended", total_meals_attended)
        
        with col3:
            st.metric("Total Meals", total_meals_possible)
        
        # Attendance details
        st.subheader("Attendance Details")
        
        attendance_df = []
        for record in attendance_data:
            day = datetime.strptime(record["date"], "%Y-%m-%d").strftime("%A")
            attendance_df.append({
                "Date": record["date"],
                "Day": day,
                "Meals Attended": record["meals_attended"],
                "Breakfast": "✅" if record["details"]["breakfast"] else "❌",
                "Lunch": "✅" if record["details"]["lunch"] else "❌",
                "Dinner": "✅" if record["details"]["dinner"] else "❌",
                "Percentage": f"{(record['meals_attended'] / record['total_meals'] * 100):.1f}%"
            })
        
        st.dataframe(attendance_df)
    else:
        st.info("No attendance records found. Book meals to track your attendance.")

def show_dashboard():
    st.title("📊 Admin Dashboard")
    
    # Get dashboard data with separate error handling for each component
    summary_data = get_api_data("/dashboard/summary")
    if not summary_data:
        st.error("Could not fetch summary data. Please try again later.")
        summary_data = {
            "student_count": 0,
            "booking_count": 0,
            "feedback_count": 0,
            "inventory_summary": {"total_items": 0},
            "today_meals": {"breakfast": 0, "lunch": 0, "dinner": 0}
        }
    
    attendance_data = get_api_data("/dashboard/attendance")
    if not attendance_data:
        st.warning("Could not fetch attendance data. Attendance charts will not be displayed.")
        attendance_data = []
    
    feedback_data = get_api_data("/dashboard/feedback")
    if not feedback_data:
        st.warning("Could not fetch feedback data. Feedback summaries will not be displayed.")
        feedback_data = {"average_ratings": {}, "recent_comments": []}
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Students", summary_data["student_count"])
    
    with col2:
        st.metric("Total Bookings", summary_data["booking_count"])
    
    with col3:
        st.metric("Feedback Received", summary_data["feedback_count"])
    
    # Today's meals
    st.subheader("Today's Meals")
    
    today_meals = summary_data["today_meals"]
    meal_col1, meal_col2, meal_col3 = st.columns(3)
    
    with meal_col1:
        st.metric("Breakfast", today_meals["breakfast"])
    
    with meal_col2:
        st.metric("Lunch", today_meals["lunch"])
    
    with meal_col3:
        st.metric("Dinner", today_meals["dinner"])
    
    # Display meal item quantities if available
    if "meal_items" in summary_data:
        st.subheader("Today's Meal Item Quantities")
        meal_items = summary_data["meal_items"]
        
        # Display breakfast items
        if meal_items["breakfast"]:
            with st.expander("Breakfast Items"):
                items_df = []
                for item, quantity in meal_items["breakfast"].items():
                    items_df.append({"Item": item, "Quantity": quantity})
                if items_df:
                    st.dataframe(items_df)
                else:
                    st.info("No breakfast items ordered today")
        
        # Display lunch items
        if meal_items["lunch"]:
            with st.expander("Lunch Items"):
                items_df = []
                for item, quantity in meal_items["lunch"].items():
                    items_df.append({"Item": item, "Quantity": quantity})
                if items_df:
                    st.dataframe(items_df)
                else:
                    st.info("No lunch items ordered today")
        
        # Display dinner items
        if meal_items["dinner"]:
            with st.expander("Dinner Items"):
                items_df = []
                for item, quantity in meal_items["dinner"].items():
                    items_df.append({"Item": item, "Quantity": quantity})
                if items_df:
                    st.dataframe(items_df)
                else:
                    st.info("No dinner items ordered today")
    else:
        st.info("Detailed meal item quantities not available")
    
    # Attendance trend
    st.subheader("Attendance Trend")
    
    if attendance_data:
        # Sort by date
        attendance_data.sort(key=lambda x: x["date"])
        
        # Prepare data for chart
        dates = [record["date"] for record in attendance_data]
        breakfast_counts = [record["breakfast"] for record in attendance_data]
        lunch_counts = [record["lunch"] for record in attendance_data]
        dinner_counts = [record["dinner"] for record in attendance_data]
        
        # Display as a bar chart
        attendance_chart_data = {
            "Date": dates,
            "Breakfast": breakfast_counts,
            "Lunch": lunch_counts,
            "Dinner": dinner_counts
        }
        
        st.bar_chart(attendance_chart_data)
    else:
        st.info("No attendance data available")
    
    # Feedback summary
    st.subheader("Feedback Summary")
    
    feedback_col1, feedback_col2 = st.columns([2, 1])
    
    with feedback_col1:
        # Average ratings
        avg_ratings = feedback_data["average_ratings"]
        
        if avg_ratings:
            # Prepare data for radar chart or display as table
            categories = ["taste", "quantity", "hygiene", "service"]
            
            # Display as table for now
            ratings_data = []
            for meal, ratings in avg_ratings.items():
                row = {"Meal": meal.capitalize()}
                for category in categories:
                    row[category.capitalize()] = f"{ratings[category]:.1f}/5"
                ratings_data.append(row)
            
            st.dataframe(ratings_data)
    
    with feedback_col2:
        # Recent comments
        st.markdown("**Recent Comments**")
        
        recent_comments = feedback_data["recent_comments"]
        
        if recent_comments:
            for comment in recent_comments:
                with st.expander(f"{comment['date']} - {comment['meal'].capitalize()}"):
                    st.markdown(f"**User:** {comment['user']}")
                    st.markdown(comment['comment'])
        else:
            st.info("No comments available")

def show_menu_management():
    st.title("🍽️ Menu Management")
    
    # Get current menu
    menu_data = get_api_data("/menu")
    
    if not menu_data:
        st.error("Could not fetch menu data. Please try again later.")
        return
    
    # Day selection
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day = st.selectbox("Select Day", days)
    
    # Get current menu for selected day
    day_menu = next((item for item in menu_data if item["day"] == selected_day), None)
    
    # Form for editing menu
    with st.form("menu_form"):
        st.subheader(f"Edit Menu for {selected_day}")
        
        breakfast = st.text_area(
            "Breakfast",
            value=day_menu["breakfast"] if day_menu else "",
            height=100
        )
        
        lunch = st.text_area(
            "Lunch",
            value=day_menu["lunch"] if day_menu else "",
            height=100
        )
        
        dinner = st.text_area(
            "Dinner",
            value=day_menu["dinner"] if day_menu else "",
            height=100
        )
        
        submit_button = st.form_submit_button("Update Menu")
        
        if submit_button:
            menu_update = {
                "day": selected_day,
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
            
            response = post_api_data("/menu/update", menu_update)
            
            if response and "message" in response:
                st.success(response["message"])
            else:
                st.error("Failed to update menu. Please try again.")
    
    # Display current menu
    st.subheader("Current Weekly Menu")
    
    # Use columns to display the menu by day
    cols = st.columns(7)
    
    for i, day in enumerate(days):
        day_menu = next((item for item in menu_data if item["day"] == day), None)
        
        if day_menu:
            with cols[i]:
                st.markdown(f"**{day}**")
                st.markdown(f"*Breakfast:* {day_menu['breakfast'][:50]}...")
                st.markdown(f"*Lunch:* {day_menu['lunch'][:50]}...")
                st.markdown(f"*Dinner:* {day_menu['dinner'][:50]}...")

def show_inventory():
    st.title("📦 Inventory Management")
    
    # Get inventory data
    inventory_data = get_api_data("/inventory")
    
    if not inventory_data:
        st.error("Could not fetch inventory data. Please try again later.")
        return
    
    # Add new item section
    st.subheader("Add/Update Inventory Item")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("inventory_form"):
            name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
            unit = st.selectbox("Unit", ["kg", "gram", "liter", "piece", "packet"])
            category = st.selectbox("Category", ["Grains", "Dairy", "Vegetables", "Fruits", "Meat", "Oils", "Spices", "Other"])
            
            submit_button = st.form_submit_button("Save Item")
            
            if submit_button:
                if not name:
                    st.error("Item name is required")
                else:
                    inventory_item = {
                        "name": name,
                        "quantity": quantity,
                        "unit": unit,
                        "category": category
                    }
                    
                    response = post_api_data("/inventory/update", inventory_item)
                    
                    if response and "message" in response:
                        st.success(response["message"])
                    else:
                        st.error("Failed to update inventory. Please try again.")
    
    with col2:
        # Quick update for existing items
        if inventory_data:
            st.subheader("Quick Update")
            
            # Select item
            item_names = [item["name"] for item in inventory_data]
            selected_item = st.selectbox("Select Item", item_names)
            
            # Get selected item details
            item = next((i for i in inventory_data if i["name"] == selected_item), None)
            
            if item:
                # Show current quantity
                current_quantity = st.number_input(
                    f"Current Quantity ({item['unit']})",
                    value=item["quantity"],
                    step=0.1
                )
                
                # Add or remove quantity
                adjust_quantity = st.number_input(
                    "Adjust Quantity (+ or -)",
                    step=0.1
                )
                
                if st.button("Update Quantity"):
                    new_quantity = current_quantity + adjust_quantity
                    
                    if new_quantity < 0:
                        st.error("Quantity cannot be negative")
                    else:
                        inventory_item = {
                            "name": item["name"],
                            "quantity": new_quantity,
                            "unit": item["unit"],
                            "category": item["category"]
                        }
                        
                        response = post_api_data("/inventory/update", inventory_item)
                        
                        if response and "message" in response:
                            st.success(response["message"])
                        else:
                            st.error("Failed to update inventory. Please try again.")
    
    # Display inventory
    st.subheader("Current Inventory")
    
    # Group by category
    categories = {}
    for item in inventory_data:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # Display by category
    for category, items in categories.items():
        with st.expander(f"{category} ({len(items)} items)"):
            # Create a dataframe for display
            items_df = []
            for item in items:
                items_df.append({
                    "Name": item["name"],
                    "Quantity": f"{item['quantity']} {item['unit']}",
                    "Category": item["category"]
                })
            
            st.dataframe(items_df)

def show_student_records():
    st.title("👨‍🎓 Student Records")
    
    # Get student data
    students_data = get_api_data("/students")
    
    if not students_data:
        st.error("Could not fetch student data. Please try again later.")
        return
    
    # Add/edit student section
    st.subheader("Add/Edit Student")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("student_form"):
            # New student flag
            is_new = st.checkbox("Add New Student")
            
            # If editing, select student
            if not is_new and students_data:
                student_usernames = [s["username"] for s in students_data]
                username = st.selectbox("Select Student", student_usernames)
                selected_student = next((s for s in students_data if s["username"] == username), None)
            else:
                username = st.text_input("Username")
                selected_student = None
            
            # Form fields
            name = st.text_input("Name", value=selected_student["name"] if selected_student else "")
            email = st.text_input("Email", value=selected_student["email"] if selected_student else "")
            phone = st.text_input("Phone", value=selected_student["phone"] if selected_student else "")
            room_number = st.text_input("Room Number", value=selected_student["room_number"] if selected_student else "")
            
            # Password field for new students
            if is_new:
                password = st.text_input("Password", type="password")
            else:
                password = st.text_input("New Password (leave blank to keep current)", type="password")
            
            submit_button = st.form_submit_button("Save Student")
            
            if submit_button:
                if is_new and not username:
                    st.error("Username is required for new students")
                elif is_new and not password:
                    st.error("Password is required for new students")
                else:
                    student_data = {
                        "username": username,
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "room_number": room_number,
                    }
                    
                    if password:
                        student_data["password"] = password
                    
                    response = post_api_data("/students/update", student_data)
                    
                    if response and "message" in response:
                        st.success(response["message"])
                    else:
                        st.error("Failed to update student. Please try again.")
    
    with col2:
        # Quick view of student details
        if students_data and not is_new:
            if selected_student:
                st.subheader("Student Details")
                
                st.markdown(f"**Username:** {selected_student['username']}")
                st.markdown(f"**Name:** {selected_student['name']}")
                st.markdown(f"**Email:** {selected_student['email']}")
                st.markdown(f"**Phone:** {selected_student['phone']}")
                st.markdown(f"**Room:** {selected_student['room_number']}")
    
    # Display all students
    st.subheader("All Students")
    
    if students_data:
        # Create a dataframe for display
        students_df = []
        for student in students_data:
            students_df.append({
                "Username": student["username"],
                "Name": student["name"],
                "Email": student["email"],
                "Phone": student["phone"],
                "Room": student["room_number"]
            })
        
        st.dataframe(students_df)
    else:
        st.info("No students found")

def show_reports():
    st.title("📈 Reports")
    
    # Report types
    report_type = st.selectbox(
        "Select Report Type",
        ["Attendance Report", "Feedback Report", "Financial Report", "Inventory Usage Report"]
    )
    
    if report_type == "Attendance Report":
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        # Format dates for API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Generate report button
        if st.button("Generate Report"):
            report_data = get_api_data(f"/reports/attendance?start_date={start_date_str}&end_date={end_date_str}")
            
            if report_data:
                st.subheader(f"Attendance Report: {start_date_str} to {end_date_str}")
                
                # Summary statistics
                total_students = len(report_data["student_attendance"])
                total_meals = sum(data["total_meals"] for data in report_data["student_attendance"].values())
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Students", total_students)
                with col2:
                    st.metric("Total Meals Served", total_meals)
                
                # Student attendance table
                st.subheader("Student Attendance Details")
                
                attendance_df = []
                for username, data in report_data["student_attendance"].items():
                    attendance_df.append({
                        "Student": data.get("name", username),
                        "Total Meals": data["total_meals"],
                        "Breakfast": data["meals_attended"]["breakfast"],
                        "Lunch": data["meals_attended"]["lunch"],
                        "Dinner": data["meals_attended"]["dinner"]
                    })
                
                st.dataframe(attendance_df)
            else:
                st.error("Failed to generate report. Please try again.")
    
    elif report_type == "Feedback Report":
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        # Format dates for API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Generate report button
        if st.button("Generate Report"):
            report_data = get_api_data(f"/reports/feedback?start_date={start_date_str}&end_date={end_date_str}")
            
            if report_data:
                st.subheader(f"Feedback Report: {start_date_str} to {end_date_str}")
                
                # Average ratings
                st.subheader("Average Ratings by Meal")
                
                avg_ratings = report_data["average_ratings"]
                
                if avg_ratings:
                    # Display as table
                    ratings_df = []
                    for meal, ratings in avg_ratings.items():
                        ratings_df.append({
                            "Meal": meal.capitalize(),
                            "Taste": f"{ratings['taste']:.1f}/5",
                            "Quantity": f"{ratings['quantity']:.1f}/5",
                            "Hygiene": f"{ratings['hygiene']:.1f}/5",
                            "Service": f"{ratings['service']:.1f}/5",
                            "Overall": f"{(sum(ratings.values()) / len(ratings)):.1f}/5"
                        })
                    
                    st.dataframe(ratings_df)
                
                # Comments
                st.subheader("Feedback Comments")
                
                comments = report_data["comments"]
                
                if comments:
                    for comment in comments:
                        with st.expander(f"{comment['date']} - {comment['meal'].capitalize()} - {comment['user']}"):
                            st.markdown(comment["comment"])
                else:
                    st.info("No comments in the selected date range")
            else:
                st.error("Failed to generate report. Please try again.")
    
    elif report_type == "Financial Report":
        # Month and year selection
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Select Month",
                [(i, datetime(2023, i, 1).strftime("%B")) for i in range(1, 13)],
                format_func=lambda x: x[1]
            )
        with col2:
            year = st.selectbox(
                "Select Year",
                list(range(2020, datetime.now().year + 1))
            )
        
        # Generate report button
        if st.button("Generate Report"):
            report_data = get_api_data(f"/reports/financial?month={month[0]}&year={year}")
            
            if report_data:
                st.subheader(f"Financial Report: {month[1]} {year}")
                
                # Cost metrics
                total_costs = report_data["total_costs"]
                meal_counts = report_data["meal_counts"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Cost", f"₹{total_costs['total']:.2f}")
                with col2:
                    st.metric("Total Meals", sum(meal_counts.values()))
                with col3:
                    avg_cost_per_meal = total_costs["total"] / sum(meal_counts.values()) if sum(meal_counts.values()) > 0 else 0
                    st.metric("Avg. Cost Per Meal", f"₹{avg_cost_per_meal:.2f}")
                
                # Meal-wise costs
                st.subheader("Meal-wise Costs")
                
                meal_costs_df = []
                for meal in ["breakfast", "lunch", "dinner"]:
                    meal_costs_df.append({
                        "Meal": meal.capitalize(),
                        "Cost Per Meal": f"₹{report_data['meal_costs'][meal]:.2f}",
                        "Number of Meals": meal_counts[meal],
                        "Total Cost": f"₹{total_costs[meal]:.2f}"
                    })
                
                st.dataframe(meal_costs_df)
                
                # Student-wise costs
                st.subheader("Student-wise Costs")
                
                student_costs_df = []
                for username, data in report_data["student_costs"].items():
                    student_costs_df.append({
                        "Student": data.get("name", username),
                        "Breakfast Cost": f"₹{data['breakfast']:.2f}",
                        "Lunch Cost": f"₹{data['lunch']:.2f}",
                        "Dinner Cost": f"₹{data['dinner']:.2f}",
                        "Total Cost": f"₹{data['total']:.2f}"
                    })
                
                st.dataframe(student_costs_df)
            else:
                st.error("Failed to generate report. Please try again.")
    
    elif report_type == "Inventory Usage Report":
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        # Format dates for API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Generate report button
        if st.button("Generate Report"):
            report_data = get_api_data(f"/reports/inventory?start_date={start_date_str}&end_date={end_date_str}")
            
            if report_data:
                st.subheader(f"Inventory Usage Report: {start_date_str} to {end_date_str}")
                
                # Category usage
                st.subheader("Usage by Category")
                
                category_usage = report_data["category_usage"]
                
                category_df = []
                for category, data in category_usage.items():
                    category_df.append({
                        "Category": category,
                        "Used Quantity": f"{data['used_quantity']:.1f}",
                        "Items": ", ".join(data["items"])
                    })
                
                st.dataframe(category_df)
                
                # Item usage
                st.subheader("Item-wise Usage")
                
                inventory_usage = report_data["inventory_usage"]
                
                inventory_df = []
                for item in inventory_usage:
                    inventory_df.append({
                        "Item": item["name"],
                        "Category": item["category"],
                        "Initial Quantity": f"{item['initial_quantity']} {item['unit']}",
                        "Current Quantity": f"{item['current_quantity']} {item['unit']}",
                        "Used Quantity": f"{item['used_quantity']} {item['unit']}",
                        "Usage %": f"{(item['used_quantity'] / item['initial_quantity'] * 100):.1f}%"
                    })
                
                st.dataframe(inventory_df)
            else:
                st.error("Failed to generate report. Please try again.")

# Main function
def main():
    # Check if logged in
    if not st.session_state.token:
        login_user()
    else:
        # Render sidebar
        render_sidebar()
        
        # Render appropriate page
        if st.session_state.page == "menu":
            show_menu()
        elif st.session_state.page == "booking":
            show_meal_booking()
        elif st.session_state.page == "attendance":
            show_attendance()
        elif st.session_state.page == "feedback":
            show_feedback()
        elif st.session_state.page == "dashboard":
            show_dashboard()
        elif st.session_state.page == "menu_management":
            show_menu_management()
        elif st.session_state.page == "inventory":
            show_inventory()
        elif st.session_state.page == "student_records":
            show_student_records()
        elif st.session_state.page == "reports":
            show_reports()
        elif st.session_state.page == "login":
            login_user()

if __name__ == "__main__":
    main()