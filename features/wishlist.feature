Feature: Add book to wishlist

  Scenario: Registered user adds a book to their wishlist
    Given Exists a user "anna" with password "testpass"
    And I login as user "anna" with password "testpass"
    And Exists a book with ISBN "1234567890" and title "Test Book" and author "Test Author"
    When I visit the book entry page for ISBN "1234567890" 
    And I click the "Want!" button
    Then Server responds with page containing "added"
    And The wishlist contains the book with ISBN "1234567890"

  Scenario: Anonymous user tries to add a book to wishlist
    Given Exists a book with ISBN "1234567890" and title "Test Book" and author "Test Author"
    And I'm not logged in
    When I visit the book entry page for ISBN "1234567890"
    And I click the "Want!" button
    Then I'm redirected to the login form
