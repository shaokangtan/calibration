Feature: play page

@trigger_mode
  Scenario Outline: Check out trigger modes on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    # play a free movie
    # wait ads to finish
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "1" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I press "KEY_PLAYPAUSE" on the playback page
    And I can read play time and program time on the playback progress bar
    Then I can detect frozen video on the playback page
    When I press "KEY_PLAYPAUSE" on the playback page
    Then I can find play time is the same on the playback progress bar
    And I can detect video on the playback page
    When  I read play time and program time on the playback progress bar
    And I press "KEY_REWIND" on the playback page
    And I wait "5" seconds
    And I press "KEY_PLAYPAUSE" on the playback page
    Then I can find play time is reduced on the playback progress bar
    And I can detect video on the playback page
    When I read play time and program time on the playback progress bar
    And I press "KEY_FASTFORWARD" on the playback page
    And I wait "5" seconds
    And I press "KEY_PLAYPAUSE" on the playback page
    Then I can find play time is increased on the playback progress bar
    And I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@soft_key_back
    Scenario Outline: Check out back soft key on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    ## play a free movie
    ## wait ads to finish
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "2" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I navigate to "back" button on the playback progress bar
    And I read play time and program time on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    # back to detail page
    And I select "Watch" on the detail page
    Then I can find play time is the same on the playback progress bar
    When I exit the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@soft_key_replay
 Scenario Outline: Check out replay soft key on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    ## play a free movie
    ## wait ads to finish
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "3" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I navigate to "replay" button on the playback progress bar
    And I read play time and program time on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    Then I can find play time is reduced on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@soft_key_rewind
 Scenario Outline: Check out rewind soft key on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    ## play a free movie
    ## wait ads to finish
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "4" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I navigate to "rewind" button on the playback progress bar
    And I read play time and program time on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    And I wait "5" seconds
    And I press "KEY_PLAYPAUSE" on the playback page
    Then I can find play time is reduced on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@soft_key_fastforward
 Scenario Outline: Check out fastforward soft key on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "5" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I navigate to "fast forward" button on the playback progress bar
    And I read play time and program time on the playback progress bar
    And I select "KEY_SELECT" button on the playback progress bar
    And I wait "5" seconds
    And I press "KEY_PLAYPAUSE" on the playback page
    Then I can find play time is increased on the playback progress bar
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |



@soft_key_all
 Scenario Outline: Check out all soft key on the playback page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select the movie poster at "6" on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    And I wait ads to complete on the playback page
    When I navigate to "replay" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    When I navigate to "video quality" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    When I navigate to "chapter" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    When I navigate to "rewind" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    When I navigate to "fast forward" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    When I navigate to "closed caption" button on the playback progress bar
    Then I exit the playback page
    And I select "Watch Free" on the detail page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
