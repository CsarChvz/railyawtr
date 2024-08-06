from sqlalchemy import Integer, DateTime, String


def test_model_structure_question_table_exists(db_inspector):
    assert db_inspector.has_table("questions")

def test_model_structure_question_column_data_types(db_inspector):
    table = "questions"
    columns = {col["name"]: col for col in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)  # id es UUID
    assert isinstance(columns["created_at"]["type"], DateTime)
    assert isinstance(columns["prompt_id"]["type"], Integer)  # prompt_id es UUID
    assert isinstance(columns["user_id"]["type"], String)  # user_id es String
    assert isinstance(columns["question_text"]["type"], String)

def test_model_structure_question_nullable_constraints(db_inspector):
    question_columns = db_inspector.get_columns("questions")

    expected_nullable = {
        "id": False,
        "created_at": True,
        "prompt_id": True,
        "user_id": True,
        "question_text": True,
    }

    for column in question_columns:
        column_name = column["name"]
        assert (
            column["nullable"] == expected_nullable.get(column_name)
        ), f"Error en columna '{column_name}': se esperaba nullable={expected_nullable[column_name]}, encontrado={column['nullable']}"

def test_model_structure_question_foreign_key(db_inspector):
    question_foreign_keys = db_inspector.get_foreign_keys("questions")
    assert any(
        set(fk["constrained_columns"]) == {"prompt_id"} for fk in question_foreign_keys
    ), "La clave foránea 'prompt_id' no está definida correctamente en la tabla 'questions'."
    assert any(
        set(fk["constrained_columns"]) == {"user_id"} for fk in question_foreign_keys
    ), "La clave foránea 'user_id' no está definida correctamente en la tabla 'questions'."
