Feature: play page video quality

@find_video_quality
  Scenario Outline: Check out video quality on the playback page
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
    And I can find video quality button on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@change_video_quality_sd
  Scenario Outline: Check out change video quality on the playback page
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
    And I can change video quality to "sd" on the playback progress bar
    And I can find video is playing "sd" on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@change_video_quality_hdx
  Scenario Outline: Check out change video quality on the playback page
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
    And I can change video quality to "hdx" on the playback progress bar
    And I can find video is playing "hdx" on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
