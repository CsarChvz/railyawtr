from sqlalchemy import DateTime, Integer, String


def test_model_structure_user_response_table_exists(db_inspector):
    assert db_inspector.has_table('user_responses')

def test_model_structure_user_response_column_data_types(db_inspector):
    table = 'user_responses'
    columns = {col['name']: col for col in db_inspector.get_columns(table)}

    assert isinstance(columns['id']['type'], Integer)  # El id es UUID
    assert isinstance(columns['question_id']['type'], Integer)  # question_id es UUID
    assert isinstance(columns['user_id']['type'], String)  # user_id es String
    assert isinstance(
        columns['selected_option_id']['type'], Integer
    )  # selected_option_id es UUID
    assert isinstance(columns['created_at']['type'], DateTime)

def test_model_structure_user_response_nullable_constraints(db_inspector):
    user_response_columns = db_inspector.get_columns('user_responses')

    expected_nullable = {
        'id': False,
        'question_id': True,
        'user_id': True,
        'selected_option_id': True,
        'created_at': True,
    }

    for column in user_response_columns:
        column_name = column['name']
        assert (
            column['nullable'] == expected_nullable.get(column_name)
        ), f'Error en columna '{column_name}': se esperaba nullable={expected_nullable[column_name]}, encontrado={column['nullable']}'

def test_model_structure_user_response_foreign_key(db_inspector):
    user_response_foreign_keys = db_inspector.get_foreign_keys('user_responses')
    assert any(
        set(fk['constrained_columns']) == {'question_id'}
        for fk in user_response_foreign_keys
    ), 'La clave foránea 'question_id' no está definida correctamente en la tabla 'user_responses'.'
    assert any(
        set(fk['constrained_columns']) == {'user_id'}
        for fk in user_response_foreign_keys
    ), 'La clave foránea 'user_id' no está definida correctamente en la tabla 'user_responses'.'
    assert any(
        set(fk['constrained_columns']) == {'selected_option_id'}
        for fk in user_response_foreign_keys
    ), 'La clave foránea 'selected_option_id' no está definida correctamente en la tabla 'user_responses'.'
