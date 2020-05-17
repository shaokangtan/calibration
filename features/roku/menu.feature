Feature: menu

@spotlight
  Scenario Outline: Check out menu page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    Then I can verify "Spotlight" selection on menu page
    And I can verify all navigation bar tabs visible on menu page
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
    And I select "KEY_LEFT" button
    Then I can verify "My Vudu" selection on menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@free
  Scenario Outline: Move to Free page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I select "KEY_RIGHT" button
    Then I can verify "Free" selection on menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@movie
  Scenario Outline: Move to Movies page
    Given I have a camera "<url>"
    And I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I go to home page
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    Then I can verify "Movies" selection on menu page
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
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    Then I can verify "TV" selection on menu page
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
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    Then I can verify "Search" selection on menu page
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
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    And I select "KEY_RIGHT" button
    Then I can verify "Settings" selection on menu page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
