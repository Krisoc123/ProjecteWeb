Feature: Add reviews to books
  In order to share my opinion about books
  As a user
  I want to add reviews to books

  Background: There is a registered user and a book
    Given Exists a user "user1" with password "password"
    And Exists a book with ISBN "1234567890"
      | title         | author          | topic      | publish_date | base_price |
      | Test Book     | Test Author     | Test Topic | 2023-01-01   | 10         |

  Scenario: Add a review when logged in
    Given I login as user "user1" with password "password"
    When I visit the book details page for ISBN "1234567890"
    And I add a review for the book
      | text                     |
      | This is a great book!    |
    Then There are 1 reviews for book with ISBN "1234567890"
    And There is a review with text "This is a great book!" for book with ISBN "1234567890"

  Scenario: Redirect to login when trying to add a review without being logged in
    Given I'm not logged in
    When I visit the book details page for ISBN "1234567890"
    And I click on "Write a Review" button
    Then I'm redirected to the login form
