from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI
from datetime import datetime
import json
#initialization 
cred = credentials.Certificate("smart-task-manager-71234-firebase-adminsdk-8vhe4-0dcccbaf64.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
# OpenAI API key
with open("config.json", "r") as f:
    config = json.load(f)
api_key = config.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found in config file.")
client = OpenAI(api_key=api_key)
# Initialize FastAPI app and Firestore client
app = FastAPI()


# Function to fetch all tasks from Firestore
def get_all_tasks():
    """
    Fetch all tasks from the Firestore 'tasks' collection.
    """
    try:
        tasks = []
        docs = db.collection("tasks").stream()
        for doc in docs:
            task = doc.to_dict()
            task["id"] = doc.id  # Add the document ID to the task
            tasks.append(task)
        return tasks
    except Exception as e:
        raise Exception(f"Error retrieving tasks: {str(e)}")

# Task 1: Retrieve all tasks
@app.get("/tasks")
def fetch_all_tasks():
    """
    Retrieve a list of all tasks stored in Firestore.
    """
    try:
        tasks = get_all_tasks()
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Task 2: Create a new task
def save_task_to_firestore(title: str, description: str, category: str):
    """
    Save a new task to Firestore and return the saved task data.
    """
    try:
        task_data = {
            "title": title,
            "description": description,
            "category": category,
            "summary": "",
            "created_at": datetime.utcnow().isoformat()  # Use UTC for consistency
        }
        task_ref = db.collection("tasks").document()  # Firestore generates a unique ID
        task_data["id"] = task_ref.id  # Add Firestore document ID
        task_ref.set(task_data)
        return task_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save task to Firestore: {str(e)}")


def categorize_task_with_openai(title: str, description: str):
    """
    Use OpenAI API to categorize the task based on its title and description.
    """
    try:
        # Define the prompt and API call using ChatCompletion
        prompt = f"Categorize the following task based on its title and description and write only the category name:Title = {title}\nDescription = {description} "
   
        response =client.chat.completions.create(
            model="gpt-4o-mini",  # Use the correct model
            messages=[
                {"role": "system", "content": "You are an AI that categorizes tasks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,  # Limit response length
            temperature=0  # Keep responses deterministic
        )
        # Extract the category from the response
        category = response.choices[0].message.content
        print(category)
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI categorization failed: {str(e)}")

@app.post("/tasks")
def create_task(request: dict):
    """
    Create a new task with AI-based categorization.
    """
    try:
        # Parse request body
        title = request.get("title")
        description = request.get("description")
        
        # Validate required fields
        if not title or not description:
            raise HTTPException(status_code=400, detail="Both 'title' and 'description' are required.")
        
        # Categorize the task using OpenAI
        category = categorize_task_with_openai(title, description)
        
        # Save the task to Firestore
        task_data = save_task_to_firestore(title, description, category)
        
        # Return the created task
        return {"task": task_data}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Task 3: Retrieve a specific task
@app.get("/tasks/{task_id}")
def fetch_task(task_id: str):
    try:
        task_ref = db.collection("tasks").document(task_id)
        doc = task_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")
        task = doc.to_dict()
        task["id"] = doc.id
        return {"task": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve task: {str(e)}")

# Task 4: Summarize a specific task
@app.post("/tasks/{task_id}/summarize")
def summarize_task(task_id: str):
    """
    Generate a summary for a task's description and update it in Firestore.
    """
    try:
        task_ref = db.collection("tasks").document(task_id)
        doc = task_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")
        
        task = doc.to_dict()
        task["id"] = doc.id  # Include the document ID

        description = task.get("description")
        if not description:
            raise HTTPException(status_code=400, detail="Task description is required to generate a summary.")
        
        # Generate summary using OpenAI
        prompt = f"Summarize the following task description:\n\n{description}\nSummary:"
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the correct model
            messages=[
                {"role": "system", "content": "You are an AI that summarizes description."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0
        )
        summary = response.choices[0].message.content
        
        # Update Firestore and task object
        task_ref.update({"summary": summary})
        task["summary"] = summary  # Include updated summary in response

        return {"task": task}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
