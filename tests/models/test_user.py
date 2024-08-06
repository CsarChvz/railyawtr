from sqlalchemy import Boolean, Date, DateTime, Integer, String


def test_model_structure_user_table_exists(db_inspector):
    assert db_inspector.has_table("users")


def test_model_structure_user_column_data_types(db_inspector):
    table = "users"
    columns = {col["name"]: col for col in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], String)  # El id es String
    assert isinstance(columns["name"]["type"], String)
    assert isinstance(columns["username"]["type"], String)
    assert isinstance(columns["birthday"]["type"], Date)
    assert isinstance(columns["gender"]["type"], String)
    assert isinstance(columns["bio"]["type"], String)
    assert isinstance(columns["profile_picture"]["type"], String)
    assert isinstance(columns["location"]["type"], String)
    assert isinstance(columns["email"]["type"], String)
    assert isinstance(columns["verified"]["type"], Boolean)
    assert isinstance(columns["school_num_handles"]["type"], String)
    assert isinstance(columns["phone_number"]["type"], String)
    assert isinstance(columns["password_hashed"]["type"], String)
    assert isinstance(columns["providers"]["type"], String)
    assert isinstance(columns["created_at"]["type"], DateTime)
    assert isinstance(columns["updated_at"]["type"], DateTime)
    assert isinstance(
        columns["interactions_count"]["type"], Integer
    )  # Añadido para el contador de interacciones


def test_model_structure_user_nullable_constraints(db_inspector):
    user_columns = db_inspector.get_columns("users")

    expected_nullable = {
        "id": False,
        "name": True,
        "username": True,
        "birthday": True,
        "gender": True,
        "bio": True,
        "profile_picture": True,
        "location": True,
        "email": True,
        "verified": True,
        "school_num_handles": True,
        "phone_number": True,
        "password_hashed": True,
        "providers": True,
        "created_at": True,
        "updated_at": True,
        "interactions_count": True,
    }

    for column in user_columns:
        column_name = column["name"]
        assert (
            column["nullable"] == expected_nullable.get(column_name)
        ), f"Error en columna '{column_name}': se esperaba nullable={expected_nullable[column_name]}, encontrado={column['nullable']}"


def test_model_structure_user_foreign_key(db_inspector):
    # Asegúrate de que no hay FK innecesarias en la tabla 'users'.
    user_foreign_keys = db_inspector.get_foreign_keys("users")
    assert (
        len(user_foreign_keys) == 0
    ), "Se encontraron claves foráneas innecesarias en la tabla 'users'."
