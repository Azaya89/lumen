import pytest

from lumen.target import Download, Facet, Target
from lumen.validation import ValidationError


@pytest.mark.parametrize(
    "spec,msg",
    (
        (
            {"by": ["model"], "layout": "column"},
            None,
        ),
        (
            {"bys": ["model"], "layout": "column"},
            "Facet component specification contained unknown key",
        ),
        (
            {"layout": "column"},
            "The Facet component requires 'by' parameter to be defined",
        ),
        (
            {"by": "model", "layout": "column"},
            "Facet component 'by' key expected list type but got str",
        ),
    ),
    ids=["correct", "unknown_key", "missing_required", "wrong_type"]
)
def test_target_facet(spec, msg):
    if msg is None:
        Facet.validate(spec)

    else:
        with pytest.raises(ValidationError, match=msg):
            Facet.validate(spec)


@pytest.mark.parametrize(
    "spec,msg",
    (
        (
            "csv",
            None,
        ),
        (
            {'format': 'csv'},
            None,
        ),
        (
            {'formats': 'csv'},
            "The Download component requires 'format' parameter to be defined",
        ),
        (
            {'format': 'csvs'},
            "Download component 'format' value failed validation: csvs",
        )
    ),
    ids=["correct1", "correct2", "missing_required", "wrong_format"]
)
def test_target_download(spec, msg):
    if msg is None:
        Download.validate(spec)

    else:
        with pytest.raises(ValidationError, match=msg):
            Download.validate(spec)


@pytest.mark.parametrize(
    "spec,msg",
    (
        (
            {'title': 'Table', 'source': 'penguins', 'views': []},
            None,
        ),
        (
            {'title': 'Table', 'source': 'penguin', 'views': []},
            "Target specified non-existent source 'penguin'",
        ),
        (
            {'title': 'Table', 'source': 'penguins'},
            "The Target component requires 'views' parameter to be defined",
        ),
        (
            {'source': 'penguins', 'views': []},
            "The Target component requires 'title' parameter to be defined",
        ),
        (
            {'title': 'Table', 'views': []},
            "Target component requires one of 'pipeline' or 'source' to be defined",
        ),
    ),
    ids=["correct", "missing_source", "missing_views", "missing_title", "missing_pipeline_or_source"]
)
def test_target_target(spec, msg):
    context = {
        'sources': {'penguins': {}},
        'targets': [],
    }

    if msg is None:
        Target.validate(spec, context)

    else:
        with pytest.raises(ValidationError, match=msg):
            Target.validate(spec, context)
