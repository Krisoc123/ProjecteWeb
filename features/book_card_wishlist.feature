Feature: Add books to wishlist from book card
  In order to quickly add books to my wishlist
  As a user
  I want to click on the wishlist icon directly from book cards in the book listing

  Background: There are registered users and books in the database
    Given Exists a user "user1" with password "password"
    And Exists a book with ISBN "1234567890"
      | title         | author          | topic      | publish_date | base_price |
      | Test Book     | Test Author     | Test Topic | 2023-01-01   | 10         |
    And Exists a book with ISBN "9876543210"
      | title           | author            | topic      | publish_date | base_price |
      | Another Book    | Another Author    | Novel·la   | 2023-02-15   | 15         |

  Scenario: Add a book to wishlist by clicking the heart icon when logged in
    Given I login as user "user1" with password "password"
    When I visit the books page
    And I click on the wishlist icon for "Test Book"
    Then I should be redirected to the wishlist form
    When I submit the wishlist form with
      | priority |
      | 2        |
    Then I can see the book with ISBN "1234567890" in my wishlist

  Scenario: Redirect to login when trying to add book to wishlist without being logged in
    Given I'm not logged in
    When I visit the books page
    And I click on the wishlist icon for "Test Book"
    Then I'm redirected to the login form
