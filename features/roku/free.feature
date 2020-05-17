Feature: menu

  Scenario Outline: Check out menu page
    Given I have a camera "<url>"
    Given I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I select "KEY_RIGHT" button
    And I select "KEY_DOWN" button
    And I select "KEY_DOWN" button
    And I select "KEY_DOWN" button
    And I select "KEY_DOWN" button
    And I select "KEY_SELECT" button
    And I select "KEY_SELECT" button
    Then I can verify all navigation bar tabs visible
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
