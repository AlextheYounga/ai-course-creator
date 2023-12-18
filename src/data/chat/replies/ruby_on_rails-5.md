# Lesson 5: Creating a Rails Application

Now that you have a good understanding of the MVC architecture, it's time to create your first Ruby on Rails application. In this lesson, we will guide you through generating a new Rails project and help you explore its directory structure.

## Generating a New Rails Application

To create a new Rails application, open your terminal and execute the following command:

```bash
rails new myapp
```

Here, `myapp` is the name you choose for your application. Rails will generate a new project folder with the specified name and set up the necessary files and configurations.

## Exploring the Directory Structure

When you generate a new Rails application, it creates a predetermined directory structure that follows Rails conventions. Let's take a look at the important directories and files:

- **app**: This folder contains the core of your application.
  - **controllers**: Controllers that handle user requests and facilitate data flow.
  - **models**: Models that represent the data and handle interactions with the database.
  - **views**: Views that display information to the users.
  - **assets**: Assets like stylesheets, JavaScript files, and images.

- **config**: Contains configurations for your application.
  - **database.yml**: Configuration file for the database connection.
  - **routes.rb**: Defines the routes that map URLs to controller actions.

- **db**: Contains database-related files, such as migrations and the schema file.

- **Gemfile**: Specifies the gems (Ruby libraries) that your application depends on.

- **public**: Contains static files accessible directly by the users, such as error pages.

- **test**: Folder for test files, including unit tests and functional tests.

- **README.md**: A markdown file that typically provides instructions and information about the project.

This is just a high-level overview of the directory structure. As you progress with Rails development, you'll become more familiar with each directory and its purpose.

## Conclusion

In this lesson, you generated a new Rails application using the `rails new` command and explored the directory structure of a Rails project. Understanding the organization of files and folders is crucial for efficient development and maintaining a well-structured application.

In the next lesson, we will dive into working with models and learn how to create database models using Rails' powerful ORM, ActiveRecord.