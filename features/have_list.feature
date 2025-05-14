Feature: Add book to have list

  Scenario: Registered user adds a book to their have list
    Given Exists a user "anna" with password "testpass"
    And I login as user "anna" with password "testpass"
    And Exists a book with ISBN "1234567890" and title "Test Book" and author "Test Author"
    When I visit the book entry page for ISBN "1234567890" 
    And I click the "I have it!" button
    # Adaptem aquest pas per ser més flexible amb el text mostrat
    Then Server responds with page containing "added"
    And The have list contains the book with ISBN "1234567890"

  Scenario: Anonymous user tries to add a book to have list
    Given Exists a book with ISBN "1234567890" and title "Test Book" and author "Test Author"
    And I'm not logged in
    When I visit the book entry page for ISBN "1234567890"
    And I click the "I have it!" button
    Then I'm redirected to the login form
