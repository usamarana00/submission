# FastAPI Firebase Task Manager

This project is a FastAPI application integrated with Google Firestore for task management and OpenAI for task categorization and summarization.

## Setup Instructions

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.11
- Docker (optional, if using Docker)


### Steps to Set Up the Environment

Unzip the file.
assuming that we already are using python 3.11
```bash 
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### Running the app
Execute the following command
```bash
uvicorn main:app --reload
```

# Or

We can use Docker instead of setting up the Environment

Assuming that we already have Docker.

```bash 
Docker ps -a
```
run the above command to see if docker is working. and then Execute the following command.

```bash 
docker build -t fastapi-firebase-app .
```

```bash 
docker run -d -p 8000:8000 --name fastapi-firebase fastapi-firebase-app
```


