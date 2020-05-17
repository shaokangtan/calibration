Feature: Get Frame

  Scenario Outline: Check out camera server frame capture
    Given I have a camera "<url>"
    When I save a frame as "<file>"
    Then I can verify the frame "<file>" is valid
    Examples:
      | url   | file      |
      | 0.0.0.0:33 | frame.png |
