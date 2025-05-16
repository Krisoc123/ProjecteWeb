Feature: User Profile
  In order to manage my account and activities
  As a user
  I want to view and edit my profile information

  Background: There is a registered user with books in lists
    Given Exists a user "user1" with password "password"
    And Exists a book with ISBN "1234567890"
      | title          | author          | topic      | publish_date | base_price |
      | Test Book      | Test Author     | Test Topic | 2023-01-01   | 10         |
    And Exists a book with ISBN "0987654321"
      | title          | author           | topic        | publish_date | base_price |
      | Another Book   | Another Author   | Another Topic| 2023-02-01   | 15         |
    And Exists a book in havelist with ISBN "1234567890" by "user1"
      | status |
      | used   |
    And Exists a book in wishlist with ISBN "0987654321" by "user1"
      | priority |
      | 3        |

  Scenario: View profile page when logged in
    Given I login as user "user1" with password "password"
    When I visit the profile page
    Then Server responds with page containing "user1's Profile"
    And Server responds with page containing "Books You Have"
    And Server responds with page containing "Books You Want"
    And I can see the book with title "Test Book" in my havelist
    And I can see the book with title "Another Book" in my wishlist

  Scenario: Redirect to login when trying to access profile without being logged in
    Given I'm not logged in
    When I visit the profile page
    Then I'm redirected to the login form

  Scenario: Update profile picture
    Given I login as user "user1" with password "password"
    When I visit the profile page
    Then I can see the profile picture upload option

  Scenario: Delete books from lists
    Given I login as user "user1" with password "password"
    When I visit the profile page
    Then I can see delete buttons for books in my lists
