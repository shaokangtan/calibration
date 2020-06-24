Feature: settings page

  Scenario Outline: Check out the settings page
    Given I have a camera
    And I have a Roku with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Settings" on the menu page
    Then I can verify "Settings" selection on the menu page
    When I select "KEY_DOWN" button
    And  I wait "3" seconds
    And  I save a frame as "my_account.png"
    Then I can verify "My Account" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "family_settings.png"
    Then I can verify "Family Settings" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "closed_captioning.png"
    Then I can verify "Closed Captioning" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "playback_quality.png"
    Then I can verify "Playback Quality" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "autoplay_settings.png"
    Then I can verify "Autoplay Settings" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "accessibility.png"
    Then I can verify "Accessibility" selection on the settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "about.png"
    Then I can verify "About" selection on the settings page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
