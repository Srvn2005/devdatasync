from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import json
import os

# JWT Settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI(title="Hostel Mess Management System API")

# Set up CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
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

class MealItem(BaseModel):
    item: str
    quantity: int

class Booking(BaseModel):
    user: str
    date: str
    breakfast: bool = False
    lunch: bool = False
    dinner: bool = False
    breakfast_items: Optional[List[MealItem]] = []
    lunch_items: Optional[List[MealItem]] = []
    dinner_items: Optional[List[MealItem]] = []

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

# In-memory data (will be replaced with a database in production)
fake_users_db = {
    "admin": {
        "username": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "phone": "1234567890",
        "room_number": "A-101",
        "role": "admin",
        "hashed_password": pwd_context.hash("adminpassword")
    },
    "student": {
        "username": "student",
        "name": "Student User",
        "email": "student@example.com",
        "phone": "9876543210",
        "room_number": "B-202",
        "role": "student",
        "hashed_password": pwd_context.hash("studentpassword")
    }
}

weekly_menu = [
    {"day": "Monday", "breakfast": "Bread, Eggs, Tea", "lunch": "Rice, Dal, Vegetables", "dinner": "Roti, Curry, Salad"},
    {"day": "Tuesday", "breakfast": "Paratha, Curd, Coffee", "lunch": "Rice, Sambar, Papad", "dinner": "Roti, Paneer, Pickle"},
    {"day": "Wednesday", "breakfast": "Idli, Sambar, Tea", "lunch": "Rice, Rajma, Curd", "dinner": "Roti, Chicken, Salad"},
    {"day": "Thursday", "breakfast": "Upma, Chutney, Coffee", "lunch": "Rice, Dal, Pakoda", "dinner": "Roti, Mix Veg, Raita"},
    {"day": "Friday", "breakfast": "Poha, Tea", "lunch": "Rice, Kadhi, Papad", "dinner": "Pulao, Raita, Sweet"},
    {"day": "Saturday", "breakfast": "Sandwich, Coffee", "lunch": "Chole Bhature, Pickle", "dinner": "Roti, Fish Curry, Salad"},
    {"day": "Sunday", "breakfast": "Aloo Paratha, Curd, Tea", "lunch": "Biryani, Raita, Sweet", "dinner": "Pizza, Soup, Ice Cream"}
]

bookings = []
feedback_data = []
inventory = [
    {"name": "Rice", "quantity": 50.0, "unit": "kg", "category": "Grains"},
    {"name": "Wheat Flour", "quantity": 30.0, "unit": "kg", "category": "Grains"},
    {"name": "Milk", "quantity": 20.0, "unit": "liter", "category": "Dairy"},
    {"name": "Tomatoes", "quantity": 10.0, "unit": "kg", "category": "Vegetables"},
    {"name": "Onions", "quantity": 15.0, "unit": "kg", "category": "Vegetables"},
    {"name": "Chicken", "quantity": 25.0, "unit": "kg", "category": "Meat"},
    {"name": "Cooking Oil", "quantity": 10.0, "unit": "liter", "category": "Oils"}
]

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
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
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/menu", response_model=List[MenuItem])
async def get_weekly_menu():
    return weekly_menu

