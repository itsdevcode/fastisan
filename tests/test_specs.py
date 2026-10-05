import pytest
from fastisan.specs import parse_fields, FieldSpec

def test_parse_valid_fields():
    fields = parse_fields("name:str, email:str, age:int?")
    
    assert len(fields) == 3
    assert fields[0] == FieldSpec("name", "str", False)
    assert fields[1] == FieldSpec("email", "str", False)
    assert fields[2] == FieldSpec("age", "int", True)

def test_parse_empty_fields():
    assert parse_fields("") == ()
    assert parse_fields("   ") == ()

def test_parse_invalid_empty_segment():
    with pytest.raises(ValueError, match="Malformed empty field segment"):
        parse_fields("name:str,,age:int")

def test_parse_missing_colon():
    with pytest.raises(ValueError, match="Missing colon"):
        parse_fields("name")

def test_parse_missing_name():
    with pytest.raises(ValueError, match="Missing field name"):
        parse_fields(":str")

def test_parse_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported field type: decimal"):
        parse_fields("price:decimal")

def test_parse_duplicate_name():
    with pytest.raises(ValueError, match="Duplicate field name: name"):
        parse_fields("name:str, name:int")

def test_parse_reserved_name():
    with pytest.raises(ValueError, match="Field name is reserved: id"):
        parse_fields("id:int")
    
    with pytest.raises(ValueError, match="Field name is reserved: created_at"):
        parse_fields("created_at:datetime")

def test_parse_invalid_identifier():
    with pytest.raises(ValueError, match="Invalid field name: first-name"):
        parse_fields("first-name:str")

    with pytest.raises(ValueError, match="Invalid field name: 1name"):
        parse_fields("1name:str")

def test_parse_keyword_name():
    with pytest.raises(ValueError, match="Invalid field name \\(Python keyword\\): class"):
        parse_fields("class:str")
