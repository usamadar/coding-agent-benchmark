class ItemStore:
    def __init__(self, items=None):
        self.items = list(items) if items else []

    def add_item(self, item):
        self.items.append(item)

    def get_items(self):
        return list(self.items)

    def get_item_count(self):
        return len(self.items)

    # TODO: Add get_page(page, per_page) method

    # TODO: Add search(query, page, per_page) method
