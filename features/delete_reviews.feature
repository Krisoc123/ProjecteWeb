Feature: Delete book reviews
  In order to remove my reviews that are no longer relevant
  As a user
  I want to delete reviews I've written

  Background: There is a registered user and a review
    Given Exists a user "user1" with password "password"
    And Exists a user "user2" with password "password"
    And Exists a book with ISBN "1234567890"
      | title         | author          | topic      | publish_date | base_price |
      | Test Book     | Test Author     | Test Topic | 2023-01-01   | 10         |
    And Exists a review for book with ISBN "1234567890" by "user1"
      | text                     |
      | This is a great book!    |

  Scenario: Delete my own review
    Given I login as user "user1" with password "password"
    When I visit the book details page for ISBN "1234567890"
    And I delete the review with text "This is a great book!"
    Then There are 0 reviews for book with ISBN "1234567890"
    And There is no review with text "This is a great book!" for book with ISBN "1234567890"

  Scenario: Cannot delete another user's review
    Given I login as user "user2" with password "password"
    When I visit the book details page for ISBN "1234567890"
    Then There is no "Delete" link available
