from sqlalchemy import DateTime, Integer, String


def test_model_structure_prompt_table_exists(db_inspector):
    assert db_inspector.has_table("prompts")

def test_model_structure_prompt_column_data_types(db_inspector):
    table = "prompts"
    columns = {col["name"]: col for col in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)  # El id es UUID
    assert isinstance(columns["created_at"]["type"], DateTime)
    assert isinstance(columns["text"]["type"], String)
    assert isinstance(columns["user_id"]["type"], String)  # user_id es String


def test_model_structure_prompt_nullable_constraints(db_inspector):
    prompt_columns = db_inspector.get_columns("prompts")

    expected_nullable = {
        "id": False,
        "created_at": True,
        "text": True,
        "user_id": True,
    }

    for column in prompt_columns:
        column_name = column["name"]
        assert (
            column["nullable"] == expected_nullable.get(column_name)
        ), f"Error en columna '{column_name}': se esperaba nullable={expected_nullable[column_name]}, encontrado={column['nullable']}"

def test_model_structure_prompt_foreign_key(db_inspector):
    prompt_foreign_keys = db_inspector.get_foreign_keys("prompts")
    assert any(
        set(fk["constrained_columns"]) == {"user_id"} for fk in prompt_foreign_keys
    ), "La clave foránea 'user_id' no está definida correctamente en la tabla 'prompts'."
