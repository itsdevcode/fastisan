from fastisan.utils.naming import to_snake_case


def test_to_snake_case() -> None:
    """Test snake case conversion."""
    assert to_snake_case("User") == "user"
    assert to_snake_case("BlogPost") == "blog_post"
    assert to_snake_case("OrderItem") == "order_item"