Feature: Book Exchange System
  In order to exchange books with other users
  As a logged in user
  I want to be able to trade my books with other users' books

  Background: There are registered users with books in their havelists
    Given Exists a user "user1" with password "password"
    And Exists a user "user2" with password "password"
    And Exists a book with ISBN "1234567890"
      | title      | author         | topic     | publish_date | base_price |
      | Book One   | Author One     | Fiction   | 2023-01-01   | 10         |
    And Exists a book with ISBN "0987654321"
      | title      | author         | topic     | publish_date | base_price |
      | Book Two   | Author Two     | Non-fiction | 2023-02-02 | 15         |
    And Exists a book in havelist with ISBN "1234567890" by "user1"
      | status | points |
      | used   | 10     |
    And Exists a book in havelist with ISBN "0987654321" by "user2"
      | status | points |
      | used   | 15     |

  Scenario: Attempt to exchange books when not logged in
    Given I'm not logged in
    When I try to visit the book trade form for ISBN "1234567890"
    Then I should be redirected to the login page

  Scenario: Exchange with a user who has no books
    Given I login as user "user1" with password "password"
    And Exists a user "user3" with password "password"
    When I visit the book trade form for ISBN "1234567890"
    And I select user "user3" to trade with
    And I click on "Next: Select Book" button
    Then I should see a message that the user has no books to exchange
