Feature: purchase page

@rent_cancel
  Scenario Outline: Check out rent and buy and cancel on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rent / Buy" on the detail page
    Then I can detect the title on the purchase page
    When I rent the "<video_quality>" on the purchase page
    Then I can detect the confirm purchase popup
    When I select "<button>" on the confirm purchase popup
    Then I can detect the title on the purchase page
    Examples:
      | url   | roku_url  | vudu | video_quality | button |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU | SD | cancel |

@rent_watch
  Scenario Outline: Check out rent and buy and watch on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rent / Buy" on the detail page
    Then I can detect the title on the purchase page
    When I rent the "<video_quality>" on the purchase page
    Then I can detect the confirm purchase popup
    When I select "<button>" on the confirm purchase popup
    And I select watch now on the thank you purchase popup
    Then I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu | video_quality | button |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU | HDX | ok |


@buy_cancel
  Scenario Outline: Check out rent and buy and cancel on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rent / Buy" on the detail page
    Then I can detect the title on the purchase page
    When I buy the "<video_quality>" on the purchase page
    Then I can detect the confirm purchase popup
    When I select "<button>" on the confirm purchase popup
    Then I can detect the title on the purchase page
    Examples:
      | url   | roku_url  | vudu | video_quality | button |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU | SD | cancel |

@buy_watch
  Scenario Outline: Check out rent and buy and watch on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rent / Buy" on the detail page
    Then I can detect the title on the purchase page
    When I buy the "<video_quality>" on the purchase page
    Then I can detect the confirm purchase popup
    When I select "<button>" on the confirm purchase popup
    Then I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu | video_quality | button |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU | HDX | ok |
