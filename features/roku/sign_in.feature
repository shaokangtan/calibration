Feature: sign in/out

@sign_out
  Scenario Outline: Check out sign out
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I am already on the home menu page
    When I navigate to "Settings" on the menu page
    And I select "My Account" on the settings page
    And I select "KEY_SELECT" button
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@sign_in
Scenario Outline: Check out sign in
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I am already on the home menu page
    When I navigate to "Settings" on the menu page
    And I select "My Account" on the settings page
    And I select "KEY_SELECT" button
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
