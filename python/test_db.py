from .database import *

def test_basic():
    dropTables(test=True)
    init(test=True)
    username = 'my_test_username'
    link = 'my_test_link'
    settings = {'project_id':9, 'codes':'LINGI2261,LINGI2262'}
    set_link(link, username, settings)

    assert isLoginPresent(username)
    assert is_link_present(link)

    link_from_username = get_link_from_username(username)
    assert link_from_username == link

    settings_from_link = get_settings_from_link(link)
    assert settings_from_link == settings

    new_settings = 'my_new_test_settings'
    update_settings_from_link(link, new_settings)
    settings_from_link = get_settings_from_link(link)
    assert settings_from_link == new_settings

    delete_link(link)
    assert not is_link_present(link)

def test_username():
    dropTables(test=True)
    init(test=True)
    link = 'my_second_test_link'
    set_link(link)

    assert is_link_present(link)
    assert not isLoginPresent('any_string')

    settings = get_settings_from_link(link)
    assert settings == None