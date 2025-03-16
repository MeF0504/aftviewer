# test functions in wikiutil/


def test_api_doc():
    from wikiutil import print_api_doc
    print_api_doc.show_items(print_api_doc.varis)
    print_api_doc.show_items(print_api_doc.types)
    print_api_doc.show_items(print_api_doc.funcs)


def test_options():
    from wikiutil import print_options


def test_intro():
    try:
        from wikiutil import print_intro
    except AssertionError:
        # assert error is acceptable.
        pass
