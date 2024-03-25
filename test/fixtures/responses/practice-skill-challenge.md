### Practice Skill Challenge

#### Question 1
[multipleChoice]
[question]Why are database indexes crucial for optimizing the performance of database queries?[/question]

- [ ] Decrease query speed
- [ ] Faster data modification operations
- [x] Improved data retrieval speed
- [ ] Increased storage space

[/multipleChoice]


#### Question 2
[fillBlank]
[question]What is a database attribute that can be added to a database column that allows for faster retrieval of records?[/question]
[answer]index[/answer]
[/fillBlank]


#### Question 3
[multipleChoice]
[question]What is the primary benefit of using database transactions in Rails?[/question]

- [ ] Ensuring data is stored without validation
- [x] Maintaining data integrity and consistency
- [ ] Increasing database performance
- [ ] Interfering with concurrent database operations

[/multipleChoice]


#### Question 4
[trueFalse]
[question]Is it possible to over-index a database?[/question]

- [x] True
- [ ] False

[/trueFalse]

#### Question 5
[codeEditor]
[question]Write a program that uses the appropriate syntax for creating a database transaction to update two tables in a Rails application.[/question]

```ruby
ActiveRecord::Base.transaction do
  account.debit!(amount)
  recipient_account.credit!(amount)
end
```

[mustContain]ActiveRecord::Base.transaction[/mustContain]

[/codeEditor]