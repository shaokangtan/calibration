Feature: Get Video

  Scenario Outline: Check out camera server video capture
    Given I have a camera "<url>"
    When I start the video on port "<port>"
    Then I can verify the video on port "<port>" is valid
    And I stop the video
    Examples:
      | url    | port |
      | 0.0.0.0:33 | 1000 |
