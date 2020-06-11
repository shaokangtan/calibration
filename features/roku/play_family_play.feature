Feature: play page family play

@family_play
  Scenario Outline: Check out family play on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    #And I select Roku home button
    #When I launch Vudu apps
    #And I navigate to "Free" on the menu page
    #And I navigate to movie poster in the New This Month on the free page
    #And I select a movie poster on the free page
    #And I select "Watch Free" on the detail page
    #Then I can detect video on the playback page
    #And I wait ads to complete on the playback page
    And I can find family play button on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@family_play_on
  Scenario Outline: Check out close cation on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    #And I select Roku home button
    #When I launch Vudu apps
    #And I navigate to "Free" on the menu page
    #And I navigate to movie poster in the New This Month on the free page
    #And I select a movie poster on the free page
    #And I select "Watch Free" on the detail page
    #Then I can detect video on the playback page
    #And I wait ads to complete on the playback page
    And I can turn "on" family play on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@family_play_off
  Scenario Outline: Check out close cation on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    #And I select Roku home button
    #When I launch Vudu apps
    #And I navigate to "Free" on the menu page
    #And I navigate to movie poster in the New This Month on the free page
    #And I select a movie poster on the free page
    #And I select "Watch Free" on the detail page
    #Then I can detect video on the playback page
    #And I wait ads to complete on the playback page
    And I can turn "off" family play on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
