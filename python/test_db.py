from .database import *

def test_basic():
    dropTables(test=True)
    init(test=True)
    username = 'my_test_username'
    link = 'my_test_link'
    settings = {'projectID':9, 'codes':'LINGI2261,LINGI2262'}
    setLink(link, username, settings)

    assert isLoginPresent(username)
    assert isLinkPresent(link)

    link_from_username = getLinkFromUsername(username)
    assert link_from_username == link

    settings_from_link = getSettingsfromLink(link)
    assert settings_from_link == settings

    new_settings = 'my_new_test_settings'
    updateSettingsFromLink(link, new_settings)
    settings_from_link = getSettingsfromLink(link)
    assert settings_from_link == new_settings

    deleteLink(link)
    assert not isLinkPresent(link)