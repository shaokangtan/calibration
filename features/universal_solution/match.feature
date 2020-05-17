Feature: Get Video

    Scenario Outline: Check out vudu image library on match
    Given I have an image "<image>"
    When I match "<template>" at "<region>"
    Then I can find the "<template>"" at "<location>"

    Examples:
      | image | region | template | location |
      | pages/Samsung/play_page_1.png | 0, 500, 1280, 720 | templates/Roku/playerBackUnHi.png | 60, 600, 120, 700 |

