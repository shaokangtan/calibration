Feature: menu page navigation

@i_am_already_on_menu
  Scenario Outline: Check out I am already on the menu page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I am already on the home menu page
    Then I can verify "Spotlight" selection on the menu page
    Examples:
        | url   | roku_url  | vudu |
        | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@spotlight
  Scenario Outline: Check out the menu page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    Then I can verify "Spotlight" selection on the menu page
    And I can verify all navigation bar tabs visible on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@my_vudu
 Scenario Outline: Move to My Vudu page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I navigate to "My Vudu" on the menu page
    Then I can verify "My Vudu" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@free
  Scenario Outline: Move to free page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I select "KEY_RIGHT" button
    Then I can verify "Free" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@movies
  Scenario Outline: Move to Movies page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I navigate to "Movies" on the menu page
    Then I can verify "Movies" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@tv
   Scenario Outline: Move to TV page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I navigate to "TV" on the menu page
    Then I can verify "TV" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@search
  Scenario Outline: Move to Search page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I navigate to "Search" on the menu page
    Then I can verify "Search" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@settings
  Scenario Outline: Move to Settings page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I navigate to "Settings" on the menu page
    Then I can verify "Settings" selection on the menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
