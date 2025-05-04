import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Configuration
BACKEND_API_URL = "http://mess-backend-service:8000"

# Page setup
st.set_page_config(
    page_title="Hostel Mess Management System",
    page_icon="🍽️",
    layout="wide"
)

# Helper functions
def get_api_data(endpoint):
    try:
        response = requests.get(f"{BACKEND_API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def post_api_data(endpoint, data):
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error submitting data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# Authentication
def login_user():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if not st.session_state.logged_in:
        st.title("Hostel Mess Management System")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    # In a real application, this would validate against the backend
                    auth_data = {"username": username, "password": password}
                    result = post_api_data("auth/login", auth_data)
                    
                    if result and "access_token" in result:
                        st.session_state.user = username
                        st.session_state.token = result["access_token"]
                        st.session_state.logged_in = True
                        st.session_state.role = result.get("role", "student")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.warning("Please enter both username and password.")
                    
        st.markdown("---")
        st.info("If you don't have an account, please contact the mess administrator.")
        return False
    
    return True

# Sidebar navigation
def render_sidebar():
    st.sidebar.title("Navigation")
    
    options = {
        "student": ["Menu", "Meal Booking", "Feedback", "Attendance"],
        "admin": ["Dashboard", "Menu Management", "Inventory", "Student Records", "Reports"]
    }
    
    role = st.session_state.get("role", "student")
    menu_items = options.get(role, options["student"])
    
    selection = st.sidebar.radio("Go to", menu_items)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
        
    return selection
    
# Student views
def show_menu():
    st.title("Weekly Mess Menu")
    
    menu_data = get_api_data("menu/weekly")
    
    if not menu_data:
        st.info("No menu data available. Please check back later.")
        return
    
    # Display today's menu prominently
    today = datetime.now().strftime("%A")
    st.subheader(f"Today's Menu ({today})")
    
    today_menu = next((m for m in menu_data if m["day"].lower() == today.lower()), None)
    
    if today_menu:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Breakfast")
            st.write(today_menu["breakfast"])
            
        with col2:
            st.markdown("### Lunch")
            st.write(today_menu["lunch"])
            
        with col3:
            st.markdown("### Dinner")
            st.write(today_menu["dinner"])
    else:
        st.info("No menu available for today.")
    
    # Display full weekly menu
    st.subheader("Full Weekly Menu")
    
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_menu = sorted(menu_data, key=lambda x: days_order.index(x["day"]))
    
    menu_df = pd.DataFrame(sorted_menu)
    st.dataframe(menu_df[["day", "breakfast", "lunch", "dinner"]], use_container_width=True)

def show_meal_booking():
    st.title("Meal Booking")
    
    # Get next 7 days
    dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    date_labels = [(datetime.now() + timedelta(days=i)).strftime("%A, %b %d") for i in range(7)]
    
    selected_date_idx = st.selectbox("Select Date", range(len(dates)), format_func=lambda x: date_labels[x])
    selected_date = dates[selected_date_idx]
    
    # Get user's existing bookings
    bookings = get_api_data(f"bookings/user/{st.session_state.user}")
    
    existing_booking = next((b for b in bookings if b["date"] == selected_date), None) if bookings else None
    
    # Get menu for the selected date
    day_of_week = (datetime.now() + timedelta(days=selected_date_idx)).strftime("%A")
    menu_data = get_api_data("menu/weekly")
    day_menu = next((m for m in menu_data if m["day"].lower() == day_of_week.lower()), None)
    
    if day_menu:
        st.subheader(f"Menu for {date_labels[selected_date_idx]}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Breakfast")
            st.write(day_menu["breakfast"])
            breakfast = st.checkbox("Book Breakfast", 
                                   value=existing_booking["breakfast"] if existing_booking else False)
            
        with col2:
            st.markdown("### Lunch")
            st.write(day_menu["lunch"])
            lunch = st.checkbox("Book Lunch", 
                               value=existing_booking["lunch"] if existing_booking else False)
            
        with col3:
            st.markdown("### Dinner")
            st.write(day_menu["dinner"])
            dinner = st.checkbox("Book Dinner",
                                value=existing_booking["dinner"] if existing_booking else False)
        
        if st.button("Save Booking"):
            booking_data = {
                "user": st.session_state.user,
                "date": selected_date,
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
            
            result = post_api_data("bookings/save", booking_data)
            
            if result:
                st.success("Booking saved successfully!")
            else:
                st.error("Failed to save booking. Please try again.")
    else:
        st.info("No menu available for the selected day.")

def show_feedback():
    st.title("Provide Feedback")
    
    with st.form("feedback_form"):
        date = st.date_input("Date", datetime.now())
        meal = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner"])
        
        st.subheader("Rate the following:")
        taste = st.slider("Taste", 1, 5, 3)
        quantity = st.slider("Quantity", 1, 5, 3)
        cleanliness = st.slider("Cleanliness", 1, 5, 3)
        service = st.slider("Service", 1, 5, 3)
        
        comments = st.text_area("Additional Comments")
        
        submit = st.form_submit_button("Submit Feedback")
        
        if submit:
            feedback_data = {
                "user": st.session_state.user,
                "date": date.strftime("%Y-%m-%d"),
                "meal": meal.lower(),
                "ratings": {
                    "taste": taste,
                    "quantity": quantity,
                    "cleanliness": cleanliness,
                    "service": service
                },
                "comments": comments
            }
            
            result = post_api_data("feedback/submit", feedback_data)
            
            if result:
                st.success("Thank you for your feedback!")
            else:
                st.error("Failed to submit feedback. Please try again.")

def show_attendance():
    st.title("Meal Attendance History")
    
    # Get last 30 days of attendance
    attendance_data = get_api_data(f"attendance/user/{st.session_state.user}")
    
    if not attendance_data:
        st.info("No attendance data available.")
        return
    
    # Summary statistics
    total_meals = sum([
        sum([1 for a in attendance_data if a["breakfast_attended"]]),
        sum([1 for a in attendance_data if a["lunch_attended"]]),
        sum([1 for a in attendance_data if a["dinner_attended"]])
    ])
    
    total_booked = sum([
        sum([1 for a in attendance_data if a["breakfast_booked"]]),
        sum([1 for a in attendance_data if a["lunch_booked"]]),
        sum([1 for a in attendance_data if a["dinner_booked"]])
    ])
    
    attendance_rate = (total_meals / total_booked * 100) if total_booked > 0 else 0
    
    # Display summary
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Meals Attended", total_meals)
    
    with col2:
        st.metric("Total Meals Booked", total_booked)
    
    with col3:
        st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
    
    # Detailed attendance
    st.subheader("Detailed Attendance")
    
    df = pd.DataFrame(attendance_data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)
    
    # Format for display
    display_df = df.copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    
    for meal in ["breakfast", "lunch", "dinner"]:
        display_df[f"{meal}_status"] = display_df.apply(
            lambda x: "Attended ✅" if x[f"{meal}_attended"] else 
                     ("Missed ❌" if x[f"{meal}_booked"] else "Not Booked"),
            axis=1
        )
    
    st.dataframe(display_df[["date", "breakfast_status", "lunch_status", "dinner_status"]], 
                use_container_width=True)

# Admin views
def show_dashboard():
    st.title("Admin Dashboard")
    
    # Get summary data
    summary = get_api_data("admin/dashboard/summary")
    
    if not summary:
        st.error("Failed to load dashboard data.")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", summary["total_students"])
    
    with col2:
        st.metric("Today's Attendance", 
                 f"{summary['today_attendance']} / {summary['today_bookings']}")
    
    with col3:
        st.metric("Weekly Revenue", f"₹{summary['weekly_revenue']:,}")
    
    with col4:
        st.metric("Feedback Score", f"{summary['avg_feedback']:.1f}/5")
    
    # Display charts
    st.subheader("Weekly Attendance")
    attendance_data = get_api_data("admin/dashboard/attendance")
    
    if attendance_data:
        attendance_df = pd.DataFrame(attendance_data)
        st.line_chart(attendance_df.set_index("date"))
    
    # Feedback overview
    st.subheader("Recent Feedback")
    feedback_data = get_api_data("admin/dashboard/feedback")
    
    if feedback_data:
        feedback_df = pd.DataFrame(feedback_data)
        st.dataframe(feedback_df, use_container_width=True)

def show_menu_management():
    st.title("Menu Management")
    
    # Get current menu
    menu_data = get_api_data("menu/weekly")
    
    if not menu_data:
        menu_data = []
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Convert to dict for easier access
    menu_dict = {item["day"]: item for item in menu_data}
    
    st.subheader("Edit Weekly Menu")
    
    selected_day = st.selectbox("Select Day", days)
    
    current_menu = menu_dict.get(selected_day, {
        "day": selected_day,
        "breakfast": "",
        "lunch": "",
        "dinner": ""
    })
    
    with st.form(f"menu_form_{selected_day}"):
        breakfast = st.text_area("Breakfast", current_menu.get("breakfast", ""))
        lunch = st.text_area("Lunch", current_menu.get("lunch", ""))
        dinner = st.text_area("Dinner", current_menu.get("dinner", ""))
        
        submit = st.form_submit_button("Save Menu")
        
        if submit:
            updated_menu = {
                "day": selected_day,
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
            
            result = post_api_data("menu/update", updated_menu)
            
            if result:
                st.success(f"Menu for {selected_day} updated successfully!")
            else:
                st.error("Failed to update menu. Please try again.")

def show_inventory():
    st.title("Inventory Management")
    
    # Get current inventory
    inventory_data = get_api_data("inventory/all")
    
    if not inventory_data:
        st.info("No inventory data available.")
        inventory_data = []
    
    # Display current inventory
    st.subheader("Current Inventory")
    
    inventory_df = pd.DataFrame(inventory_data)
    st.dataframe(inventory_df, use_container_width=True)
    
    # Add new item
    st.subheader("Add/Update Item")
    
    with st.form("inventory_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=0)
        unit = st.selectbox("Unit", ["kg", "liters", "packets", "boxes", "units"])
        category = st.selectbox("Category", ["Vegetables", "Fruits", "Grains", "Dairy", "Meat", "Spices", "Other"])
        
        submit = st.form_submit_button("Save Item")
        
        if submit:
            if not item_name:
                st.error("Item name is required.")
            else:
                inventory_item = {
                    "name": item_name,
                    "quantity": quantity,
                    "unit": unit,
                    "category": category
                }
                
                result = post_api_data("inventory/update", inventory_item)
                
                if result:
                    st.success(f"Inventory updated successfully!")
                else:
                    st.error("Failed to update inventory. Please try again.")

def show_student_records():
    st.title("Student Records")
    
    # Get all students
    students_data = get_api_data("admin/students")
    
    if not students_data:
        st.info("No student records available.")
        return
    
    # Display students
    st.subheader("All Students")
    
    students_df = pd.DataFrame(students_data)
    st.dataframe(students_df, use_container_width=True)
    
    # Add/Edit student
    st.subheader("Add/Edit Student")
    
    with st.form("student_form"):
        username = st.text_input("Username")
        name = st.text_input("Full Name")
        room_number = st.text_input("Room Number")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        password = st.text_input("Password (leave blank to keep unchanged)", type="password")
        
        submit = st.form_submit_button("Save Student")
        
        if submit:
            if not username or not name:
                st.error("Username and Full Name are required.")
            else:
                student_data = {
                    "username": username,
                    "name": name,
                    "room_number": room_number,
                    "email": email,
                    "phone": phone
                }
                
                if password:
                    student_data["password"] = password
                
                result = post_api_data("admin/students/update", student_data)
                
                if result:
                    st.success(f"Student information updated successfully!")
                else:
                    st.error("Failed to update student information. Please try again.")

def show_reports():
    st.title("Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Attendance Report", "Feedback Report", "Financial Report", "Inventory Usage Report"]
    )
    
    if report_type == "Attendance Report":
        st.subheader("Attendance Report")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            return
        
        # Get attendance data
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        attendance_data = get_api_data(f"reports/attendance?start_date={params['start_date']}&end_date={params['end_date']}")
        
        if not attendance_data:
            st.info("No attendance data available for the selected period.")
            return
        
        # Summary statistics
        total_bookings = attendance_data["total_bookings"]
        total_attended = attendance_data["total_attended"]
        attendance_rate = (total_attended / total_bookings * 100) if total_bookings > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Bookings", total_bookings)
        with col2:
            st.metric("Total Attended", total_attended)
        with col3:
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        
        # Daily attendance chart
        st.subheader("Daily Attendance")
        daily_df = pd.DataFrame(attendance_data["daily"])
        st.line_chart(daily_df.set_index("date"))
        
        # Detailed data
        st.subheader("Detailed Data")
        st.dataframe(pd.DataFrame(attendance_data["details"]), use_container_width=True)
        
    elif report_type == "Feedback Report":
        st.subheader("Feedback Report")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            return
        
        # Get feedback data
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        feedback_data = get_api_data(f"reports/feedback?start_date={params['start_date']}&end_date={params['end_date']}")
        
        if not feedback_data:
            st.info("No feedback data available for the selected period.")
            return
        
        # Average ratings
        avg_ratings = feedback_data["average_ratings"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Taste", f"{avg_ratings['taste']:.1f}/5")
        with col2:
            st.metric("Quantity", f"{avg_ratings['quantity']:.1f}/5")
        with col3:
            st.metric("Cleanliness", f"{avg_ratings['cleanliness']:.1f}/5")
        with col4:
            st.metric("Service", f"{avg_ratings['service']:.1f}/5")
        
        # Feedback by meal
        st.subheader("Feedback by Meal")
        meal_df = pd.DataFrame(feedback_data["by_meal"])
        st.bar_chart(meal_df.set_index("meal"))
        
        # Recent comments
        st.subheader("Recent Comments")
        comments_df = pd.DataFrame(feedback_data["recent_comments"])
        st.dataframe(comments_df, use_container_width=True)
        
    elif report_type == "Financial Report":
        st.subheader("Financial Report")
        
        # Month selection
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        current_month = datetime.now().month - 1  # 0-based index
        current_year = datetime.now().year
        
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox("Month", range(len(months)), index=current_month, format_func=lambda x: months[x])
        with col2:
            selected_year = st.selectbox("Year", range(current_year-2, current_year+1), index=2)
        
        # Get financial data
        params = {
            "month": selected_month + 1,  # 1-based for API
            "year": selected_year
        }
        
        financial_data = get_api_data(f"reports/financial?month={params['month']}&year={params['year']}")
        
        if not financial_data:
            st.info("No financial data available for the selected period.")
            return
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"₹{financial_data['total_revenue']:,}")
        with col2:
            st.metric("Total Expenses", f"₹{financial_data['total_expenses']:,}")
        with col3:
            profit = financial_data['total_revenue'] - financial_data['total_expenses']
            st.metric("Profit/Loss", f"₹{profit:,}", delta=f"₹{profit:,}")
        
        # Revenue breakdown
        st.subheader("Revenue Breakdown")
        revenue_df = pd.DataFrame(financial_data["revenue_breakdown"])
        st.bar_chart(revenue_df.set_index("category"))
        
        # Expense breakdown
        st.subheader("Expense Breakdown")
        expense_df = pd.DataFrame(financial_data["expense_breakdown"])
        st.bar_chart(expense_df.set_index("category"))
        
        # Detailed transactions
        st.subheader("Recent Transactions")
        transactions_df = pd.DataFrame(financial_data["recent_transactions"])
        st.dataframe(transactions_df, use_container_width=True)
        
    elif report_type == "Inventory Usage Report":
        st.subheader("Inventory Usage Report")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            return
        
        # Get inventory usage data
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        inventory_data = get_api_data(f"reports/inventory?start_date={params['start_date']}&end_date={params['end_date']}")
        
        if not inventory_data:
            st.info("No inventory usage data available for the selected period.")
            return
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Items Used", inventory_data["total_items_used"])
        with col2:
            st.metric("Total Cost", f"₹{inventory_data['total_cost']:,}")
        
        # Usage by category
        st.subheader("Usage by Category")
        category_df = pd.DataFrame(inventory_data["usage_by_category"])
        st.bar_chart(category_df.set_index("category"))
        
        # Top used items
        st.subheader("Top Used Items")
        top_items_df = pd.DataFrame(inventory_data["top_items"])
        st.bar_chart(top_items_df.set_index("item"))
        
        # Detailed usage
        st.subheader("Detailed Usage")
        details_df = pd.DataFrame(inventory_data["details"])
        st.dataframe(details_df, use_container_width=True)

# Main app logic
def main():
    if login_user():
        page = render_sidebar()
        
        # Route to appropriate page based on selection and role
        if st.session_state.role == "student":
            if page == "Menu":
                show_menu()
            elif page == "Meal Booking":
                show_meal_booking()
            elif page == "Feedback":
                show_feedback()
            elif page == "Attendance":
                show_attendance()
        else:  # admin role
            if page == "Dashboard":
                show_dashboard()
            elif page == "Menu Management":
                show_menu_management()
            elif page == "Inventory":
                show_inventory()
            elif page == "Student Records":
                show_student_records()
            elif page == "Reports":
                show_reports()

if __name__ == "__main__":
    main()
