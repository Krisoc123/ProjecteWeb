Feature: Add books to wishlist
  In order to keep track of books I want
  As a user
  I want to add books to my wishlist

  Background: There is a registered user and a book
    Given Exists a user "user1" with password "password"
    And Exists a book with ISBN "1234567890"
      | title         | author          | topic      | publish_date | base_price |
      | Test Book     | Test Author     | Test Topic | 2023-01-01   | 10         |

  Scenario: Add a book to wishlist when logged in
    Given I login as user "user1" with password "password"
    When I visit the book details page for ISBN "1234567890"
    And I add the book to my wishlist
      | priority |
      | 2        |
    Then I can see the book with ISBN "1234567890" in my wishlist
    And Server responds with page containing "Test Book"

  Scenario: Redirect to login when trying to add book to wishlist without being logged in
    Given I'm not logged in
    When I visit the book details page for ISBN "1234567890"
    And I click on "Add to my Wishlist" button
    Then I'm redirected to the login form