@app.post("/menu/update")
async def update_menu(menu_item: MenuItem, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for i, item in enumerate(weekly_menu):
        if item["day"] == menu_item.day:
            weekly_menu[i] = menu_item.dict()
            return {"message": f"Menu for {menu_item.day} updated successfully"}
    
    weekly_menu.append(menu_item.dict())
    return {"message": f"Menu for {menu_item.day} added successfully"}

@app.get("/bookings/{username}")
async def get_user_bookings(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_bookings = [booking for booking in bookings if booking["user"] == username]
    return user_bookings

@app.post("/bookings/save")
async def save_booking(booking: Booking, current_user: User = Depends(get_current_user)):
    if current_user.username != booking.user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if booking already exists for the date
    existing_booking = next((b for b in bookings if b["user"] == booking.user and b["date"] == booking.date), None)
    
    if existing_booking:
        # Update existing booking
        for i, b in enumerate(bookings):
            if b["user"] == booking.user and b["date"] == booking.date:
                bookings[i] = booking.dict()
                return {"message": "Booking updated successfully"}
    else:
        # Create new booking
        bookings.append(booking.dict())
        return {"message": "Booking created successfully"}

@app.post("/feedback/submit")
async def submit_feedback(feedback: Feedback, current_user: User = Depends(get_current_user)):
    if current_user.username != feedback.user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    feedback_data.append(feedback.dict())
    return {"message": "Feedback submitted successfully"}

@app.get("/feedback/{username}")
async def get_user_feedback(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_feedback = [feedback for feedback in feedback_data if feedback["user"] == username]
    return user_feedback

@app.get("/inventory")
async def get_all_inventory(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return inventory

@app.post("/inventory/update")
async def update_inventory(item: InventoryItem, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if item exists
    existing_item = next((i for i in inventory if i["name"] == item.name), None)
    
    if existing_item:
        # Update existing item
        for i, inv_item in enumerate(inventory):
            if inv_item["name"] == item.name:
                inventory[i] = item.dict()
                return {"message": f"Inventory item {item.name} updated successfully"}
    else:
        # Create new item
        inventory.append(item.dict())
        return {"message": f"Inventory item {item.name} added successfully"}

@app.get("/attendance/{username}")
async def get_user_attendance(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate attendance based on bookings
    user_bookings = [booking for booking in bookings if booking["user"] == username]
    
    attendance = []
    for booking in user_bookings:
        meals_attended = 0
        if booking["breakfast"]:
            meals_attended += 1
        if booking["lunch"]:
            meals_attended += 1
        if booking["dinner"]:
            meals_attended += 1
        
        attendance.append({
            "date": booking["date"],
            "meals_attended": meals_attended,
            "total_meals": 3,
            "details": {
                "breakfast": booking["breakfast"],
                "lunch": booking["lunch"],
                "dinner": booking["dinner"]
            }
        })
    
    return attendance

@app.get("/students")
async def get_all_students(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    students = []
    for username, user_data in fake_users_db.items():
        if user_data["role"] == "student":
            user_copy = user_data.copy()
            user_copy.pop("hashed_password")
            students.append(user_copy)
    
    return students

@app.post("/students/update")
async def update_student(student_data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    username = student_data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    if username in fake_users_db:
        # Update existing student
        student = fake_users_db[username]
        student.update({k: v for k, v in student_data.items() if k != "hashed_password"})
        
        # Update password if provided
        if "password" in student_data:
            student["hashed_password"] = pwd_context.hash(student_data["password"])
        
        return {"message": f"Student {username} updated successfully"}
    else:
        # Create new student
        if "password" not in student_data:
            raise HTTPException(status_code=400, detail="Password is required for new students")
        
        new_student = {
            "username": username,
            "name": student_data.get("name", ""),
            "email": student_data.get("email", ""),
            "phone": student_data.get("phone", ""),
            "room_number": student_data.get("room_number", ""),
            "role": "student",
            "hashed_password": pwd_context.hash(student_data["password"])
        }
        
        fake_users_db[username] = new_student
        return {"message": f"Student {username} created successfully"}

@app.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Count students
    student_count = sum(1 for user in fake_users_db.values() if user["role"] == "student")
    
    # Count total bookings
    booking_count = len(bookings)
    
    # Count today's meals and calculate item quantities
    today = datetime.now().strftime("%Y-%m-%d")
    today_bookings = [b for b in bookings if b["date"] == today]
    
    breakfast_count = sum(1 for b in today_bookings if b["breakfast"])
    lunch_count = sum(1 for b in today_bookings if b["lunch"])
    dinner_count = sum(1 for b in today_bookings if b["dinner"])
    
    # Calculate quantities for each meal item
    breakfast_items = {}
    lunch_items = {}
    dinner_items = {}
    
    for booking in today_bookings:
        # Compile breakfast item quantities
        if booking.get("breakfast") and "breakfast_items" in booking:
            for item in booking.get("breakfast_items", []):
                item_name = item.get("item", "")
                if item_name:
                    if item_name not in breakfast_items:
                        breakfast_items[item_name] = 0
                    breakfast_items[item_name] += item.get("quantity", 0)
        
        # Compile lunch item quantities
        if booking.get("lunch") and "lunch_items" in booking:
            for item in booking.get("lunch_items", []):
                item_name = item.get("item", "")
                if item_name:
                    if item_name not in lunch_items:
                        lunch_items[item_name] = 0
                    lunch_items[item_name] += item.get("quantity", 0)
        
        # Compile dinner item quantities
        if booking.get("dinner") and "dinner_items" in booking:
            for item in booking.get("dinner_items", []):
                item_name = item.get("item", "")
                if item_name:
                    if item_name not in dinner_items:
                        dinner_items[item_name] = 0
                    dinner_items[item_name] += item.get("quantity", 0)
    
    # Count feedback
    feedback_count = len(feedback_data)
    
    return {
        "student_count": student_count,
        "booking_count": booking_count,
        "today_meals": {
            "breakfast": breakfast_count,
            "lunch": lunch_count,
            "dinner": dinner_count
        },
        "meal_items": {
            "breakfast": breakfast_items,
            "lunch": lunch_items,
            "dinner": dinner_items
        },
        "feedback_count": feedback_count
    }

@app.get("/dashboard/attendance")
async def get_dashboard_attendance(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all dates from bookings
    all_dates = set(booking["date"] for booking in bookings)
    
    # Calculate attendance by date
    attendance_by_date = []
    for date in all_dates:
        date_bookings = [b for b in bookings if b["date"] == date]
        breakfast_count = sum(1 for b in date_bookings if b["breakfast"])
        lunch_count = sum(1 for b in date_bookings if b["lunch"])
        dinner_count = sum(1 for b in date_bookings if b["dinner"])
        
        attendance_by_date.append({
            "date": date,
            "breakfast": breakfast_count,
            "lunch": lunch_count,
            "dinner": dinner_count,
            "total": breakfast_count + lunch_count + dinner_count
        })
    
    # Sort by date
    attendance_by_date.sort(key=lambda x: x["date"])
    
    return attendance_by_date

@app.get("/dashboard/feedback")
async def get_dashboard_feedback(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate average ratings
    meals = ["breakfast", "lunch", "dinner"]
    rating_categories = ["taste", "quantity", "hygiene", "service"]
    
    meal_ratings = {}
    for meal in meals:
        meal_feedback = [f for f in feedback_data if f["meal"] == meal]
        if not meal_feedback:
            meal_ratings[meal] = {cat: 0 for cat in rating_categories}
            continue
        
        meal_avg = {}
        for category in rating_categories:
            ratings = [f["ratings"].get(category, 0) for f in meal_feedback]
            meal_avg[category] = sum(ratings) / len(ratings) if ratings else 0
        
        meal_ratings[meal] = meal_avg
    
    # Get recent comments
    recent_comments = []
    for feedback in sorted(feedback_data, key=lambda x: x["date"], reverse=True)[:5]:
        if feedback.get("comments"):
            recent_comments.append({
                "user": feedback["user"],
                "date": feedback["date"],
                "meal": feedback["meal"],
                "comment": feedback["comments"]
            })
    
    return {
        "average_ratings": meal_ratings,
        "recent_comments": recent_comments
    }

@app.get("/reports/attendance")
async def get_attendance_report(
    start_date: str, 
    end_date: str, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Filter bookings within date range
    filtered_bookings = [
        b for b in bookings 
        if start_date <= b["date"] <= end_date
    ]
    
    # Calculate attendance by student
    student_attendance = {}
    for booking in filtered_bookings:
        username = booking["user"]
        if username not in student_attendance:
            student_attendance[username] = {
                "total_meals": 0,
                "meals_attended": {
                    "breakfast": 0,
                    "lunch": 0,
                    "dinner": 0
                }
            }
        
        if booking["breakfast"]:
            student_attendance[username]["meals_attended"]["breakfast"] += 1
            student_attendance[username]["total_meals"] += 1
        
        if booking["lunch"]:
            student_attendance[username]["meals_attended"]["lunch"] += 1
            student_attendance[username]["total_meals"] += 1
        
        if booking["dinner"]:
            student_attendance[username]["meals_attended"]["dinner"] += 1
            student_attendance[username]["total_meals"] += 1
    
    # Get student names
    for username in student_attendance:
        if username in fake_users_db:
            student_attendance[username]["name"] = fake_users_db[username]["name"]
        else:
            student_attendance[username]["name"] = username
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "student_attendance": student_attendance
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
    filtered_feedback = [
        f for f in feedback_data 
        if start_date <= f["date"] <= end_date
    ]
    
    # Calculate average ratings by meal and category
    meals = ["breakfast", "lunch", "dinner"]
    rating_categories = ["taste", "quantity", "hygiene", "service"]
    
    meal_ratings = {}
    for meal in meals:
        meal_feedback = [f for f in filtered_feedback if f["meal"] == meal]
        if not meal_feedback:
            meal_ratings[meal] = {cat: 0 for cat in rating_categories}
            continue
        
        meal_avg = {}
        for category in rating_categories:
            ratings = [f["ratings"].get(category, 0) for f in meal_feedback]
            meal_avg[category] = sum(ratings) / len(ratings) if ratings else 0
        
        meal_ratings[meal] = meal_avg
    
    # Collect all comments
    all_comments = []
    for feedback in filtered_feedback:
        if feedback.get("comments"):
            all_comments.append({
                "user": feedback["user"],
                "date": feedback["date"],
                "meal": feedback["meal"],
                "comment": feedback["comments"]
            })
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "average_ratings": meal_ratings,
        "comments": all_comments
    }

@app.get("/reports/financial")
async def get_financial_report(
    month: int, 
    year: int, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mock financial data for demonstration
    meal_costs = {
        "breakfast": 25.0,
        "lunch": 40.0,
        "dinner": 35.0
    }
    
    # Filter bookings for the given month and year
    filtered_bookings = []
    for booking in bookings:
        booking_date = datetime.strptime(booking["date"], "%Y-%m-%d")
        if booking_date.month == month and booking_date.year == year:
            filtered_bookings.append(booking)
    
    # Calculate total costs
    total_breakfast_count = sum(1 for b in filtered_bookings if b["breakfast"])
    total_lunch_count = sum(1 for b in filtered_bookings if b["lunch"])
    total_dinner_count = sum(1 for b in filtered_bookings if b["dinner"])
    
    breakfast_cost = total_breakfast_count * meal_costs["breakfast"]
    lunch_cost = total_lunch_count * meal_costs["lunch"]
    dinner_cost = total_dinner_count * meal_costs["dinner"]
    
    total_cost = breakfast_cost + lunch_cost + dinner_cost
    
    # Calculate per-student costs
    student_costs = {}
    for booking in filtered_bookings:
        username = booking["user"]
        if username not in student_costs:
            student_costs[username] = {
                "breakfast": 0,
                "lunch": 0,
                "dinner": 0,
                "total": 0
            }
        
        if booking["breakfast"]:
            student_costs[username]["breakfast"] += meal_costs["breakfast"]
            student_costs[username]["total"] += meal_costs["breakfast"]
        
        if booking["lunch"]:
            student_costs[username]["lunch"] += meal_costs["lunch"]
            student_costs[username]["total"] += meal_costs["lunch"]
        
        if booking["dinner"]:
            student_costs[username]["dinner"] += meal_costs["dinner"]
            student_costs[username]["total"] += meal_costs["dinner"]
    
    # Get student names
    for username in student_costs:
        if username in fake_users_db:
            student_costs[username]["name"] = fake_users_db[username]["name"]
        else:
            student_costs[username]["name"] = username
    
    return {
        "month": month,
        "year": year,
        "meal_costs": meal_costs,
        "total_costs": {
            "breakfast": breakfast_cost,
            "lunch": lunch_cost,
            "dinner": dinner_cost,
            "total": total_cost
        },
        "meal_counts": {
            "breakfast": total_breakfast_count,
            "lunch": total_lunch_count,
            "dinner": total_dinner_count
        },
        "student_costs": student_costs
    }

@app.get("/reports/inventory")
async def get_inventory_report(
    start_date: str, 
    end_date: str, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mock inventory usage data for demonstration
    inventory_usage = []
    for item in inventory:
        # Generate random usage data
        initial_quantity = item["quantity"] * 1.2  # 20% more than current
        used_quantity = initial_quantity - item["quantity"]
        
        inventory_usage.append({
            "name": item["name"],
            "category": item["category"],
            "initial_quantity": initial_quantity,
            "current_quantity": item["quantity"],
            "used_quantity": used_quantity,
            "unit": item["unit"]
        })
    
    # Group by category
    category_usage = {}
    for item in inventory_usage:
        category = item["category"]
        if category not in category_usage:
            category_usage[category] = {
                "used_quantity": 0,
                "items": []
            }
        
        category_usage[category]["used_quantity"] += item["used_quantity"]
        category_usage[category]["items"].append(item["name"])
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "inventory_usage": inventory_usage,
        "category_usage": category_usage
    }

@app.get("/")
async def root():
    return {"message": "Welcome to Hostel Mess Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)