def create_query(query, select_section: list, attributes_filters: dict):
    for select_field in select_section:
        query = query.add_columns(select_field)

    for attribute, value in attributes_filters.items():
        query = query.filter(attribute == value)

    return query
