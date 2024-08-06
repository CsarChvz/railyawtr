from enum import Enum

class Tags(Enum):
    USERS = "Users"
    PROMPTS = "Prompts"
    QUESTIONS = "Questions"
    OPTIONS = "Options"
    THREADS = "Threads"
    FEEDBACK = "Feedback"
    NOTIFICATION = "Notification"
    CONTACTS = "Contacts"
    EMAIL = "Email"
    INVESTORS = "Investors"


tags_metadata = [
    {
        "name": Tags.USERS.value,
        "description": "Operations related to users of the system.",
    },
    {
        "name": Tags.THREADS.value,
        "description": "Endpoint related to the threads"
    },
    {"name": Tags.PROMPTS.value, "description": "Endpoints related to user prompts."},
    {
        "name": Tags.QUESTIONS.value,
        "description": "Administrative endpoints for managing questions.",
    },
    {
        "name": Tags.OPTIONS.value,
        "description": "Endpoints for managing various configurable options.",
    },
    {
        "name": Tags.FEEDBACK.value,
        "description": "Endpoints for managing feedback",
    },
    {
        "name": Tags.NOTIFICATION.value,
        "description": "Endpoints for managing notifications",
    },
    {
        "name": Tags.CONTACTS.value,
        "description": "Endpoints for contacts of the users",
    },
    {
        "name": Tags.EMAIL.value,
        "description": "Endpoints for email actions",
    },
    {
        "name": Tags.INVESTORS.value,
        "description": "Endpoints for investors",
    },
    
]
