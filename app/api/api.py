from fastapi import APIRouter

from app.tags import Tags

from app.api import (
    contacts_routes,
    options_routes,  
    prompts_routes, 
    questions_routes, 
    user_routes, 
    feedback_routes,
    notification_routes,
    email_routes,
    investor_routes,
    user_assignment_routes
)
router = APIRouter()

router.include_router(user_routes.user_router, prefix="/user", tags=[Tags.USERS.value])
router.include_router(prompts_routes.prompts_router, prefix="/prompts", tags=[Tags.PROMPTS.value])
router.include_router(
    questions_routes.questions_router, prefix="/questions", tags=[Tags.QUESTIONS.value]
)
router.include_router(options_routes.options_router, prefix="/options", tags=[Tags.OPTIONS.value])
router.include_router(feedback_routes.feedback_router, prefix="/feedback", tags=[Tags.FEEDBACK.value])
router.include_router(notification_routes.notification_router, prefix="/notifications",  tags=[Tags.NOTIFICATION.value])
router.include_router(contacts_routes.contacts_router, prefix="/contacts",  tags=[Tags.CONTACTS.value])
router.include_router(email_routes.email_router, prefix="/email", tags=[Tags.EMAIL.value])
router.include_router(investor_routes.investor_interest_router, prefix="/investors", tags=[Tags.INVESTORS.value])
router.include_router(user_assignment_routes.user_assignment_router, prefix="/assignments")
