from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
import uuid

app = FastAPI(title="Hostel Mess Management System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Data models
class User(BaseModel):
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    room_number: Optional[str] = None
    role: str = "student"

class UserInDB(User):
    hashed_password: str

class UserCreate(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MenuItem(BaseModel):
    day: str
    breakfast: str
    lunch: str
    dinner: str

class Booking(BaseModel):
    user: str
    date: str
    breakfast: bool = False
    lunch: bool = False
    dinner: bool = False

class Feedback(BaseModel):
    user: str
    date: str
    meal: str
    ratings: Dict[str, int]
    comments: Optional[str] = None

class InventoryItem(BaseModel):
    name: str
    quantity: float
    unit: str
    category: str

# In-memory data storage (in production, this would be a database)
users_db = {
    "admin": {
        "username": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "phone": "1234567890",
        "room_number": "Admin",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123")
    },
    "student1": {
        "username": "student1",
        "name": "Student One",
        "email": "student1@example.com",
        "phone": "9876543210",
        "room_number": "A101",
        "role": "student",
        "hashed_password": pwd_context.hash("student123")
    }
}

menu_db = [
    {
        "day": "Monday",
        "breakfast": "Bread, Butter, Jam, Eggs, Milk, Tea",
        "lunch": "Rice, Dal, Chapati, Paneer Curry, Salad",
        "dinner": "Rice, Dal, Chapati, Mixed Vegetable, Curd"
    },
    {
        "day": "Tuesday",
        "breakfast": "Idli, Sambhar, Coconut Chutney, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Chicken Curry, Salad",
        "dinner": "Rice, Dal, Chapati, Aloo Gobi, Raita"
    },
    {
        "day": "Wednesday",
        "breakfast": "Paratha, Curd, Pickle, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Rajma, Salad",
        "dinner": "Rice, Dal, Chapati, Egg Curry, Salad"
    },
    {
        "day": "Thursday",
        "breakfast": "Poha, Upma, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Chole, Salad",
        "dinner": "Rice, Dal, Chapati, Mix Veg, Kheer"
    },
    {
        "day": "Friday",
        "breakfast": "Dosa, Sambhar, Coconut Chutney, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Kadhi Pakora, Salad",
        "dinner": "Rice, Dal, Chapati, Matar Paneer, Raita"
    },
    {
        "day": "Saturday",
        "breakfast": "Bread, Omelette, Jam, Butter, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Fish Curry, Salad",
        "dinner": "Rice, Dal, Chapati, Aloo Matar, Custard"
    },
    {
        "day": "Sunday",
        "breakfast": "Puri, Aloo Sabzi, Tea, Coffee",
        "lunch": "Rice, Dal, Chapati, Mutton/Paneer, Salad, Ice Cream",
        "dinner": "Rice, Dal, Chapati, Veg Biryani, Raita"
    }
]

bookings_db = []
feedback_db = []
inventory_db = [
    {"name": "Rice", "quantity": 50.0, "unit": "kg", "category": "Grains"},
    {"name": "Wheat Flour", "quantity": 30.0, "unit": "kg", "category": "Grains"},
    {"name": "Potatoes", "quantity": 20.0, "unit": "kg", "category": "Vegetables"},
    {"name": "Onions", "quantity": 15.0, "unit": "kg", "category": "Vegetables"},
    {"name": "Tomatoes", "quantity": 10.0, "unit": "kg", "category": "Vegetables"},
    {"name": "Milk", "quantity": 25.0, "unit": "liters", "category": "Dairy"},
    {"name": "Cooking Oil", "quantity": 20.0, "unit": "liters", "category": "Other"},
    {"name": "Sugar", "quantity": 10.0, "unit": "kg", "category": "Other"},
    {"name": "Salt", "quantity": 5.0, "unit": "kg", "category": "Other"},
    {"name": "Chicken", "quantity": 15.0, "unit": "kg", "category": "Meat"}
]

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# API Endpoints

# Authentication
@app.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: dict):
    user = authenticate_user(form_data["username"], form_data["password"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# Menu Endpoints
@app.get("/menu/weekly")
async def get_weekly_menu():
    return menu_db

@app.post("/menu/update")
async def update_menu(menu_item: MenuItem, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update menu")
    
    # Find and update the menu item
    for i, item in enumerate(menu_db):
        if item["day"] == menu_item.day:
            menu_db[i] = menu_item.dict()
            return {"status": "success", "message": f"Menu for {menu_item.day} updated"}
    
    # If day not found, add it
    menu_db.append(menu_item.dict())
    return {"status": "success", "message": f"Menu for {menu_item.day} added"}

# Booking Endpoints
@app.get("/bookings/user/{username}")
async def get_user_bookings(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view these bookings")
    
    user_bookings = [booking for booking in bookings_db if booking["user"] == username]
    return user_bookings

@app.post("/bookings/save")
async def save_booking(booking: Booking, current_user: User = Depends(get_current_user)):
    if current_user.username != booking.user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to save this booking")
    
    # Check if booking already exists for this date and user
    for i, existing in enumerate(bookings_db):
        if existing["user"] == booking.user and existing["date"] == booking.date:
            # Update existing booking
            bookings_db[i] = booking.dict()
            return {"status": "success", "message": "Booking updated"}
    
    # Add new booking
    bookings_db.append(booking.dict())
    return {"status": "success", "message": "Booking saved"}

# Feedback Endpoints
@app.post("/feedback/submit")
async def submit_feedback(feedback: Feedback, current_user: User = Depends(get_current_user)):
    if current_user.username != feedback.user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to submit this feedback")
    
    # Add feedback with ID
    feedback_data = feedback.dict()
    feedback_data["id"] = str(uuid.uuid4())
    feedback_data["timestamp"] = datetime.utcnow().isoformat()
    
    feedback_db.append(feedback_data)
    return {"status": "success", "message": "Feedback submitted", "id": feedback_data["id"]}

@app.get("/feedback/user/{username}")
async def get_user_feedback(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this feedback")
    
    user_feedback = [feedback for feedback in feedback_db if feedback["user"] == username]
    return user_feedback

# Inventory Endpoints
@app.get("/inventory/all")
async def get_all_inventory(current_user: User = Depends(get_current_user)):
    return inventory_db

@app.post("/inventory/update")
async def update_inventory(item: InventoryItem, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update inventory")
    
    # Check if item already exists
    for i, existing in enumerate(inventory_db):
        if existing["name"] == item.name:
            # Update existing item
            inventory_db[i] = item.dict()
            return {"status": "success", "message": f"Inventory item {item.name} updated"}
    
    # Add new item
    inventory_db.append(item.dict())
    return {"status": "success", "message": f"Inventory item {item.name} added"}

# Attendance Endpoints
@app.get("/attendance/user/{username}")
async def get_user_attendance(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this attendance")
    
    # Generate sample attendance data based on bookings
    user_bookings = [booking for booking in bookings_db if booking["user"] == username]
    
    attendance = []
    for booking in user_bookings:
        # Simulate random attendance (in a real app, this would be actual data)
        import random
        attendance_record = {
            "date": booking["date"],
            "breakfast_booked": booking["breakfast"],
            "lunch_booked": booking["lunch"],
            "dinner_booked": booking["dinner"],
            "breakfast_attended": booking["breakfast"] and random.random() > 0.2,
            "lunch_attended": booking["lunch"] and random.random() > 0.1,
            "dinner_attended": booking["dinner"] and random.random() > 0.15
        }
        attendance.append(attendance_record)
    
    return attendance

# Admin Endpoints
@app.get("/admin/students")
async def get_all_students(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    students = []
    for username, user_data in users_db.items():
        if user_data["role"] == "student":
            student = {k: v for k, v in user_data.items() if k != "hashed_password"}
            students.append(student)
    
    return students

@app.post("/admin/students/update")
async def update_student(student_data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    username = student_data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    # Check if student exists
    if username in users_db:
        # Update existing student
        for key, value in student_data.items():
            if key != "password" and key != "role":  # Don't update role directly
                users_db[username][key] = value
        
        # Update password if provided
        if "password" in student_data and student_data["password"]:
            users_db[username]["hashed_password"] = pwd_context.hash(student_data["password"])
        
        return {"status": "success", "message": f"Student {username} updated"}
    else:
        # Create new student
        new_student = {
            "username": username,
            "name": student_data.get("name", ""),
            "email": student_data.get("email", ""),
            "phone": student_data.get("phone", ""),
            "room_number": student_data.get("room_number", ""),
            "role": "student"
        }
        
        if "password" in student_data and student_data["password"]:
            new_student["hashed_password"] = pwd_context.hash(student_data["password"])
        else:
            new_student["hashed_password"] = pwd_context.hash("changeme")  # Default password
        
        users_db[username] = new_student
        return {"status": "success", "message": f"Student {username} created"}

# Dashboard and Reports Endpoints
@app.get("/admin/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Generate sample dashboard data
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Count students
    student_count = sum(1 for user in users_db.values() if user["role"] == "student")
    
    # Count today's bookings and attendance
    today_bookings = sum(1 for booking in bookings_db 
                         if booking["date"] == today and 
                         (booking["breakfast"] or booking["lunch"] or booking["dinner"]))
    
    # In a real app, this would be actual attendance data
    today_attendance = int(today_bookings * 0.85)  # Assume 85% attendance rate
    
    # Calculate weekly revenue (sample data)
    weekly_revenue = student_count * 50 * 7  # Assuming ₹50 per student per day
    
    # Calculate average feedback score
    if feedback_db:
        total_ratings = 0
        rating_count = 0
        for feedback in feedback_db:
            for category, rating in feedback["ratings"].items():
                total_ratings += rating
                rating_count += 1
        avg_feedback = total_ratings / rating_count if rating_count > 0 else 0
    else:
        avg_feedback = 0
    
    return {
        "total_students": student_count,
        "today_bookings": today_bookings,
        "today_attendance": today_attendance,
        "weekly_revenue": weekly_revenue,
        "avg_feedback": avg_feedback
    }

@app.get("/admin/dashboard/attendance")
async def get_dashboard_attendance(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Generate sample attendance data for the past week
    today = datetime.now()
    
    attendance_data = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        day_name = (today - timedelta(days=i)).strftime("%A")
        
        # In a real app, this would be actual data
        breakfast_count = 20 + i  # Sample data
        lunch_count = 25 + i      # Sample data
        dinner_count = 22 + i     # Sample data
        
        attendance_data.append({
            "date": date,
            "day": day_name,
            "breakfast": breakfast_count,
            "lunch": lunch_count,
            "dinner": dinner_count,
            "total": breakfast_count + lunch_count + dinner_count
        })
    
    return attendance_data

@app.get("/admin/dashboard/feedback")
async def get_dashboard_feedback(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get recent feedback with names instead of usernames
    recent_feedback = []
    for feedback in sorted(feedback_db, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]:
        username = feedback["user"]
        name = users_db.get(username, {}).get("name", username)
        
        feedback_entry = {
            "id": feedback.get("id", ""),
            "date": feedback["date"],
            "name": name,
            "meal": feedback["meal"],
            "average_rating": sum(feedback["ratings"].values()) / len(feedback["ratings"]),
            "comments": feedback.get("comments", "")
        }
        recent_feedback.append(feedback_entry)
    
    return recent_feedback

@app.get("/reports/attendance")
async def get_attendance_report(
    start_date: str, 
    end_date: str, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In a real app, this would query a database
    # For demo purposes, we'll generate sample data
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    days = (end - start).days + 1
    
    # Generate daily data
    daily_data = []
    total_bookings = 0
    total_attended = 0
    
    for i in range(days):
        current_date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        day_name = (start + timedelta(days=i)).strftime("%A")
        
        # Sample data generation
        if day_name in ["Saturday", "Sunday"]:
            bookings = 40 + int(5 * (i % 3))  # Less bookings on weekends
        else:
            bookings = 60 + int(8 * (i % 5))
            
        attended = int(bookings * (0.75 + 0.15 * (i % 3) / 3))  # Random attendance rate
        
        daily_data.append({
            "date": current_date,
            "day": day_name,
            "bookings": bookings,
            "attended": attended,
            "percentage": round(attended / bookings * 100 if bookings > 0 else 0, 1)
        })
        
        total_bookings += bookings
        total_attended += attended
    
    # Generate details for students (sample data)
    details = []
    for username, user in users_db.items():
        if user["role"] == "student":
            # Sample attendance data for each student
            student_bookings = int(days * 2.5 * (0.7 + 0.3 * (hash(username) % 10) / 10))
            student_attended = int(student_bookings * (0.7 + 0.3 * (hash(username) % 10) / 10))
            
            details.append({
                "username": username,
                "name": user["name"],
                "room": user["room_number"],
                "bookings": student_bookings,
                "attended": student_attended,
                "percentage": round(student_attended / student_bookings * 100 if student_bookings > 0 else 0, 1)
            })
    
    return {
        "total_bookings": total_bookings,
        "total_attended": total_attended,
        "attendance_rate": round(total_attended / total_bookings * 100 if total_bookings > 0 else 0, 1),
        "daily": daily_data,
        "details": sorted(details, key=lambda x: x["percentage"], reverse=True)
    }

@app.get("/reports/feedback")
async def get_feedback_report(
    start_date: str, 
    end_date: str, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Filter feedback within date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # In a real app, this would query a database
    # For demo, we'll use the existing data and add some if needed
    
    # Ensure we have some data to work with
    if len(feedback_db) < 10:
        # Generate sample feedback data
        for i in range(20):
            date = (start + timedelta(days=i % 10)).strftime("%Y-%m-%d")
            meal = ["breakfast", "lunch", "dinner"][i % 3]
            user = list(users_db.keys())[i % len(users_db)]
            
            feedback_data = {
                "id": str(uuid.uuid4()),
                "user": user,
                "date": date,
                "meal": meal,
                "ratings": {
                    "taste": 3 + (i % 3),
                    "quantity": 3 + ((i + 1) % 3),
                    "cleanliness": 4 + (i % 2),
                    "service": 3 + ((i + 2) % 3)
                },
                "comments": f"Sample feedback #{i}",
                "timestamp": datetime.utcnow().isoformat()
            }
            feedback_db.append(feedback_data)
    
    # Filter feedback within date range
    filtered_feedback = [
        f for f in feedback_db 
        if start_date <= f["date"] <= end_date
    ]
    
    # Calculate average ratings
    total_ratings = {"taste": 0, "quantity": 0, "cleanliness": 0, "service": 0}
    counts = {"taste": 0, "quantity": 0, "cleanliness": 0, "service": 0}
    
    for feedback in filtered_feedback:
        for category, rating in feedback["ratings"].items():
            total_ratings[category] += rating
            counts[category] += 1
    
    average_ratings = {
        category: round(total / counts[category], 1) if counts[category] > 0 else 0
        for category, total in total_ratings.items()
    }
    
    # Get ratings by meal
    meals = ["breakfast", "lunch", "dinner"]
    by_meal = []
    
    for meal in meals:
        meal_feedback = [f for f in filtered_feedback if f["meal"] == meal]
        
        if meal_feedback:
            avg_rating = sum(
                sum(f["ratings"].values()) / len(f["ratings"]) 
                for f in meal_feedback
            ) / len(meal_feedback)
        else:
            avg_rating = 0
        
        by_meal.append({
            "meal": meal.capitalize(),
            "count": len(meal_feedback),
            "average_rating": round(avg_rating, 1)
        })
    
    # Get recent comments
    recent_comments = []
    for feedback in sorted(filtered_feedback, key=lambda x: x.get("date", ""), reverse=True)[:10]:
        if "comments" in feedback and feedback["comments"].strip():
            username = feedback["user"]
            name = users_db.get(username, {}).get("name", username)
            
            comment_entry = {
                "date": feedback["date"],
                "name": name,
                "meal": feedback["meal"].capitalize(),
                "rating": sum(feedback["ratings"].values()) / len(feedback["ratings"]),
                "comment": feedback["comments"]
            }
            recent_comments.append(comment_entry)
    
    return {
        "average_ratings": average_ratings,
        "by_meal": by_meal,
        "recent_comments": recent_comments,
        "total_feedback": len(filtered_feedback)
    }

@app.get("/reports/financial")
async def get_financial_report(
    month: int, 
    year: int, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In a real app, this would query financial records
    # For demo purposes, we'll generate sample data
    
    # Number of students
    student_count = sum(1 for user in users_db.values() if user["role"] == "student")
    
    # Calculate days in month
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Generate revenue data
    daily_rate = 50  # ₹50 per student per day
    monthly_revenue = student_count * daily_rate * days_in_month
    
    # Revenue breakdown
    revenue_breakdown = [
        {"category": "Regular Meals", "amount": monthly_revenue * 0.85},
        {"category": "Special Meals", "amount": monthly_revenue * 0.1},
        {"category": "Extra Items", "amount": monthly_revenue * 0.05}
    ]
    
    # Expense categories and percentages
    expense_categories = [
        {"category": "Food Ingredients", "percentage": 0.6},
        {"category": "Staff Salaries", "percentage": 0.2},
        {"category": "Utilities", "percentage": 0.1},
        {"category": "Maintenance", "percentage": 0.05},
        {"category": "Miscellaneous", "percentage": 0.05}
    ]
    
    # Calculate expenses (assuming expenses are 80% of revenue)
    total_expenses = monthly_revenue * 0.8
    
    # Expense breakdown
    expense_breakdown = [
        {"category": cat["category"], "amount": total_expenses * cat["percentage"]}
        for cat in expense_categories
    ]
    
    # Generate sample transactions
    import random
    transactions = []
    
    # Expense transactions
    for i in range(20):
        category = random.choice(expense_categories)["category"]
        amount = round(random.uniform(500, 5000), 2)
        
        transactions.append({
            "date": f"{year}-{month:02d}-{random.randint(1, days_in_month):02d}",
            "description": f"{category} - {['Payment', 'Purchase', 'Bill'][i % 3]} #{i+1}",
            "type": "expense",
            "category": category,
            "amount": amount
        })
    
    # Revenue transactions
    for i in range(10):
        category = random.choice(["Regular Meals", "Special Meals", "Extra Items"])
        amount = round(random.uniform(5000, 20000), 2)
        
        transactions.append({
            "date": f"{year}-{month:02d}-{random.randint(1, days_in_month):02d}",
            "description": f"{category} - Collection #{i+1}",
            "type": "revenue",
            "category": category,
            "amount": amount
        })
    
    return {
        "total_revenue": monthly_revenue,
        "total_expenses": total_expenses,
        "revenue_breakdown": revenue_breakdown,
        "expense_breakdown": expense_breakdown,
        "recent_transactions": sorted(transactions, key=lambda x: x["date"], reverse=True)
    }

@app.get("/reports/inventory")
async def get_inventory_report(
    start_date: str, 
    end_date: str, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In a real app, this would query inventory usage records
    # For demo purposes, we'll generate sample data
    
    # Generate random usage data based on inventory
    usage_data = []
    total_cost = 0
    
    for item in inventory_db:
        # Random usage between 10% and 50% of current quantity
        usage_quantity = round(item["quantity"] * random.uniform(0.1, 0.5), 2)
        
        # Random cost based on category
        if item["category"] == "Meat":
            unit_cost = random.uniform(200, 500)
        elif item["category"] == "Dairy":
            unit_cost = random.uniform(50, 100)
        elif item["category"] == "Vegetables":
            unit_cost = random.uniform(30, 80)
        elif item["category"] == "Fruits":
            unit_cost = random.uniform(60, 150)
        else:
            unit_cost = random.uniform(40, 120)
        
        item_cost = usage_quantity * unit_cost
        total_cost += item_cost
        
        usage_data.append({
            "item": item["name"],
            "category": item["category"],
            "quantity": usage_quantity,
            "unit": item["unit"],
            "unit_cost": round(unit_cost, 2),
            "total_cost": round(item_cost, 2)
        })
    
    # Sort by total cost
    usage_data = sorted(usage_data, key=lambda x: x["total_cost"], reverse=True)
    
    # Usage by category
    categories = {}
    for item in usage_data:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += item["total_cost"]
    
    usage_by_category = [
        {"category": cat, "amount": round(amount, 2)}
        for cat, amount in categories.items()
    ]
    
    # Top used items (by cost)
    top_items = [
        {"item": item["item"], "amount": item["total_cost"]}
        for item in usage_data[:8]  # Top 8 items
    ]
    
    return {
        "total_items_used": len(usage_data),
        "total_cost": round(total_cost, 2),
        "usage_by_category": usage_by_category,
        "top_items": top_items,
        "details": usage_data
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Hostel Mess Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
