# Lesson 6: Working with Models

Models are a fundamental part of Ruby on Rails applications. In this lesson, we will learn how to create database models using Rails' powerful ORM (Object-Relational Mapping), ActiveRecord. We will explore migrations, associations, and how to perform basic database operations.

## Creating a Model

To create a model in Rails, we use the `generate` command with the `model` keyword. Let's say we want to create a `User` model to represent users in our application. Open your terminal and execute the following command:

```bash
rails generate model User
```

This command will generate a new file under `db/migrate` that defines a migration for creating the `users` table. It will also generate a model file under `app/models` for the `User` class.

## Migrations and Schema Management

Migrations are scripts that help manage database schema changes in a Rails application. They allow you to create and modify tables, columns, indexes, and more. Once you've created a migration file for a model, you can apply the changes to the database using the `db:migrate` command:

```bash
rails db:migrate
```

Rails keeps track of executed migrations in a table called `schema_migrations`, ensuring that each migration is only applied once.

## Associations between Models

In Rails, you can establish associations between models to define relationships and navigate between them. For example, a `User` model might have a one-to-many association with a `Post` model. To define this association, you would add the necessary code to the model files using ActiveRecord macros like `has_many` and `belongs_to`.

Associations allow you to perform operations like retrieving associated records, creating new records, and updating relationships between models.

## Performing Basic Database Operations

Once you have models and associations in place, you can perform basic database operations using ActiveRecord methods. ActiveRecord provides a set of query methods like `create`, `find`, `where`, and `update` that allow you to interact with the database without writing raw SQL queries.

These methods provide an intuitive and expressive way to perform CRUD (Create, Read, Update, Delete) operations on your models.

## Conclusion

In this lesson, we learned how to work with models in Ruby on Rails. We explored how to generate a model, manage database schema changes using migrations, establish associations between models, and perform basic database operations using ActiveRecord.

In the next lesson, we will focus on implementing views in Rails. You will learn about Rails' view templating system, how to work with layouts and partials, and how to utilize view helpers to enhance the user interface.