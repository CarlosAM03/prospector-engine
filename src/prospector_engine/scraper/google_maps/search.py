from prospector_engine.engines.navigation import NavigationEngine

from prospector_engine.models.search_query import SearchQuery


def create_search_page(
    browser,
    query: SearchQuery,
    page_factory=None,
):

    navigation = NavigationEngine(
        browser=browser,
        source=query.source,
        page_factory=page_factory,
    )

    page = navigation.open()

    search_text = (
        f"{query.keyword} {query.location}"
    )

    navigation.search(
        page=page,
        query=search_text,
    )

    return page
