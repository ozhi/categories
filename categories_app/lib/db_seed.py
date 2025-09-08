from categories_app.models import Category


def create_example_categories() -> dict[str, Category]:
    """
    Keep method idempotent because of db seeding -
    do not duplicate categories with same name but different parent, description etc.
    """
    category_defs = [
        {"name": "Tech", "description": "All things tech", "parent": None},
        {"name": "Computers", "description": "Thinking machines", "parent": "Tech"},
        {"name": "Laptops", "parent": "Computers"},
        {"name": "Desktops", "parent": "Computers"},
        {"name": "Audio", "parent": "Tech"},
        {"name": "Headphones", "parent": "Audio"},
        {"name": "Wireless headphones", "parent": "Headphones"},
        {"name": "In-ear wireless headphones", "parent": "Wireless headphones"},
        {"name": "Over-ear wireless headphones", "parent": "Wireless headphones"},
        {"name": "Food", "parent": None},
        {"name": "Fresh produce", "parent": "Food"},
        {"name": "Vegetables", "parent": "Fresh produce"},
        {"name": "Potatoes", "parent": "Vegetables"},
        {"name": "Sweet potatoes", "parent": "Potatoes"},
        {"name": "Books", "parent": None},
    ]

    # Update or create categories without parents.
    categories_map: dict[str, Category] = {}
    for cat_def in category_defs:
        cat, _ = Category.objects.update_or_create(
            name=cat_def["name"],
            defaults={
                "description": cat_def.get("description"),
                "parent": None,
            },
        )
        categories_map[cat_def["name"]] = cat

    # Add parent relationships.
    for cat_def in category_defs:
        parent_name = cat_def.get("parent")
        if parent_name:
            categories_map[cat_def["name"]].parent = categories_map[parent_name]
            categories_map[cat_def["name"]].save()

    # Add similarity relationships
    categories_map["Computers"].similar_to.add(
        categories_map["Laptops"], categories_map["Desktops"]
    )
    categories_map["Laptops"].similar_to.add(categories_map["Desktops"])
    categories_map["Books"].similar_to.add(categories_map["Computers"])
    categories_map["Potatoes"].similar_to.add(categories_map["Sweet potatoes"])

    return categories_map
