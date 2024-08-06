import datetime
from itertools import count

from faker import Faker

faker = Faker()

id_counter = count(start=1)


def get_random_user_dict(id_: str = None):
    id_ = id_ or f"USR{next(id_counter)}"
    # Generar la fecha de nacimiento solo con la fecha, sin hora
    birthday_date = faker.date_of_birth()
    birthday_str = (
        birthday_date.isoformat()
        if isinstance(birthday_date, datetime.datetime)
        else f"{birthday_date}T00:00:00"
    )

    return {
        "id": id_,
        "interactions_count": 0,  # Initial interactions count is 0
        "name": faker.name(),
        "username": faker.user_name(),
        "birthday": birthday_str,
        "gender": faker.random_element(elements=("Male", "Female", "Non-binary")),
        "bio": faker.text(max_nb_chars=200),
        "profile_picture": faker.image_url(),
        "location": faker.city(),
        "email": faker.email(),
        "verified": faker.boolean(),
        "school_num_handles": faker.word(),
        "phone_number": faker.phone_number(),
        "password_hashed": faker.password(length=12),
        "providers": faker.word(),
        "created_at": faker.date_time_this_year().isoformat(),  # Convertir a string en formato ISO
        "updated_at": faker.date_time_this_year().isoformat(),  # Convertir a string en formato ISO
    }


def get_random_prompt_dict(user_id: str):
    id_ = next(id_counter)
    return {
        "id": id_,
        "created_at": faker.date_time_this_year().isoformat(),
        "text": faker.sentence(),
        "user_id": user_id,
    }


def get_random_question_dict(prompt_id: int, user_id: str):
    id_ = next(id_counter)
    return {
        "id": id_,
        "created_at": faker.date_time_this_year().isoformat(),
        "prompt_id": prompt_id,
        "user_id": user_id,
        "question_text": faker.sentence(),
    }


def get_random_option_dict(question_id: int):
    id_ = next(id_counter)
    return {
        "id": id_,
        "question_id": question_id,
        "option_text": faker.sentence(),
    }

def get_random_user_response_dict(question_id: int, user_id: str, selected_option_id: int):
    id_ = next(id_counter)
    return {
        "id": id_,
        "question_id": question_id,
        "user_id": user_id,
        "selected_option_id": selected_option_id,
        "created_at": faker.date_time_this_year().isoformat(),
    }
