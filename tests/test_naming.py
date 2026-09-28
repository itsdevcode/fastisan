from fastisan.utils.naming import to_snake_case, to_table_name


def test_to_snake_case() -> None:
    assert to_snake_case("User") == "user"
    assert to_snake_case("BlogPost") == "blog_post"


def test_to_table_name() -> None:
    assert to_table_name("User") == "users"
    assert to_table_name("BlogPost") == "blog_posts"
    assert to_table_name("Category") == "categories"
    assert to_table_name("Person") == "people"