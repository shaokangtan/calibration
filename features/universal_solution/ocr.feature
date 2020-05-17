Feature: match

  Scenario Outline: Check out vudu image library on OCR
    Given I have an image "<image>"
    When I OCR "<image>" at "<region>"
    Then I can find the text "<text>"

    Examples:
      | image | region | text |
      | pages/Samsung/play_page_1.png | 20, 20, 292, 84 | A Star Is Born |
