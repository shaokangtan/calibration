Feature: serch page

@search_verify
  Scenario Outline: Check out search on the search page
    Given I have a camera
    when I have a Roku with "<vudu>" app installed
    And I select Roku home button
    And I launch Vudu apps
    When I navigate to "Search" on the menu page
    And I select "KEY_SELECT" button
    And I enter search "PANDA" on the search page
    Then I can verify search "PANDA" on the search page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@suggestion_verify
  Scenario Outline: Check out suggestion on the search page
    Given I have a camera
    when I have a Roku with "<vudu>" app installed
    And I select Roku home button
    And I launch Vudu apps
    When I navigate to "Search" on the menu page
    And I select "KEY_SELECT" button
    And I enter search "PANDA" on the search page
    Then I can verify suggestion "PANDA" on the search page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@search_verify_play
  Scenario Outline: Check out search on the search page
    Given I have a camera
    when I have a Roku with "<vudu>" app installed
    And I select Roku home button
    And I launch Vudu apps
    When I navigate to "Search" on the menu page
    And I select "KEY_SELECT" button
    And I enter search "PANDA" on the search page
    Then I can verify search "PANDA" on the search page
    When I select a movie poster on the search page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

