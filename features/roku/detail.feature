Feature: detail page

@rent_buy
  Scenario Outline: Check out rent and buy on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rent / Buy" on the detail page
    Then I can detect title on the purchase page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@watch_trailer
  Scenario Outline: Check out watch trailer on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I select "Watch Trailer" on the detail page
    Then I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |


@watch_free
  Scenario Outline: Check out watch free on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select a movie poster on the free page
    And I select "Watch Free" on the detail page
    Then I can detect video on the playback page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@add_to_list
  Scenario Outline: Check out add to list on the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Free" on the menu page
    And I navigate to movie poster in the New This Month on the free page
    And I select a movie poster on the free page
    And I select "Add to List" on the detail page
    Then I can detect title on the add to list page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |

@rate
  Scenario Outline: Check out chapter grid the detail page
    Given I have a camera "<url>"
    when I have a Roku "<roku_url>" with "<vudu>" app installed
    And I select Roku home button
    When I launch Vudu apps
    And I navigate to "Movies" on the menu page
    And I navigate to movie poster on the movie page
    And I select a movie poster on the movie page
    And I save title on the detail page
    And I select "Rate" on the detail page
    Then I can detect title on the rate page
    Examples:
      | url   | roku_url  | vudu |
      | 0.0.0.0:33 | 192.168.8.32:8060 | VUDU |
