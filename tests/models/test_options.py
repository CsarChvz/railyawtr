from sqlalchemy import String, Integer


def test_model_structure_option_table_exists(db_inspector):
    assert db_inspector.has_table("options")


def test_model_structure_option_column_data_types(db_inspector):
    table = "options"
    columns = {col["name"]: col for col in db_inspector.get_columns(table)}

    assert isinstance(columns["id"]["type"], Integer)  # id es Int
    assert isinstance(columns["question_id"]["type"], Integer)  # question_id también es Int
    assert isinstance(columns["option_text"]["type"], String)  # option_text es String


def test_model_structure_option_nullable_constraints(db_inspector):
    option_columns = db_inspector.get_columns("options")

    expected_nullable = {
        "id": False,
        "question_id": True,
        "option_text": True,
    }

    for column in option_columns:
        column_name = column["name"]
        assert (
            column["nullable"] == expected_nullable.get(column_name)
        ), f"Error en columna '{column_name}': se esperaba nullable={expected_nullable[column_name]}, encontrado={column['nullable']}"


def test_model_structure_option_foreign_key(db_inspector):
    option_foreign_keys = db_inspector.get_foreign_keys("options")
    assert any(
        set(fk["constrained_columns"]) == {"question_id"} for fk in option_foreign_keys
    ), "La clave foránea 'question_id' no está definida correctamente en la tabla 'options'."
