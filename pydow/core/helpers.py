def h(element_type: str, element_props: dict, *element_children: list) -> dict:
    """ Method to create an element in the virtual DOM (representation of a DOM object).
    """

    return {
        "type": element_type,
        "props": element_props,
        "children": [child for child in element_children if child is not None],
    }
