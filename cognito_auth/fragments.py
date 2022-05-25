# common relay fragment
page_info_fragment = """
    fragment PageInfoFragment on PageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
        __typename
    }
"""


def use_fragment(query, *fragments):
    message = ""
    for f in fragments:
        message += f + "\n"

    return f"{message}" f"{query}"