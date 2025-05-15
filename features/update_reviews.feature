Feature: Update book reviews
  In order to correct or improve my reviews
  As a user
  I want to update reviews I've written

  Background: There is a registered user and a review
    Given Exists a user "user1" with password "password"
    And Exists a user "user2" with password "password"
    And Exists a book with ISBN "1234567890"
      | title         | author          | topic      | publish_date | base_price |
      | Test Book     | Test Author     | Test Topic | 2023-01-01   | 10         |
    And Exists a review for book with ISBN "1234567890" by "user1"
      | text                     |
      | This is a great book!    |

  Scenario: Update my own review
    Given I login as user "user1" with password "password"
    When I visit the book details page for ISBN "1234567890"
    And I edit the review with text "This is a great book!"
      | text                     |
      | This book is amazing!    |
    Then There are 1 reviews for book with ISBN "1234567890"
    And There is a review with text "This book is amazing!" for book with ISBN "1234567890"
    And There is no review with text "This is a great book!" for book with ISBN "1234567890"

  Scenario: Cannot edit another user's review
    Given I login as user "user2" with password "password"
    When I visit the book details page for ISBN "1234567890"
    Then There is no "Edit" link available
