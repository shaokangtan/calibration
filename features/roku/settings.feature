Feature: menu

  Scenario Outline: Check out menu page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And  I save a frame as "settings.png"
    Then I can verify "Settings" selection on menu page
    When I select "KEY_DOWN" button
    And  I wait "3" seconds
    And  I save a frame as "my_account.png"
    Then I can verify "My Account" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "family_settings.png"
    Then I can verify "Family Settings" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "closed_captioning.png"
    Then I can verify "Closed Captioning" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "playback_quality.png"
    Then I can verify "Playback Quality" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "autoplay_settings.png"
    Then I can verify "Autoplay Settings" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "accessibility.png"
    Then I can verify "Accessibility" selection on settings page
    When I select "KEY_DOWN" button
    And  I save a frame as "about.png"
    Then I can verify "About" selection on settings page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
