class Category:
    name: str
    description: str
    list_product: list
    category_count = 0
    product_count = 0

    def __init__(self, name, description, list_product):
        self.name = name
        self.description = description
        self.list_product = list_product
        Category.category_count += 1
        Category.product_count += len(list_product)
