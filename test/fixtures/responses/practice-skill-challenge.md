### Practice Skill Challenge

#### Question 1
Why are database indexes crucial for optimizing the performance of database queries?

- A) Decrease query speed
- B) Faster data modification operations
- C) Improved data retrieval speed
- D) Increased storage space

<div id="answerable-multiple-choice">
    <p id="question">Why are database indexes crucial for optimizing the performance of database queries?</p>
    <select id="choices">
        <option>Decrease query speed</option>
        <option>Faster data modification operations</option>
        <option id="correct-answer">Improved data retrieval speed</option>
        <option>Increased storage space</option>
    </select>
</div>

#### Question 2
How does a database index resemble the concept of a library index?

<div id="answerable-fill-blank">
    <p id="question">How does a database index resemble the concept of a library index?</p>
    <p id="correct-answer">In a similar way to how a library index helps find books efficiently, a database index helps retrieve data quickly from large datasets.</p>
</div>

#### Question 3
What is the primary benefit of using database transactions in Rails?

- A) Ensuring data is stored without validation
- B) Maintaining data integrity and consistency
- C) Increasing database performance
- D) Interfering with concurrent database operations

<div id="answerable-multiple-choice">
    <p id="question">What is the purpose of using database transactions in Rails?</p>
    <select id="choices">
        <option>Ensuring data is stored without validation</option>
        <option id="correct-answer">Maintaining data integrity and consistency</option>
        <option>Increasing database performance</option>
        <option>Interfering with concurrent database operations</option>
    </select>
</div>

#### Question 4
Explain the potential downside of over-indexing in a database.

<div id="answerable-fill-blank">
    <p id="question">Explain the potential downside of over-indexing in a database.</p>
    <p id="correct-answer">Over-indexing can lead to decreased performance, much like cluttering a book with an excessive number of bookmarks, making it harder to navigate.</p>
</div>

#### Question 5
Write a program that uses a database transaction to update two tables in a Rails application.

<div id="answerable-code-editor">
    <p id="question">Write a program that uses a database transaction to update two tables in a Rails application.</p>
    <p id="correct-answer">ActiveRecord::Base.transaction do
  account.debit!(amount)
  recipient_account.credit!(amount)
end</p>
</div>