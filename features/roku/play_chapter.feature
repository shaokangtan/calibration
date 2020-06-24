Feature: play page chapter change

@find_chapter
  Scenario Outline: Check out chapter grid the playback page
    Given I have a camera
    when I have a Roku with "<vudu>" app installed
    #And I select Roku home button
    #When I launch Vudu apps
    #And I navigate to "Free" on the menu page
    #And I navigate to movie poster in the New This Month on the free page
    #And I select a movie poster on the free page
    #And I select "Watch Free" on the detail page
    #Then I can detect video on the playback page
    #And I wait ads to complete on the playback page
    Then I can find chapter on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@change_chapter
  Scenario Outline: Check out close cation on the playback page
    Given I have a camera
    when I have a Roku with "<vudu>" app installed
    #And I select Roku home button
    #When I launch Vudu apps
    #And I navigate to "Free" on the menu page
    #And I navigate to movie poster in the New This Month on the free page
    #And I select a movie poster on the free page
    #And I select "Watch Free" on the detail page
    #Then I can detect video on the playback page
    #And I wait ads to complete on the playback page
    Then I can play chapter "14" on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
