Feature: trailer playback

  Scenario Outline: Check out the menu page
    Given I have a camera "<url>"
    Given I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select a movie poster on the free page
    And I select "Watch Trailer" on the detail page
    Then I can detect video on the playback page
    And I can read play time and program time on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
