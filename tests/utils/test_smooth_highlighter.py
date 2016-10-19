from doksit.utils.highlighters import SmoothHighlighter


def test_get_smooth_api_documentation(documentation):
    smooth = SmoothHighlighter(documentation)
    smooth_doc = smooth.get_api_documentation()

    assert smooth_doc
    assert "\x1b[1m# API" in smooth_doc
    assert "**Note**" not in smooth_doc
    assert "[source](" not in smooth_doc


###############################################################################


def test_modify_link():
    smooth = SmoothHighlighter("blabla")

    original_link = (
        "[source](https://github.com/nait-aul/doksit/blob/master/"
        "test_data/module.py)"
    )
    modified_link = "-> test_data/module.py"

    assert modified_link == smooth._modify_link(original_link)
