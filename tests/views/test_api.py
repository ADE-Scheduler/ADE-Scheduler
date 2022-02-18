from flask import session, url_for


def test_get_events(client, manager):
    """
    Test the get_events API route
    There are 4 options to test:
        - View
        - Year
        - Code
        - Filtered events
    """
    # Test if the JSON API works; the rest is easier to test using the
    # non-json API. Thus, this is the only test where view=False
    params = dict(code="ELME2M", view=False)
    rv = client.get(url_for("api.get_events"), query_string=params)

    assert rv.status_code == 200
    assert isinstance(rv.json.get("events"), list)

    # By default, view = False. This is just to ensure if correctly defaults
    # whenever view is unspecified.
    params = dict(code="ELME2M")
    rv = client.get(url_for("api.get_events"), query_string=params)

    assert rv.status_code == 200
    assert isinstance(rv.json.get("events"), list)

    # Test the "year" param
    for item in manager.get_project_ids():
        project_id, year = item.values()

        params = dict(code="ELME2M", year=year, view=True)
        rv = client.get(
            url_for("api.get_events"), query_string=params, follow_redirects=True
        )

        assert rv.status_code == 200
        assert session["current_schedule"].project_id == project_id

    # Test if the "year" param defaults correctly when not specified
    params = dict(code="ELME2M", view=True)
    rv = client.get(
        url_for("api.get_events"), query_string=params, follow_redirects=True
    )

    assert rv.status_code == 200
    assert session["current_schedule"].project_id == manager.get_default_project_id()

    # Test the "code" param
    params = dict(code="ELME2M", view=True)
    rv = client.get(
        url_for("api.get_events"), query_string=params, follow_redirects=True
    )

    assert rv.status_code == 200
    assert session["current_schedule"].codes == [params["code"]]

    params = dict(code=["LMECA2170", "LELEC2570"], view=True)
    rv = client.get(
        url_for("api.get_events"), query_string=params, follow_redirects=True
    )

    assert rv.status_code == 200
    assert session["current_schedule"].codes == params["code"]

    # Test the "filtered events" param
    params = dict(code="ELME2M", ELME2M=["subcode1", "subcode2"], view=True)
    rv = client.get(
        url_for("api.get_events"), query_string=params, follow_redirects=True
    )

    assert rv.status_code == 200
    assert session["current_schedule"].filtered_subcodes["ELME2M"] == set(
        params["ELME2M"]
    )
